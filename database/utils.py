import datetime
import random
from typing import Dict, List, Optional, Tuple

from sqlalchemy import cast, create_engine, Date, distinct, extract, Float, func, text
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


def get_all_song_ids(engine) -> list:
    """
    Retrieve a list of all song IDs from the database.

    Returns:
    A list of all song IDs available in the database.
    """
    with SessionManager(engine) as session:
        return [id[0] for id in session.query(Song.id).all()]


def get_all_songs_streamed(engine) -> list[object]:
    """
    Query all song streaming records.

    Returns:
    A list of tuples representing song streaming records. Each tuple contains the song ID and the timestamp of when it was streamed.

    Note:
    - The records are ordered by the timestamp of when the songs were streamed.
    """
    with SessionManager(engine) as session:
        return [
            (i.song_id, i.played_at)
            for i in session.query(SongStreamed).order_by(SongStreamed.played_at).all()
        ]

def get_artist_ids_without_genres(engine) -> list:
    with SessionManager(engine) as session:
        artist_ids = [id[0] for id in session.query(Artist.id).all()]
        genre_artist_ids = [id[0] for id in session.query(ArtistGenre.artist_id).all()]

    return list(set(artist_ids).difference(set(genre_artist_ids)))

# def get_artist_ids_without_genres(engine) -> list[Artist.id]:

#     with SessionManager(engine) as session:
#         subquery = session.query(ArtistGenre.artist_id).subquery()
#         query = session.query(Artist.id).filter(~Artist.id.in_(subquery))

#         results = query.all()

#     return [result[0] for result in results]


def get_distinct_artists(engine) -> list:
    with SessionManager(engine) as session:
        return [i[0] for i in session.query(distinct(Artist.id)).all()]


def get_distinct_songs(engine) -> list:
    with SessionManager(engine) as session:
        return [i[0] for i in session.query(distinct(SongStreamed.song_id)).all()]


def get_distinct_song_ids(engine) -> list[SongStreamed.song_id]:
    with SessionManager(engine) as session:
        return [
            song_id[0]
            for song_id in session.query(StreamHistory.song_id).distinct().all()
        ]


def get_percentage_difference(engine):
    with SessionManager(engine) as session:
        # Step 1: Get the total number of songs listened to up to the current date for the current year
        # Step 1: Get the total number of songs listened to up to the current date for the current year
        songs_this_year = (
            session.query(func.count(func.distinct(SongStreamed.song_id)))
            .filter(
                SongStreamed.played_at >= func.date_trunc("year", func.current_date())
            )
            .filter(SongStreamed.played_at <= func.current_date())
            .scalar()
        )

        # Step 2: Get the total number of songs listened to up to the same date of the previous year
        songs_last_year = (
            session.query(func.count(func.distinct(SongStreamed.song_id)))
            .filter(
                SongStreamed.played_at
                >= func.date_trunc(
                    "year", func.current_date() - text("interval '1 year'")
                )
            )
            .filter(
                SongStreamed.played_at
                <= func.current_date() - text("interval '1 year'")
            )
            .scalar()
        )

        # Step 3: Calculate the percentage difference
        percentage_difference = (
            (float(songs_this_year) - float(songs_last_year)) / float(songs_last_year)
        ) * 100.0

    return round(percentage_difference)


def get_random_songs(engine, num_songs: int) -> dict:
    """
    Retrieve a dictionary containing today's date and a list of randomly selected song IDs.

    Returns:
    A dictionary with the following keys:
    - "today": The formatted date representing today in the format "YYYY-MM-DD".
    - "song_ids": A list of 100 randomly selected song IDs.

    Note:
    - The song IDs are randomly selected from all available songs in the database.
    """
    today = datetime.datetime.today().date()
    formatted_date = today.strftime("%Y-%m-%d")
    with SessionManager(engine) as session:
        all_songs = [(song[0]) for song in session.query(Song.id).all()]
        return {
            "today": formatted_date,
            "song_ids": random.sample(all_songs, num_songs),
        }


def get_songs_by_date(engine, query_date: datetime) -> list[tuple]:
    """
    Retrieve a list of songs streamed on a specific date.

    Args:
    - query_date (datetime): The date to query for streamed songs.

    Returns:
    A list of tuples containing the song ID and the timestamp of each song streamed on the specified date.
    The list is ordered by the timestamp of the song.

    Example:
    songs_by_date(datetime.datetime(2023, 6, 20))  # Retrieves songs streamed on June 20, 2023.
    """
    with SessionManager(engine) as session:
        return [
            (song[0], song[1])
            for song in session.query(SongStreamed.song_id, SongStreamed.played_at)
            .filter(cast(SongStreamed.played_at, Date) == query_date)
            .order_by(SongStreamed.played_at)
            .all()
        ]


def get_song_id_count(engine, target_song_id: str) -> int:
    with SessionManager(engine) as session:
        return (
            session.query(func.count(SongStreamed.song_id))
            .filter(SongStreamed.song_id == target_song_id)
            .scalar()
        )


def get_stream_counts_by_day(engine, week_dates: list) -> list[int]:
    with SessionManager(engine) as session:
        stream_counts = []
        for date in week_dates:
            count = (
                session.query(func.count(SongStreamed.song_id))
                .filter(func.date(SongStreamed.played_at) == date.date())
                .scalar()
            )
            stream_counts.append(count)
        return stream_counts


