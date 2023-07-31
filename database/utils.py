import datetime
from typing import Dict, Optional, Tuple

from sqlalchemy import cast, create_engine, func, Date
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker

from database.models import (
    Base,
    Album,
    AlbumArtist,
    Artist,
    Song,
    SongArtist,
    SongStreamed,
    StreamHistory,
)


class SessionManager:
    def __init__(self, engine):
        self.Session = sessionmaker(bind=engine)

    def __enter__(self):
        self.session = self.Session()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()
        self.session.close()


def create_database(database_url) -> None:
    engine = create_engine(database_url)
    Base.metadata.create_all(engine)


def get_song_id_count(engine, target_song_id: str) -> int:
    with SessionManager(engine) as session:
        return (
            session.query(func.count(SongStreamed.song_id))
            .filter(SongStreamed.song_id == target_song_id)
            .scalar()
        )


def get_distinct_song_ids(engine) -> list[SongStreamed.song_id]:
    with SessionManager(engine) as session:
        return [
            song_id[0]
            for song_id in session.query(StreamHistory.song_id).distinct().all()
        ]


def insert_rows_with_conflict_handling(
    engine, data_lists
) -> Tuple[Optional[Dict[str, int]], Optional[str]]:
    """
    Bulk insert data into the database tables while ignoring duplicates.

    This function performs bulk inserts for multiple data lists into the corresponding database tables. It uses the "DO NOTHING" approach to ignore duplicates during the insert operation, ensuring that existing records are not overwritten.

    Parameters:
        engine (sqlalchemy.engine.Engine): The SQLAlchemy engine used to connect to the database.
        data_lists (list): A list of data lists for each database table. Each data list should contain data objects of the corresponding table's model.

    Returns:
        tuple or None: A tuple with two elements: the result of the operation (None for success) and an error message in case of any exceptions (or None if no error occurred).

    Example:
        # Assuming 'engine' and 'data_lists' are defined appropriately
        result, error_message = bulk_insert_ignore_duplicates(engine, data_lists)
        if result is None:
            print("Bulk insert successful!")
        else:
            print(f"Error occurred: {error_message}")

    Note:
        - The data_lists should contain data objects with attributes matching the model fields.
        - The primary key constraint names for each model should be provided in the model_to_constraint dictionary within the function.
        - The function uses a SessionManager to handle the database session.
        - The data classes in the data_lists should have a custom 'as_dict()' method that returns a dictionary representation of the data object.

    """
    model_to_constraint = {
        Artist: "artists_pkey",
        Album: "albums_pkey",
        AlbumArtist: "album_artists_pkey",
        Song: "songs_pkey",
        SongArtist: "song_artists_pkey",
        SongStreamed: "streams_pkey",
    }

    row_counts = {}

    with SessionManager(engine) as session:
        for model, data_list in zip(model_to_constraint, data_lists):
            insert_stmt = insert(model).values([item.as_dict() for item in data_list])

            primary_key = model_to_constraint[model]

            on_conflict_stmt = insert_stmt.on_conflict_do_nothing(
                constraint=primary_key
            )

            try:
                result = session.execute(on_conflict_stmt)
                session.commit()

                row_counts[model.__name__] = result.rowcount

            except IntegrityError as e:
                session.rollback()
                return None, str(e)

            except Exception as e:
                session.rollback()
                return None, str(e)

    return row_counts, None


def summary_queries(engine) -> dict:
    year = datetime.datetime.utcnow().year
    year_begin = datetime.datetime(year, 1, 1)
    year_end = datetime.datetime(year, 12, 31)

    with SessionManager(engine) as session:
        return {
            "table_counts": table_counts(engine),
            "stream_count_per_day": (
                session.query(
                    cast(SongStreamed.played_at, Date),
                    func.count(cast(SongStreamed.played_at, Date)),
                )
                .group_by(cast(SongStreamed.played_at, Date))
                .order_by(func.count(cast(SongStreamed.played_at, Date)))
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
            "top_artist_year": (
                session.query(
                    func.count(Artist.id).label("artist_count"),
                    Artist.name.label("artist_name"),
                )
                .join(SongArtist, SongArtist.artist_id == Artist.id, isouter=True)
                .join(SongStreamed, SongStreamed.song_id == SongArtist.song_id, isouter=True)
                .filter(cast(SongStreamed.played_at, Date) >= "2022-12-31")
                .group_by(Artist.id, Artist.name)
                .order_by(func.count(Artist.id).desc())
                .limit(1)
                .first()
            ),
            "top_song_today": (
                session.query(
                    func.count(SongStreamed.song_id),
                    Song.name,
                    Artist.name,
                )
                .join(SongArtist, SongArtist.song_id == SongStreamed.song_id)
                .join(Song, Song.id == SongStreamed.song_id)
                .join(Artist, Artist.id == SongArtist.artist_id)
                .filter(
                    cast(SongStreamed.played_at, Date)
                    == datetime.datetime.utcnow().date()
                )
                .group_by(SongStreamed.song_id, Song.name, Artist.name)
                .order_by(func.count(SongStreamed.song_id).desc())
                .first()
            ),
            "top_song_year": (
                session.query(
                    func.count(SongStreamed.song_id),
                    Song.name,
                    Artist.name,
                )
                .join(Song, Song.id == SongStreamed.song_id)
                .join(SongArtist, SongArtist.song_id == SongStreamed.song_id)
                .join(Artist, Artist.id == SongArtist.artist_id)
                .filter(cast(SongStreamed.played_at, Date) >= year_begin)
                .group_by(SongStreamed.song_id, Song.name, Artist.name)
                .order_by(func.count(SongStreamed.song_id).desc())
                .first()
            ),
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


def table_counts(engine) -> dict:
    models = [Album, AlbumArtist, Artist, Song, SongArtist, SongStreamed]
    with SessionManager(engine) as session:
        return [
            {"model": model, "count": session.query(model).count()} for model in models
        ]
