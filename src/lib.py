import random
from typing import List, Optional, Tuple, Union
from datetime import datetime

import json
import time

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import rgb_to_hsv, hsv_to_rgb
from PIL import Image
from wordcloud import WordCloud, ImageColorGenerator

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from sqlalchemy import cast, create_engine, distinct, Date, func
from sqlalchemy.dialects.postgresql import insert as pg_insert

from database.models import (
    Album,
    AlbumArtist,
    Artist,
    Song,
    SongArtist,
    SongStreamed,
    CurrentSong,
)
from database.utils import SessionManager


def grey_color_func(
    word, font_size, position, orientation, random_state=None, **kwargs
) -> str:
    """Returns grey color for word cloud font"""
    random.seed(42)
    return "hsl(0, 0%%, %d%%)" % random.randint(60, 100)


def generate_word_cloud(
    font_path: str,
    freq_dict: dict,
    outfile_path: str,
    mask_image: str,
    multi_flag: bool,
):
    """Generates a word cloud from frequency_dict, mask_image, and stores result in file_path"""
    mask = np.array(Image.open(mask_image))

    wc = WordCloud(
        background_color="black",
        font_path=font_path,
        mask=mask,
        # max_font_size=256,
    ).generate_from_frequencies(freq_dict)

    if multi_flag:
        image_colors = ImageColorGenerator(mask)
        fig, axes = plt.subplots(1, 3)
        axes[0].imshow(wc, interpolation="bilinear")
        axes[1].imshow(wc.recolor(color_func=image_colors), interpolation="bilinear")
        axes[2].imshow(mask, cmap=plt.cm.gray, interpolation="bilinear")
        for ax in axes:
            ax.set_axis_off()
        plt.axis("off")
        plt.savefig(
            outfile_path,
            bbox_inches="tight",
            pad_inches=0,
            dpi=1200,
        )
    else:
        plt.imshow(
            wc.recolor(color_func=grey_color_func),
            interpolation="bilinear",
        )
        plt.axis("off")
        plt.savefig(
            outfile_path,
            bbox_inches="tight",
            pad_inches=0,
            dpi=1200,
        )


def generate_thumbnail(in_file: str, size=(512, 512)) -> None:
    """Generates a thumbnail image from the word cloud plot.

    Args:
        in_file (str): The input file path of the image to generate the thumbnail from.
        size (tuple, optional): The size of the thumbnail. Defaults to (512, 512).

    Raises:
        FileNotFoundError: If the input file is not found.

    Returns:
        None
    """
    try:
        with Image.open(in_file) as tn:
            tn.thumbnail(size)
            tn.copy().save(f"{in_file}.thumbnail", "PNG")
    except FileNotFoundError as e:
        raise FileNotFoundError(f"No file found at {in_file}...") from e


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


def load_tables(engine, record_dicts: list) -> None:
    """
    Load records into the database tables.

    Args:
        record_dicts: A list of dictionaries, where each dictionary represents a chunk of records to be inserted.

    Returns:
        None
    """
    with SessionManager(engine) as session:
        statements = [
            pg_insert(chunk["model"]).values(record).on_conflict_do_nothing()
            for chunk in record_dicts
            for record in chunk["records"]
        ]
        [session.execute(statement) for statement in statements]


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


def playlist(engine) -> list:
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


def query_all_song_streamed(engine) -> list[object]:
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


def random_songs(engine) -> dict:
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
        return {"today": formatted_date, "song_ids": random.sample(all_songs, 100)}


def song_ids(engine) -> list:
    """
    Retrieve a list of all song IDs from the database.

    Returns:
    A list of all song IDs available in the database.
    """
    with SessionManager(engine) as session:
        return [id[0] for id in session.query(Song.id).all()]


def songs_by_date(engine, query_date: datetime) -> list[tuple]:
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


