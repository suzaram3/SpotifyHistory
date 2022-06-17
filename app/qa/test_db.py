import configparser, sqlalchemy

config = configparser.ConfigParser()
config.read(
    "/Users/msuzara/Library/Mobile Documents/com~apple~CloudDocs/cloud_workspace/python/SpotifyHistory/db.conf"
)


class DB:
    """Singleton DB class to connect to Postgres DB and create engine"""

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
        return sqlalchemy.create_engine(config["qa"]["db_uri"])

    def connect(self):
        return self.engine.connect()
