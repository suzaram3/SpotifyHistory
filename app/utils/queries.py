import datetime
from contextlib import contextmanager
from datetime import date
from sqlalchemy import cast, Date, func, select
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects import postgresql
from SpotifyHistory.config import Config
from SpotifyHistory.models.models import Album, Artist, Song, SongStreamed

c = Config()
models = [Album, Artist, Song, SongStreamed]


@contextmanager
def session_scope():
    Session = sessionmaker(c.engine, expire_on_commit=False)
    session = Session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        Config.file_logger.error("rollback transaction")
        Config.file_logger.error(f"{e}")
        raise
    finally:
        session.expunge_all()
        session.close()


def cloud() -> dict:
    with session_scope() as session:
        return {
            "top_song_list": session.query(Song.name, func.count(SongStreamed.song_id))
            .join(
                Song,
                Song.id == SongStreamed.song_id,
            )
            .group_by(SongStreamed.song_id, Song.name)
            .order_by(func.count(SongStreamed.song_id).desc())
            .all(),
            "top_artist_list": session.query(Artist.name, func.count(Artist.id))
            .join(
                Song,
                Song.artist_id == Artist.id,
                isouter=True,
            )
            .join(
                SongStreamed,
                SongStreamed.song_id == Song.id,
                isouter=True,
            )
            .group_by(Artist.id, Artist.name)
            .order_by(func.count(Artist.id).desc())
            .all(),
        }


def song_ids() -> list:
    with session_scope() as session:
        return [id[0] for id in session.query(Song.id).all()]


def load_tables(record_dicts: list) -> None:
    with session_scope() as session:
        statements = [
            pg_insert(chunk["model"]).values(record).on_conflict_do_nothing()
            for chunk in record_dicts
            for record in chunk["records"]
        ]
        [session.execute(statement) for statement in statements]


def playlist() -> dict:
    with session_scope() as session:
        return {
            "top_songs": session.query(SongStreamed.song_id)
            .group_by(SongStreamed.song_id)
            .order_by(func.count(SongStreamed.song_id).desc())
            .limit(300)
            .all()
        }


def summary(year: datetime = int(datetime.datetime.today().strftime("%Y"))) -> dict:
    year_begin = datetime.datetime(year, 1, 1)
    year_end = datetime.datetime(year, 12, 31)
    with session_scope() as session:
        return {
            "table_counts": table_counts(),
            "stream_count_per_day": (
                session.query(
                    func.count(cast(SongStreamed.played_at, Date)),
                )
                .group_by(cast(SongStreamed.played_at, Date))
                .all()
            ),
            "freq_by_day": (
                session.query(
                    cast(SongStreamed.played_at, Date),
                    func.count(cast(SongStreamed.played_at, Date)),
                )
                .group_by(cast(SongStreamed.played_at, Date))
                .order_by(cast(SongStreamed.played_at, Date).desc())
                .all()
            ),
            "play_today": (
                session.query(func.count(SongStreamed.song_id))
                .filter(cast(SongStreamed.played_at, Date) == date.today())
                .first()
            ),
            "top_song_today": (
                session.query(
                    func.count(SongStreamed.song_id),
                    Song.name,
                    Artist.name,
                )
            )
            .join(
                Song,
                Song.id == SongStreamed.song_id,
            )
            .join(
                Artist,
                Artist.id == Song.artist_id,
            )
            .filter(cast(SongStreamed.played_at, Date) == date.today())
            .group_by(
                SongStreamed.song_id,
                Song.name,
                Artist.name,
            )
            .order_by(func.count(SongStreamed.song_id).desc())
            .first(),
            "year_count": (
                session.query(SongStreamed)
                .filter(SongStreamed.played_at.between(year_begin, year_end))
                .count()
            ),
            "days": (
                session.query(func.sum(Song.length))
                .join(SongStreamed, Song.id == SongStreamed.song_id, isouter=True)
                .first()
            ),
        }


def table_counts() -> dict:
    with session_scope() as session:
        return [
            {"model": model, "count": session.query(model).count()} for model in models
        ]


def update(id: str, length: int) -> dict:
    with session_scope() as session:
        (session.query(Song).filter(Song.id == id).update({Song.length: length}))
