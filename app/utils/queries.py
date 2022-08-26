import datetime
from contextlib import contextmanager
from datetime import date
from sqlalchemy import cast, create_engine, distinct, Date, func
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.dialects import postgresql
from SpotifyHistory.config import Config
from SpotifyHistory.models.models import Album, Artist, Song, SongStreamed


c = Config()
engine = create_engine(c.config["prod"]["db_uri"])
models = [Album, Artist, Song, SongStreamed]


@contextmanager
def session_scope():
    Session = sessionmaker(engine, expire_on_commit=False)
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


def load_tables(record_dicts: list) -> None:
    with session_scope() as session:
        statements = [
            pg_insert(chunk["model"]).values(record).on_conflict_do_nothing()
            for chunk in record_dicts
            for record in chunk["records"]
        ]
        [session.execute(statement) for statement in statements]


def monthly_summary(date: datetime) -> list[dict]:
    with session_scope() as session:
        return [
            {"day": day[0].strftime("%d"), "count": day[1]}
            for day in session.query(
                cast(SongStreamed.played_at, Date),
                func.count(cast(SongStreamed.played_at, Date)),
            )
            .filter(
                cast(SongStreamed.played_at, Date).between(date.replace(day=1), date)
            )
            .group_by(cast(SongStreamed.played_at, Date))
            .all()
        ]


def playlist() -> list:
    with session_scope() as session:
        return [
            song[0]
            for song in session.query(SongStreamed.song_id)
            .group_by(SongStreamed.song_id)
            .order_by(func.count(SongStreamed.song_id).desc())
            .limit(100)
            .all()
        ]


def query_all_song_streamed() -> list[object]:
    with session_scope() as session:
        return [
            (i.song_id, i.played_at)
            for i in session.query(SongStreamed).order_by(SongStreamed.played_at).all()
        ]


def song_ids() -> list:
    with session_scope() as session:
        return [id[0] for id in session.query(Song.id).all()]


def songs_by_date(query_date: datetime) -> list[tuple]:
    with session_scope() as session:
        return [
            (song[0], song[1])
            for song in session.query(SongStreamed.song_id, SongStreamed.played_at)
            .filter(cast(SongStreamed.played_at, Date) == query_date)
            .order_by(SongStreamed.played_at)
            .all()
        ]


def summary() -> dict:
    year = int(datetime.datetime.utcnow().strftime("%Y"))
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
                .filter(
                    cast(SongStreamed.played_at, Date)
                    == datetime.datetime.utcnow().date()
                )
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
            .filter(
                cast(SongStreamed.played_at, Date) == datetime.datetime.utcnow().date()
            )
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


def update_song_length(id: str, length: int) -> dict:
    with session_scope() as session:
        (session.query(Song).filter(Song.id == id).update({Song.length: length}))


def weekly_summary(week: dict) -> dict:
    with session_scope() as session:
        for day in week:
            day["count"] = (
                session.query(func.count(SongStreamed.song_id))
                .filter(cast(SongStreamed.played_at, Date) == day["week_day"])
                .all()[0][0]
            )
        return week


def yesterday_top_ten() -> dict:
    yesterday = datetime.datetime.utcnow().date() - datetime.timedelta(days=1)
    with session_scope() as session:
        return {
            "date": yesterday,
            "desc": f"Top 10 from {yesterday}",
            "song_ids": [
                song[1]
                for song in session.query(
                    func.count(SongStreamed.song_id), SongStreamed.song_id
                )
                .filter(cast(SongStreamed.played_at, Date) == yesterday)
                .group_by(SongStreamed.song_id)
                .order_by(func.count(SongStreamed.song_id).desc())
                .having(func.count(SongStreamed.song_id) > 1)
                .limit(10)
                .all()
            ],
        }


def distinct_songs() -> list:
    with session_scope() as session:
        return [i[0] for i in session.query(distinct(SongStreamed.song_id)).all()]


def add_artists(data: dict) -> None:
    with session_scope() as session:
        statements = [
            pg_insert(data["model"])
            .values(
                id=chunk.id,
                name=chunk.name,
            )
            .on_conflict_do_nothing()
            for chunk in data["data"]
        ]
        [session.execute(statement) for statement in statements]


def add_albums(data: dict) -> None:
    with session_scope() as session:
        statements = [
            pg_insert(data["model"])
            .values(
                id=chunk.id,
                name=chunk.name,
                release_year=chunk.release_year,
                artist_id=chunk.artist_id,
            )
            .on_conflict_do_nothing()
            for chunk in data["data"]
        ]
        [session.execute(statement) for statement in statements]


def add_songs(data: dict) -> None:
    with session_scope() as session:
        statements = [
            pg_insert(data["model"])
            .values(
                id=chunk.id,
                name=chunk.name,
                album_id=chunk.album_id,
                artist_id=chunk.artist_id,
                spotify_url=chunk.spotify_url,
                length=chunk.length,
            )
            .on_conflict_do_nothing()
            for chunk in data["data"]
        ]
        [session.execute(statement) for statement in statements]
