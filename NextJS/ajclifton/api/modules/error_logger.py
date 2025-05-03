import os
import sqlite3
import traceback
import yaml
import uuid
from enum import Enum
import time


class ErrorLogger:

    def __new__(cls):
        if not hasattr(cls, "instance"):
            cls.instance = super(ErrorLogger, cls).__new__(cls)
        return cls.instance
    
    def __init__(self):
        with open("config.yaml", "r") as stream:
            self.config = yaml.safe_load(stream)["error_logging"]

        self.con = sqlite3.connect(self.config["database_path"])
        with self.con:
            self.con.execute("""
                CREATE TABLE IF NOT EXISTS errors (
                    id TEXT,
                    time TEXT,
                    severity TEXT,
                    source TEXT,
                    error TEXT,
                    stack_trace TEXT,
                    user_id TEXT,
                    additional_data TEXT,
                    PRIMARY KEY (id));
                """)
            
    def log_error(self, severity, source, error, stack_trace, user_id=None, additional_data=None):
        error_id = str(uuid.uuid4())
        try: 
            with self.con:
                self.con.execute("""INSERT INTO errors VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                                (error_id, int(time.time()), severity.value, source, error, stack_trace, user_id, additional_data))
        except sqlite3.IntegrityError:
            self.log_error(severity, source, error, stack_trace, user_id=user_id, additional_data=additional_data)

    def get_errors(self):
        try:
            with self.con:
                result = self.con.execute("""SELECT * FROM errors""")
                return result.fetchall()
        except Exception as e:
            self.log_error(ErrorSeverity.ERROR, 
                           os.path.basename(__file__),
                           type(e).__name__, 
                           traceback.format_exc())


class ErrorSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"