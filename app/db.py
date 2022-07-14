import sqlalchemy


class DB:
    """Singleton DB class to connect to Postgres DB and create engine"""

    def __init__(self, config: object) -> None:
        """Virtually private constructor"""
        self.engine = self.create_engine(config)

    def create_engine(self, config: object):
        return sqlalchemy.create_engine(config['db_uri'])

    def connect(self):
        return self.engine.connect()
