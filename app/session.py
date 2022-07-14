from contextlib import contextmanager
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy import func
from db import DB
from config import DevelopmentConfig, ProductionConfig
from models import Artist, Album, Song, SongStreamed


class SessionHandler:
    def get_all_records(self, session: object, model: object) -> list:
        return list(session.query(model).all())

    def get_table_count(self, session: object, model: object) -> int:
        return {"model": model, "count": session.query(model).count()}

    def get_top_artists(self, session):
        return (
            session.query(Artist.name, func.count(Artist.id))
            .join(Song, Song.artist_id == Artist.id, isouter=True)
            .join(SongStreamed, SongStreamed.song_id == Song.id, isouter=True)
            .group_by(Artist.id, Artist.name)
            .order_by(func.count(Artist.id).desc())
            .all()
        )

    def get_top_song_ids(self, session, max_records=100):
        return (
            session.query(SongStreamed.song_id)
            .group_by(SongStreamed.song_id)
            .order_by(func.count(SongStreamed.song_id).desc())
            .limit(max_records)
            .all()
        )

    def get_top_song_names(self, session):
        return (
            session.query(Song.name, func.count(SongStreamed.song_id))
            .join(Song, Song.id == SongStreamed.song_id)
            .group_by(SongStreamed.song_id, Song.name)
            .order_by(func.count(SongStreamed.song_id).desc())
            .all()
        )

    def insert_many(self, session: object, payload: dict) -> None:
        """Bulk insert into model"""
        statements = [
            pg_insert(payload["model"]).values(record).on_conflict_do_nothing()
            for record in payload["records"]
        ]
        [session.execute(statement) for statement in statements]
        return self.get_table_count(session, payload["model"])

    @contextmanager
    def session_scope(self, engine) -> None:
        Session = sessionmaker(bind=engine)
        session = Session()
        try:
            yield session
            session.commit()
        except:
            session.rollback()
            raise
        finally:
            session.close()
