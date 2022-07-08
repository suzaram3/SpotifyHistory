from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import func


class SessionHandler:
    __instance = None

    def __init__(self, session, model):
        """Virtually private constructor."""

        SessionHandler.__instance = self
        self.model = model
        self.session = session

    @staticmethod
    def create(session, model):
        """Singleton create instance of session using session and table model"""
        SessionHandler.__instance = SessionHandler(session, model)
        return SessionHandler.__instance

    def insert_many(self, record_list):
        """Bulk insert into model"""
        statements = [
            pg_insert(self.model).values(record_dict).on_conflict_do_nothing()
            for record_dict in record_list
        ]
        return [self.session.execute(statement) for statement in statements]

    def update(self, query_dict, update_dict):
        """Bulk update for model"""
        return (
            self.session.query(self.model).filter_by(**query_dict).update(update_dict)
        )

    def get_total_count(self):
        """Return total count in model"""
        return self.session.query(self.model).count()

    def delete(self, query_dict):
        """Delete from model"""
        return self.session.query(self.model).filter_by(**query_dict).delete()

    def get_top_songs(self):
        """Return top 100 songs in SongStreamed model"""
        return (
            self.session.query(func.count(self.model.song_id), self.model.song_id)
            .group_by(self.model.song_id)
            .order_by(func.count(self.model.song_id).desc())
            .limit(100)
            .all()
        )
