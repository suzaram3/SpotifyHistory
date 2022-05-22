import configparser, logging, sqlalchemy
import logging.config

config = configparser.ConfigParser()
config.read(
    [
        "/Users/msuzara/Library/Mobile Documents/com~apple~CloudDocs/cloud_workspace/python/SpotifyHistory/db.conf",
        # "/Users/msuzara/Library/Mobile Documents/com~apple~CloudDocs/cloud_workspace/python/SpotifyHistory/logging.conf",
    ]
)
logger = logging.getLogger("logFile")
logger.info("Logger for db")


class DB:
    __instance = None

    def __init__(self) -> None:
        """Virtually private constructor"""

        if DB.__instance is not None:
            raise Exception("This class is a singleton, use DB.create()")
        else:
            DB.__instance = self
        self.engine = self.create_engine()

    @staticmethod
    def create():
        if DB.__instance is None:
            DB.__instance = DB()

        return DB.__instance

    def create_engine(self):
        return sqlalchemy.create_engine(config["postgresql"]["db_uri"])

    def connect(self):
        return self.engine.connect()
