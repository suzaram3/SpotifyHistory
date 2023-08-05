from typing import List, Optional, Tuple, Union
from datetime import datetime, timedelta

import random
import json
import time

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import rgb_to_hsv, hsv_to_rgb
from PIL import Image
from wordcloud import WordCloud, ImageColorGenerator

import spotipy
from spotipy.oauth2 import CacheFileHandler, SpotifyOAuth

from database.models import (
    Album,
    AlbumArtist,
    Artist,
    Song,
    SongArtist,
    SongStreamed,
    CurrentSong,
)

"""Spotify API Modules"""


def create_new_playlist(
    playlist_name: str, playlist_desc: str, sp: spotipy.Spotify
) -> tuple[str, None]:
    """
    Create a new Spotify playlist for the current user.

    Args:
        playlist_name (str): The name of the new playlist.
        playlist_desc (str): The description of the new playlist.
        sp (spotipy.Spotify): The Spotipy client instance authenticated with the user's credentials.

    Returns:
        tuple[None, str]: A tuple containing either None (if the playlist was created successfully)
                          or an error message (if there was an issue with the Spotify authentication).

    Raises:
        spotipy.SpotifyException: If there is an error in the Spotify authentication process.
    """
    try:
        # Get the user ID
        response = sp.current_user()
        user_id = response["id"]

        # Create the playlist
        playlist = sp.user_playlist_create(
            user_id, playlist_name, public=True, description=playlist_desc
        )

        playlist_id = playlist["id"]

        return (
            f"Playlist '{playlist_name}' created successfully with ID: {playlist_id}",
            None,
        )

    except spotipy.SpotifyException as e:
        return None, e


def get_spotify_client(credentials: dict) -> Union[spotipy.Spotify, str]:
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
        Union[spotipy.Spotify, str]: If successful, returns a Spotify client object
        that can be used to make requests to the Spotify Web API. If there's an error,
        returns an error message as a string.

    Example:
        credentials = {
            'cache_path': '/path/to/cache_file',
            'client_id': 'your_client_id',
            'client_secret': 'your_client_secret',
            'redirect_uri': 'https://your_redirect_uri.com',
            'scope': 'user-library-read user-read-recently-played',
        }
        spotify_client = create_spotify_client(credentials)
        if isinstance(spotify_client, spotipy.Spotify):
            user_playlists = spotify_client.current_user_playlists()
            print(user_playlists)
        else:
            print(f"Error: {spotify_client}")
    """
    try:
        cache_handler = CacheFileHandler(credentials["cache_path"])

        auth_manager = SpotifyOAuth(
            cache_handler=cache_handler,
            client_id=credentials["client_id"],
            client_secret=credentials["client_secret"],
            redirect_uri=credentials["redirect_uri"],
            scope=credentials["scope"],
            open_browser=False,
            requests_timeout=10,
        )

        return spotipy.Spotify(auth_manager=auth_manager)
    except Exception as e:
        return str(e)


"""Data Extraction Modules"""


def chunk_list(lst: list, chunk_size: int = 50):
    return [lst[i : i + chunk_size] for i in range(0, len(lst), chunk_size)]


def parse_recent_tracks(
    file_name: str,
) -> Tuple[
    Union[Tuple[List[Artist], List[Album], List[Song], List[SongStreamed]], str]
]:
    """
    Parse the recent tracks data from a JSON file.

    Args:
        file_name (str): The name of the JSON file containing recent tracks data.

    Returns:
        Tuple: A tuple containing the parsed data as lists of Artists, Albums, Songs,
               SongArtists, and SongStreamed. If an error occurs during parsing, a
               tuple containing (None, error_message) is returned.

    Raises:
        FileNotFoundError: If the specified file_name is not found.
        KeyError: If a required key is missing in the JSON data.
    """
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


def parse_current_song(song_data: dict) -> Union[CurrentSong, str]:
    """
    Parse the current song data received from Spotify.

    Args:
        song_data (dict): A dictionary containing the current song data.

    Returns:
        Union[CurrentSong, str]: If the parsing is successful, returns an instance
        of the CurrentSong class containing parsed data. Otherwise, returns an
        error message as a string.
    """
    try:
        song = song_data["item"]
        artist = song["artists"][0]
        album = song["album"]

        current_song = CurrentSong(
            song_id=song["id"],
            song_name=song["name"],
            song_url=song["external_urls"]["spotify"],
            song_artist_id=artist["id"],
            song_artist_name=artist["name"],
            song_album_id=album["id"],
            song_album=album["name"],
        )

        return current_song, None  # Return the CurrentSong object and no error

    except KeyError as e:
        error_message = f"KeyError: {e}"
        return None, error_message
    except (TypeError, IndexError) as e:
        error_message = f"TypeError or IndexError: {e}"
        return None, error_message


"""I/O Modules"""


def prompt_for_playlist_info() -> tuple[str, str]:
    playlist_name = input("Enter the playlist name: ")
    playlist_desc = input("Enter the playlist description: ")
    return playlist_name, playlist_desc


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
    print(
        f"PercentageDifferenceFromLastYear: {query_results['percentage_from_last_year']}"
    )
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


def write_song_data(
    data_tuple: Tuple[
        list[Artist],
        list[Album],
        list[AlbumArtist],
        list[Song],
        list[SongArtist],
        list[SongStreamed],
    ]
) -> None:
    """
    Write song data to a JSON file in /tmp/ directory.

    Args:
        data_tuple (Tuple): A tuple containing song data for recent artists,
        recent albums, recent album artists, recent songs, recent song artists,
        and recent streams.

    Raises:
        Exception: If there is an error during writing the data to the file.
    """
    try:
        data = {
            "recent_artists": [artist.as_dict() for artist in data_tuple[0]],
            "recent_albums": [album.as_dict() for album in data_tuple[1]],
            "recent_album_artists": [album.as_dict() for album in data_tuple[2]],
            "recent_songs": [song.as_dict() for song in data_tuple[3]],
            "recent_song_artists": [song.as_dict() for song in data_tuple[4]],
            "recent_streams": [stream.as_dict() for stream in data_tuple[5]],
        }

        # Write the data dictionary to the JSON file
        file_name = f"/tmp/{int(time.time())}_recently_played_data.json"
        with open(file_name, "w", encoding="utf-8") as fp:
            json.dump(data, fp, indent=4)
    except Exception as e:
        raise Exception(f"Error writing song data to file: {str(e)}")


"""Miscellaneous Modules """


def get_dates_of_week() -> list[datetime]:
    today = datetime.today()
    start_date = today - timedelta(days=today.weekday())
    end_date = start_date + timedelta(days=6)
    week_dates = [start_date + timedelta(days=i) for i in range(7)]
    return week_dates


def get_unix_timestamps():
    timestamps = []
    now = int(time.time())  # Current Unix timestamp in seconds
    yesterday = now - 86400  # Subtract 24 hours (86400 seconds)

    # Generate timestamps in 30-minute increments
    timestamp = yesterday
    while timestamp <= now:
        timestamps.append(timestamp * 1000)  # Convert seconds to milliseconds
        timestamp += 1800  # Increment by 30 minutes (1800 seconds)

    return timestamps


def is_spotify_instance(spotify_object: spotipy.Spotify) -> bool:
    return type(spotify_object) is spotipy.Spotify


"""WordCloud Modules"""


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
