import configparser
import logging
import logging.config
import sqlalchemy

config = configparser.ConfigParser()
config.read(
    "/Users/msuzara/Library/Mobile Documents/com~apple~CloudDocs/cloud_workspace/python/SpotifyHistory/db.conf"
)
logging.config.fileConfig(
    "/Users/msuzara/Library/Mobile Documents/com~apple~CloudDocs/cloud_workspace/python/SpotifyHistory/logging.conf"
)
file_logger = logging.getLogger("file")
console_logger = logging.getLogger("console")


class DB:
    """Singleton DB class to connect to Postgres DB and create engine"""

    def __init__(self, instance_flag: str) -> None:
        """Virtually private constructor"""
        self.instance_flag = instance_flag
        self.engine = self.create_engine()

    def create_engine(self):
        try:
            return sqlalchemy.create_engine(config[self.instance_flag]["db_uri"])
        except Exception as error:
            file_logger.error(f"{error}")

    def connect(self):
        try:
            return self.engine.connect()
        except Exception as error:
            file_logger.error(f"{error}")
