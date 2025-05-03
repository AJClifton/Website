import requests
import datetime
import sqlite3
import yaml
from modules.error_logger import ErrorLogger, ErrorSeverity
import traceback
import os
import json

class Playtime():

    error_severity = {
        sqlite3.IntegrityError: ErrorSeverity.INFO,
        ValueError: ErrorSeverity.WARNING,
        PermissionError: ErrorSeverity.CRITICAL,
        LookupError: ErrorSeverity.CRITICAL,
        KeyError: ErrorSeverity.ERROR,
    }


    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(Playtime, cls).__new__(cls)
        return cls.instance


    def __init__(self):
        self.config = yaml.safe_load(open("config.yaml"))["steam"]

        self.con = sqlite3.connect(self.config["database_path"])
        with self.con:
            self.con.execute("""
                CREATE TABLE IF NOT EXISTS data (
                    date TEXT,
                    username TEXT,
                    appid INTEGER,
                    total_time NUMERIC,
                    daily_time NUMERIC,
                    fortnight_time NUMERIC,
                    PRIMARY KEY (date, username, appid));
                """)
            self.con.execute("""
                CREATE TABLE IF NOT EXISTS games (
                    appid INTEGER PRIMARY KEY,
                    name TEXT,
                    formatted_name TEXT);
                """)

    def get_user_playtime(self, id):
        """Get the playtime data for the given user in a JSON format.
        
        :param id: Steam user id
        :raises ValueError: invalid ID
        :raises PermissionError: invalid key
        :raises LookupError: incorrect URL
        :raises KeyError: unexpected response format"""
        r = requests.get(f'https://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/?key={self.config["key"]}&steamid={id}&format=json')
        if r.status_code == 400:
            raise ValueError
        elif r.status_code == 403:
            raise PermissionError
        elif r.status_code == 404:
            raise LookupError
        return r.json()["response"]

    def get_last_total_time(self, username, appid):
        with self.con:
            result = self.con.execute("""SELECT total_time FROM data WHERE username = ? AND appid = ? ORDER BY date DESC LIMIT 1""", 
                                (username, appid))
        line = result.fetchone()
        return None if line is None else line[0]

    def days_collected_for_user(self, username):
        with self.con:
            result = self.con.execute("""SELECT count(DISTINCT date) FROM data WHERE username = ?""", (username,))
        return result.fetchone()[0]

    def insert_data(self, date, username, appid, playtime_total, playtime_daily, playtime_2weeks):
        with self.con:
            self.con.execute("""INSERT INTO data VALUES (?, ?, ?, ?, ?, ?)""",
                        (date, username, appid, playtime_total, playtime_daily, playtime_2weeks))         

    def fetch_game_by_appid(self, appid):
        with self.con:
            result = self.con.execute("""SELECT * fROM games WHERE appid = ?""", (appid,))
        return result.fetchone()

    # Games can apparently (deadlock) have no name for a while - app id also never changes making it resiliant to name changes.
    def add_game(self, appid, name=None):
        existing_entry = self.fetch_game_by_appid(appid)
        if existing_entry != None:
            if name is not None and existing_entry[1] == None: # existing_entry[1] is the game name.
                self.add_game_name(appid, name)
            return
        if name is None:
            with self.con:
                self.con.execute("""INSERT INTO games(appid) VALUES (?)""", (appid,))
        else:
            formatted_name = self.format_game_name(name)
            with self.con:
                self.con.execute("""INSERT INTO games VALUES (?,?,?)""", (appid, name, formatted_name))

    def add_game_name(self, appid, name):
        formatted_name = self.format_game_name(name)
        with self.con:
            self.con.execute("""UPDATE games SET name = ?, formatted_name = ? WHERE appid = ?""", (name, formatted_name, appid))
            
    def format_game_name(self, game_name):
        return "".join(ch for ch in game_name if ch.isalnum()).lower()

    def fetch_data(self, username, game_name, start_date, end_date):
        formatted_game_name = self.format_game_name(game_name)
        sql_request = """SELECT d.username, g.name, d.date, d.total_time, d.daily_time 
                        FROM data d INNER JOIN games g ON d.appid = g.appid 
                        WHERE d.username = ? AND g.formatted_name = ?"""
        with self.con:
            result = self.con.execute(sql_request, (username, formatted_game_name))
        formatted_result = {}
        for row in result.fetchall():
            if formatted_result.get(row[0], None) is None:
                formatted_result[row[0]] = {}
            if formatted_result[row[0]].get(row[1], None) is None:
                formatted_result[row[0]][row[1]] = {"date": [row[2]], 
                                                    "total_time": [row[3]], 
                                                    "daily_time": [row[4]]}
                continue
            formatted_result[row[0]][row[1]]["date"].append(row[2])
            formatted_result[row[0]][row[1]]["total_time"].append(row[3])
            formatted_result[row[0]][row[1]]["daily_time"].append(row[4])
        return formatted_result


    def update_playtimes(self):
        date = datetime.date.today().strftime("%Y/%m/%d")
        for user in self.config["users"]:
            try:
                playtime_data = self.get_user_playtime(user["id"])
                # If no games have been played, there is no 'games' value.
                if playtime_data == {} or playtime_data['total_count'] == 0:
                    continue
                for game in playtime_data['games']:
                    appid = game['appid']
                    game_name = None
                    # If the game name is missing, ignore the error and pass in None
                    try:
                        game_name = game['name'].replace("'", "")
                    except KeyError:
                        pass
                    self.add_game(appid, game_name)

                    last_total_time = self.get_last_total_time(user["username"], game_name)
                    playtime_forever = float(game["playtime_forever"])
                    playtime_2weeks = float(game["playtime_2weeks"])

                    if last_total_time is not None:
                        daily_hours = playtime_forever - last_total_time
                    elif playtime_forever == playtime_2weeks and self.days_collected_for_user(user["username"]) == 0:
                        daily_hours = playtime_2weeks
                    else:
                        daily_hours = 0

                    self.insert_data(date, user["username"], appid, playtime_forever, daily_hours, playtime_2weeks)
            except Exception as e:
                # If an error occurs in 'get_user_playtime', playtime_data would not be defined
                # Unsure whether this or assigning it to be None before calling the method is preferred
                additional_data = None
                try:
                    playtime_data
                except NameError:
                    pass
                else:
                    additional_data = "playtime_data="+str(playtime_data)
                ErrorLogger().log_error(self.error_severity.get(type(e), ErrorSeverity.CRITICAL), 
                                        os.path.basename(__file__),
                                        type(e).__name__, 
                                        traceback.format_exc(),
                                        additional_data=additional_data)
    
    def update_playtime_from_backup(self, username):
        with open(username + ".txt", "r") as file:
            for line in file.readlines():
                date = "/".join(line[:10].split("/")[::-1])
                corrected_line = self.replace_single_quotes_in_backup(line[10:])
                playtime_data = json.loads(corrected_line)['response']
                # If no games have been played, there is no 'games' value.
                if playtime_data == {} or playtime_data['total_count'] == 0:
                    continue
                for game in playtime_data['games']:
                    appid = game['appid']
                    game_name = None
                    # If the game name is missing, ignore the error and pass in None
                    try:
                        game_name = game['name'].replace("'", "")
                    except KeyError:
                        pass
                    self.add_game(appid, game_name)

                    last_total_time = self.get_last_total_time(username, appid)
                    playtime_forever = float(game["playtime_forever"])
                    playtime_2weeks = float(game["playtime_2weeks"])

                    if last_total_time is not None:
                        # TODO something about this isn't quite right. Have a look into it. daily said to be zero when it shouldn't be as first value.
                        daily_hours = playtime_forever - last_total_time
                    elif playtime_forever == playtime_2weeks and self.days_collected_for_user(username) == 0:
                        daily_hours = playtime_2weeks
                    else:
                        daily_hours = 0

                    self.insert_data(date, username, appid, playtime_forever, daily_hours, playtime_2weeks)


    # If a game has  a ' in its title, it will be surrounded by double quotes. 
    # It should not be replaced by " so a simple replace won't work here
    def replace_single_quotes_in_backup(self, json_string):
        json_list = list(json_string)
        inside_game_name = False
        for i in range(len(json_string)):
            if json_list[i] == '"':
                inside_game_name = not inside_game_name
            elif json_list[i] == "'" and not inside_game_name:
                json_list[i] = '"'
        return "".join(json_list)
    