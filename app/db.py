import configparser, sqlalchemy

config = configparser.ConfigParser()
config.read(
    "/Users/msuzara/Library/Mobile Documents/com~apple~CloudDocs/cloud_workspace/python/SpotifyHistory/db.conf"
)


class DB:
    """Singleton DB class to connect to Postgres DB and create engine"""

    def __init__(self, instance_flag: str) -> None:
        """Virtually private constructor"""
        self.instance_flag = instance_flag
        self.engine = self.create_engine()

    def create_engine(self):
        return sqlalchemy.create_engine(config[self.instance_flag]["db_uri"])

    def connect(self):
        return self.engine.connect()
