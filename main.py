import flask
import flask_login
import yaml
import playtime

config = yaml.safe_load(open("config.yaml"))
app = flask.Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = config["secret_key"]
login_manager = flask_login.LoginManager(app)


@app.route("/api/steamplaytime")
def fetch_steam_playtime():
    args = flask.request.args
    steam_playtime = playtime.Playtime()
    return steam_playtime.fetch_data(args.get("username", None), args.get("game_name", None), None, None)