def get_table_counts(engine) -> dict:
    """
    Retrieve the counts of records in various tables.

    Returns:
    A dictionary containing the counts of records in each table.

    Example:
    table_counts()  # Retrieves the counts of records in various tables.
    """
    with SessionManager(engine) as session:
        return [
            {"model": model, "count": session.query(model).count()} for model in models
        ]


def get_top_songs_and_artists(engine) -> dict:
    """
    Retrieve the top song list and top artist list based on the number of times they have been streamed.

    Returns:
        A dictionary with the following keys:
        - "top_song_list": A list of tuples containing the name of the song and the number of times it has been streamed,
                           sorted in descending order of the stream count.
        - "top_artist_list": A list of tuples containing the name of the artist and the number of times their songs
                             have been streamed, sorted in descending order of the stream count.
    """
    with SessionManager(engine) as session:
        return {
            "top_song_list": session.query(Song.name, func.count(SongStreamed.song_id))
            .join(
                SongStreamed,
                Song.id == SongStreamed.song_id,
            )
            .group_by(SongStreamed.song_id, Song.name)
            .order_by(func.count(SongStreamed.song_id).desc())
            .all(),
            "top_artist_list": session.query(Artist.name, func.count(Artist.id))
            .join(
                SongArtist,
                Artist.id == SongArtist.artist_id,
                isouter=True,
            )
            .join(
                SongStreamed,
                SongStreamed.song_id == SongArtist.song_id,
                isouter=True,
            )
            .group_by(Artist.id, Artist.name)
            .order_by(func.count(Artist.id).desc())
            .all(),
        }


def get_top_songs_by_year(engine, year: int) -> list[Song.id]:
    with SessionManager(engine) as session:
        subquery = (
            session.query(
                SongStreamed.song_id,
                func.count().label("count_per_year"),
                func.row_number()
                .over(partition_by=SongStreamed.song_id, order_by=func.count().desc())
                .label("rank"),
            )
            .filter(extract("year", SongStreamed.played_at) == year)
            .group_by(SongStreamed.song_id)
            .subquery()
        )

    top_songs_of_year = (
        session.query(subquery.c.song_id)
        .filter(subquery.c.rank <= 50)
        .order_by(subquery.c.count_per_year.desc(), subquery.c.song_id)
        .distinct(subquery.c.song_id, subquery.c.count_per_year)
        .limit(50)
        .all()
    )

    return [song_id[0] for song_id in top_songs_of_year]


def get_weekly_summary(engine, week: dict) -> dict:
    with SessionManager(engine) as session:
        for day in week:
            day["count"] = (
                session.query(func.count(SongStreamed.song_id))
                .filter(cast(SongStreamed.played_at, Date) == day["week_day"])
                .all()[0][0]
            )
        return week


def get_yesterday_top_ten(engine) -> dict:
    yesterday = datetime.datetime.utcnow().date() - datetime.timedelta(days=1)
    with SessionManager(engine) as session:
        top_ten_songs = (
            session.query(
                SongStreamed.song_id,
                func.count(SongStreamed.song_id).label("play_count"),
            )
            .filter(cast(SongStreamed.played_at, Date) == yesterday)
            .group_by(SongStreamed.song_id)
            .having(func.count(SongStreamed.song_id) > 1)
            .order_by(func.count(SongStreamed.song_id).desc())
            .limit(10)
            .all()
        )

    return {
        "date": yesterday,
        "desc": f"Top 10 from {yesterday}",
        "song_ids": [song[0] for song in top_ten_songs],
    }


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


def monthly_summary(engine, date: datetime) -> list[dict]:
    """
    Get the daily summary of song streams for a specific month.

    Args:
        date: A datetime object representing the month and year for which to retrieve the summary.

    Returns:
        A list of dictionaries, where each dictionary represents a day in the specified month and contains the following keys:
        - "day": The day of the month in two-digit format (e.g., "01", "02", ..., "31").
        - "count": The number of song streams that occurred on that day.

    Note:
    - The date parameter should include the month and year information, while the day information will be ignored.
    - The summary includes only the days within the specified month.
    """
    with SessionManager(engine) as session:
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
                .join(
                    SongStreamed,
                    SongStreamed.song_id == SongArtist.song_id,
                    isouter=True,
                )
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
            "percentage_from_last_year": get_percentage_difference(engine),
        }


def table_counts(engine) -> dict:
    models = [Album, AlbumArtist, Artist, Song, SongArtist, SongStreamed]
    with SessionManager(engine) as session:
        return [
            {"model": model, "count": session.query(model).count()} for model in models
        ]


def top_streamed_song_ids(engine) -> list:
    """
    Get a playlist of the most streamed songs.

    Returns:
    A list of song names representing the most streamed songs.

    Note:
    - The playlist is based on the songs that have been streamed the most.
    - The function returns a maximum of 100 songs in the playlist.
    """
    with SessionManager(engine) as session:
        return [
            song[0]
            for song in session.query(SongStreamed.song_id)
            .group_by(SongStreamed.song_id)
            .order_by(func.count(SongStreamed.song_id).desc())
            .limit(100)
            .all()
        ]


def update_song_length(engine, id: str, length: int) -> dict:
    with SessionManager(engine) as session:
        (session.query(Song).filter(Song.id == id).update({Song.length: length}))
