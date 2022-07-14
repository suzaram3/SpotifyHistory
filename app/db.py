import sqlalchemy


class DB:
    """Singleton DB class to connect to Postgres DB and create engine"""

    def __init__(self, db_uri: str) -> None:
        """Virtually private constructor"""
        self.db_uri = db_uri
        self.engine = self.create_engine()

    def create_engine(self):
        return sqlalchemy.create_engine(self.db_uri)

    def connect(self):
        return self.engine.connect()