def summary(engine) -> dict:
    """
    Retrieve a summary of various statistics and counts related to song streaming.

    Returns:
    A dictionary containing the following information:
    - "table_counts": The counts of records in various tables.
    - "stream_count_per_day": The number of song streams per day.
    - "freq_by_day": The frequency of song streams by day, ordered from most recent to oldest.
    - "play_today": The number of song streams recorded today.
    - "top_artist_year": The artist with the highest number of streams in the current year.
    - "top_song_today": The song with the highest number of streams today, along with its artist.
    - "top_song_year": The song with the highest number of streams in the current year, along with its artist.
    - "year_count": The total number of song streams in the current year.
    - "days": The total duration of all songs streamed.

    Example:
    summary()  # Retrieves a summary of song streaming statistics.
    """
    year = int(datetime.datetime.utcnow().strftime("%Y"))
    year_begin = datetime.datetime(year, 1, 1)
    year_end = datetime.datetime(year, 12, 31)
    with SessionManager(engine) as session:
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
            "top_artist_year": (
                session.query(
                    func.count(Artist.id),
                    Artist.name,
                )
            )
            .join(
                Song,
                Song.artist_id == Artist.id,
            )
            .join(
                SongStreamed,
                SongStreamed.song_id == Song.id,
            )
            .filter(cast(SongStreamed.played_at, Date) >= year_begin)
            .group_by(
                Artist.id,
                Artist.name,
            )
            .order_by(func.count(Artist.id).desc())
            .first(),
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
            "top_song_year": (
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
            .filter(cast(SongStreamed.played_at, Date) >= year_begin)
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


def table_counts(engine) -> dict:
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


def update_song_length(engine, id: str, length: int) -> dict:
    with SessionManager(engine) as session:
        (session.query(Song).filter(Song.id == id).update({Song.length: length}))


def weekly_summary(engine, week: dict) -> dict:
    with SessionManager(engine) as session:
        for day in week:
            day["count"] = (
                session.query(func.count(SongStreamed.song_id))
                .filter(cast(SongStreamed.played_at, Date) == day["week_day"])
                .all()[0][0]
            )
        return week


def yesterday_top_ten(engine) -> dict:
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


def distinct_songs(engine) -> list:
    with SessionManager(engine) as session:
        return [i[0] for i in session.query(distinct(SongStreamed.song_id)).all()]


def add_artists(engine, data: dict) -> None:
    with SessionManager(engine) as session:
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


def add_albums(engine, data: dict) -> None:
    with SessionManager(engine) as session:
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


def add_songs(engine, data: dict) -> None:
    with SessionManager(engine) as session:
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


def transform_data(raw_track_data: list) -> dict:
    """
    Transform raw track data into a dictionary of desired JSON data.

    Args:
    - raw_track_data (list): Raw track data to be transformed.

    Returns:
    A dictionary containing the transformed data with the following keys:
    - song_id: ID of the song.
    - song_name: Name of the song.
    - song_length: Length of the song in milliseconds.
    - artist_id: ID of the artist.
    - artist_name: Name of the artist.
    - album_id: ID of the album.
    - album_name: Name of the album.
    - album_release_year: Release year of the album.
    - played_at: Timestamp of when the track was played.
    - spotify_url: URL of the track on Spotify.

    Example:
    raw_track_data = {
        "track": {
            "id": "12345",
            "name": "Example Song",
            "duration_ms": 300000,
            "artists": [
                {
                    "id": "6789",
                    "name": "Example Artist"
                }
            ],
            "album": {
                "id": "9876",
                "name": "Example Album",
                "release_date": "2022-01-01"
            },
            "external_urls": {
                "spotify": "https://example.com"
            }
        },
        "played_at": "2023-06-20T10:30:00.000Z"
    }
    transform_data(raw_track_data)  # Transforms raw track data into a dictionary.
    """
    try:
        track = raw_track_data["track"]
        artists = track["artists"]

        return {
            "song_id": track["id"],
            "song_name": track["name"],
            "song_length": track["duration_ms"],
            "artist_id": artists[0]["id"],
            "artist_name": artists[0]["name"],
            "album_id": track["album"]["id"],
            "album_name": track["album"]["name"],
            "album_release_year": track["album"]["release_date"][:4],
            "played_at": raw_track_data["played_at"][:19],
            "spotify_url": track["external_urls"]["spotify"],
        }
    except KeyError as e:
        raise ValueError(f"Invalid raw track data. Missing key: {str(e)}")
    except (TypeError, IndexError) as e:
        raise ValueError(f"Invalid raw track data format: {str(e)}")


def compile_model_lists(data_list: list) -> list:
    return (
        [
            {
                "id": record["album_id"],
                "name": record["album_name"],
                "release_year": record["album_release_year"],
                "artist_id": record["artist_id"],
            }
            for record in data_list
        ],
        [
            {
                "id": record["artist_id"],
                "name": record["artist_name"],
            }
            for record in data_list
        ],
        [
            {
                "id": record["song_id"],
                "name": record["song_name"],
                "album_id": record["album_id"],
                "artist_id": record["artist_id"],
                "spotify_url": record["spotify_url"],
                "length": record["song_length"],
            }
            for record in data_list
        ],
        [
            {"song_id": record["song_id"], "played_at": record["played_at"]}
            for record in data_list
        ],
    )


def create_spotify_client(credentials: dict) -> spotipy.Spotify:
    """Create a Spotify client object for accessing Spotify's Web API.

    This function initializes and returns a Spotify client object using the provided
    credentials for authentication and authorization. The client can be used to make
    requests to the Spotify Web API for retrieving user data, accessing playlists,
    and performing other operations related to music and user profiles.

    Args:
        credentials (dict): A dictionary containing the required authentication
        credentials for the Spotify client. It should have the following keys:
            - 'cache_path' (str): The file path where the Spotify OAuth token cache
              will be stored.
            - 'client_id' (str): The client ID obtained from the Spotify Developer
              Dashboard for your application.
            - 'client_secret' (str): The client secret obtained from the Spotify
              Developer Dashboard for your application.
            - 'redirect_uri' (str): The URI to redirect the user after successful
              authorization through the Spotify Web API.
            - 'scope' (str): The scope of access required for the application. This
              specifies the level of permissions the user grants to the application.

    Returns:
        spotipy.Spotify: A Spotify client object that can be used to make requests to
        the Spotify Web API.

    Example:
        credentials = {
            'cache_path': '/path/to/cache_file',
            'client_id': 'your_client_id',
            'client_secret': 'your_client_secret',
            'redirect_uri': 'https://your_redirect_uri.com',
            'scope': 'user-library-read user-read-recently-played',
        }
        spotify_client = create_spotify_client(credentials)
        user_playlists = spotify_client.current_user_playlists()
        print(user_playlists)
    """
    return spotipy.Spotify(
        auth_manager=SpotifyOAuth(
            cache_path=credentials["cache_path"],
            client_id=credentials["client_id"],
            client_secret=credentials["client_secret"],
            open_browser=False,
            redirect_uri=credentials["redirect_uri"],
            scope=credentials["scope"],
        ),
        requests_timeout=10,
        retries=5,
    )


def parse_recent_tracks(
    file_name: str,
) -> Tuple[
    Union[Tuple[List[Artist], List[Album], List[Song], List[SongStreamed]], str]
]:
    recent_artists = []
    recent_albums = []
    recent_album_artists = []
    recent_songs = []
    recent_song_artists = []
    recent_streams = []

    try:
        with open(file_name, "r", encoding="utf-8") as fp:
            data = json.load(fp)

        for item in data:
            album_section = item["track"]["album"]
            artists_section = item["track"]["artists"]

            album_id = album_section["id"]

            length = item["track"]["duration_ms"]
            played_at = item["played_at"]
            song_id = item["track"]["id"]
            song_name = item["track"]["name"]

            new_song = Song(
                id=song_id, name=song_name, album_id=album_id, length=length
            )
            recent_songs.append(new_song)

            new_song_streamed = SongStreamed(song_id=song_id, played_at=played_at)
            recent_streams.append(new_song_streamed)

            new_album = Album(
                id=album_section["id"],
                name=album_section["name"],
                release_year=album_section["release_date"][:4],
            )
            recent_albums.append(new_album)

            for artist in artists_section:
                new_artist = Artist(
                    id=artist["id"],
                    name=artist["name"],
                )
                recent_artists.append(new_artist)
                new_song_artists = SongArtist(
                    song_id=song_id,
                    artist_id=artist["id"],
                )
                recent_song_artists.append(new_song_artists)

            for artist in album_section["artists"]:
                new_album_artist = AlbumArtist(
                    album_id=album_id, artist_id=artist["id"]
                )
                recent_album_artists.append(new_album_artist)

        return (
            recent_artists,
            recent_albums,
            recent_album_artists,
            recent_songs,
            recent_song_artists,
            recent_streams,
        ), None

    except FileNotFoundError as e:
        return None, str(e)

    except KeyError as e:
        return None, str(e)

    except Exception as e:
        print(f"Error: {str(e)}")
        return None, str(e)


def parse_current_song(song_data: dict) -> CurrentSong:
    song = song_data["item"]
    artist = song["artists"][0]
    album = song["album"]

    return CurrentSong(
        song_id=song["id"],
        song_name=song["name"],
        song_url=song["external_urls"]["spotify"],
        song_artist_id=artist["id"],
        song_artist_name=artist["name"],
        song_album_id=album["id"],
        song_album=album["name"],
    )


def write_song_data(data_tuple: tuple) -> None:
    data = {
        "recent_artists": [artist.as_dict() for artist in data_tuple[0]],
        "recent_albums": [album.as_dict() for album in data_tuple[1]],
        "recent_album_artists": [album.as_dict() for album in data_tuple[2]],
        "recent_songs": [song.as_dict() for song in data_tuple[3]],
        "recent_song_artists": [song.as_dict() for song in data_tuple[4]],
        "recent_streams": [stream.as_dict() for stream in data_tuple[5]],
    }

    # Write the data dictionary to the JSON file
    with open(
        f"/tmp/{int(time.time())}_recently_played_data.json",
        "w",
        encoding="utf-8",
    ) as fp:
        json.dump(data, fp, indent=4)


def chunk_list(lst: list, chunk_size: int):
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def get_item_data(track_ids: list, sp: spotipy.Spotify):
    try:
        item_data = sp.tracks(track_ids)
        return item_data
    except Exception as e:
        print(f"Error fetching data: {e}")


def summary_main(query_results: dict) -> None:
    freq = {
        "Monday": 0,
        "Tuesday": 0,
        "Wednesday": 0,
        "Thursday": 0,
        "Friday": 0,
        "Saturday": 0,
        "Sunday": 0,
    }

    average_streams_per_day = sum(
        [row[1] for row in query_results["stream_count_per_day"]]
    ) // len(query_results["stream_count_per_day"])

    for day in query_results["freq_by_day"]:
        freq[day[0].strftime("%A")] = freq.get(day[0].strftime("%A")) + day[1]

    top_song_msg = ""
    print(f"\n\033[1mUTC\033[0m: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n**SpotifyData**\n\n-TableCounts-")
    [
        print(f"{model['model'].__name__}: {model['count']:,}")
        for model in query_results["table_counts"]
    ]
    print("\n*TotalDayFrequency*")
    [print(f"{day}: {freq[day]:,}") for day in freq]
    print(f"\n*MiscellaneousData*")
    print(f"AverageStreamsPerDay : {average_streams_per_day}")
    print(f"StreamTimeInDays: {(query_results['days'][0] // 1000) // 86400}")
    print(f"StreamsThisYear: {query_results['year_count']:,}")
    print(f"\n*TodayData*")
    print(f"StreamsToday: {query_results['play_today'][0]}")
    if query_results["top_song_today"] and query_results["top_song_today"][0] > 1:
        top_song_msg = (
            f"TodayTopSong: {query_results['top_song_today'][0]} "
            f"plays | {query_results['top_song_today'][1]}"
            f"- \033[1m{query_results['top_song_today'][2]}\033[0m\n"
        )
        print(top_song_msg)
    print(f"\n*YearData*")
    print(
        f"TopArtistThisYear: {query_results['top_artist_year'][1]} | Plays : {query_results['top_artist_year'][0]}"
    )
    print(
        f"TopSongThisYear: {query_results['top_song_year'][1]} | Plays: {query_results['top_song_year'][0]} | Artist: {query_results['top_song_year'][2]}"
    )
    print()
