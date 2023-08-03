import argparse
import concurrent.futures
import json
from functools import partial
from sqlalchemy import create_engine, exc as SQLAlchemyError


from config import Config
from database.utils import (
    create_database,
    get_distinct_song_ids,
    get_random_songs,
    get_song_id_count,
    get_yesterday_top_ten,
    insert_rows_with_conflict_handling,
    summary_queries,
)
from utils.lib import (
    create_new_playlist,
    get_spotify_client,
    parse_current_song,
    parse_recent_tracks,
    prompt_for_playlist_info,
    summary_main,
)


def create_new_spotify_playlist(config: Config) -> None:
    """
    Create a new Spotify playlist using the provided configuration and user input.

    Args:
        config (Config): An instance of the Config class containing Spotify credentials
                         and logging configurations.

    Returns:
        None

    Raises:
        Exception: If there's an error while creating the playlist.

    Note:
        This function uses the 'spotipy' library to interact with the Spotify Web API
        and requires a valid Spotify developer account and credentials.

    """
    try:
        spotify_credentials = dict(config.config["spotify"])
        sp = get_spotify_client(spotify_credentials)

        playlist_name, playlist_desc = prompt_for_playlist_info()

        if not playlist_name or not playlist_desc:
            print("Playlist name and description cannot be empty.")
            return

        response = create_new_playlist(playlist_name, playlist_desc, sp)
        if response[0]:
            config.file_logger.info(response[0])
        else:
            config.file_logger.error(response[1])

    except Exception as e:
        raise Exception("Error while creating playlist.") from e


def current_song(config: Config) -> None:
    """
    Get the currently playing song from the Spotify API and print its information.

    Parameters:
        config (Config()): The configuration object containing database and API credentials.

    Raises:
        Exception: If there is an error while fetching or processing the song data.

    Returns:
        None
    """
    try:
        engine = create_engine(config.db_config["db_uri"])
        spotify_credentials = dict(config.config["spotify"])
        sp = get_spotify_client(spotify_credentials)
        song_data = sp.currently_playing()

        if song_data:
            current_song = parse_current_song(song_data)
            count = get_song_id_count(engine, current_song.song_id)
            print(f"SongStreams: {count}")
            print(f"CurrentSong: {json.dumps(current_song.as_dict(), indent=4)}")
        else:
            print("Nothing playing currently")

    except Exception as e:
        raise Exception("Error while fetching or processing song data.") from e


def db_setup(config: Config) -> None:
    """
    Set up the database based on the provided configuration.

    This function attempts to create the necessary database tables using SQLAlchemy,
    based on the database URI provided in the config object.

    Args:
        config (Config): An instance of the Config class containing the database URI
                         and logging configurations.

    Returns:
        None

    Raises:
        SQLAlchemyError: If there's an error while creating the database tables.
        Exception: If an unexpected error occurs during the database setup.

    Note:
        This function uses SQLAlchemy to interact with the database. Make sure to
        provide a valid and accessible database URI in the config object.
    """
    try:
        config.file_logger.info("Attempting database creation")
        create_database(config.db_config["db_uri"])

    except SQLAlchemyError as e:
        config.file_logger.error(f"An error occurred while creating the database: {e}")

    except Exception as e:
        config.file_logger.error(f"An unexpected error occurred: {e}")


def etl(config: Config) -> None:
    """
    Extract, transform, and load (ETL) Spotify recently played tracks data into the database.

    This function extracts the recently played tracks data from the user's Spotify account
    using the provided Spotify credentials from the config object. The data is then transformed
    and saved into a JSON file specified by the file paths in the config object. Finally,
    the transformed data is loaded into the database using SQLAlchemy's conflict handling
    mechanism.

    Args:
        config (Config): An instance of the Config class containing Spotify credentials,
                         file paths, database URI, and logging configurations.

    Returns:
        None

    Raises:
        ValueError: If Spotify credentials or file paths are not found in the config.
        SQLAlchemyError: If there's an error during the database operation.
        Exception: If an unexpected error occurs during the ETL process.

    Note:
        - This function requires valid Spotify credentials in the config object to interact
          with the Spotify Web API.
        - Make sure the file paths in the config object are set appropriately.
        - The function uses SQLAlchemy to interact with the database. Ensure the provided
          database URI in the config object is valid and accessible.
    """
    try:
        spotify_credentials = dict(config.config["spotify"])
        file_paths = dict(config.config["file_paths"])

        if not spotify_credentials:
            raise ValueError("Spotify credentials not found in config.")

        if not file_paths:
            raise ValueError("File paths not found in config.")

        engine = create_engine(config.db_config["db_uri"])

        sp = get_spotify_client(spotify_credentials)
        recent_tracks = sp.current_user_recently_played()

        if recent_tracks and "items" in recent_tracks:
            with open(file_paths["recent_songs"], "w", encoding="utf-8") as fp:
                json.dump(recent_tracks["items"], fp)

            data_tuple = parse_recent_tracks(file_paths["recent_songs"])
            if data_tuple is not None:
                try:
                    row_counts, error = insert_rows_with_conflict_handling(
                        engine, data_tuple[0]
                    )
                    if error:
                        config.file_logger.error(error)
                    else:
                        for model_name, count in row_counts.items():
                            if count > 0:
                                config.file_logger.info(
                                    "%s: %s rows inserted", model_name, count
                                )
                except SQLAlchemyError as db_error:
                    config.file_logger.critical("Database error: %s", db_error)
                    raise
            else:
                config.file_logger.warning("No data to process")
        else:
            config.file_logger.warning("No recent tracks found")

    except Exception as e:
        config.file_logger.critical("ETL process failed with error: %s", e)
        raise


def random_song_playlist(config: Config) -> None:
    """
    Update a Spotify playlist with random songs.

    This function selects a specified number of random song IDs from the database and updates
    the corresponding Spotify playlist with the selected songs. The playlist's details, such
    as description and number of tracks, are also updated.

    Args:
        config (Config): An instance of the Config class containing database URI,
                         Spotify credentials, and logging configurations.

    Returns:
        None

    Raises:
        Exception: If there's an error during the process.

    Note:
        - The function requires valid Spotify credentials and a database URI to interact with
          the Spotify Web API and the database.
        - The number of random song IDs to select is defined by the constant `NUM_SONG_IDS`.
          Adjust this value based on your preference.
        - The function logs the status of each step, including successful updates and any errors.
    """
    NUM_SONG_IDS = 100
    try:
        engine = create_engine(config.db_config["db_uri"])
        spotify_credentials = dict(config.config["spotify"])
        sp = get_spotify_client(spotify_credentials)

        random_song_ids = get_random_songs(engine, NUM_SONG_IDS)

        config.file_logger.info(
            "Updating details for Spotify playlist: %s",
            spotify_credentials["random_playlist"],
        )
        sp.playlist_change_details(
            spotify_credentials["random_playlist"],
            description=f"Here is {NUM_SONG_IDS} random songs. Last updated {random_song_ids['today']}",
        )
        config.file_logger.info(
            "Refresing %s new tracks for playlist: %s",
            NUM_SONG_IDS,
            spotify_credentials["random_playlist"],
        )
        sp.playlist_replace_items(
            spotify_credentials["random_playlist"], random_song_ids["song_ids"]
        )
        config.file_logger.info(
            "Update successful for Spotify playlist: %s",
            spotify_credentials["random_playlist"],
        )
    except Exception as e:
        config.file_logger.error(e)


def summary(config: Config) -> None:
    engine = create_engine(config.db_config["db_uri"])
    summary_results = summary_queries(engine)
    summary_main(summary_results)


def yesterday_top_ten(config: Config) -> None:
    """
    Update a Spotify playlist with top tracks from yesterday.

    This function takes a `Config` object as an argument, which contains necessary
    configurations including database connection and Spotify API details. The function
    retrieves the top ten tracks from yesterday's data using a database engine,
    then updates a designated Spotify playlist with these tracks and their details.

    Args:
        config (Config): A configuration object containing database and Spotify settings.

    Raises:
        This function does not explicitly raise any exceptions. However, it can catch
        and log any exceptions that occur during the process.

    Returns:
        None: This function doesn't return any value. It performs the task of updating
        the specified Spotify playlist with top tracks from yesterday's data.
    """
    try:
        engine = create_engine(config.db_config["db_uri"])
        spotify_metadata = dict(config.config["spotify"])
        sp = get_spotify_client(spotify_metadata)

        yesterday_top_ten = get_yesterday_top_ten(engine)

        config.file_logger.info(
            "Updating details for Spotify playlist: %s",
            spotify_metadata["yesterday_top_10_id"],
        )
        sp.playlist_change_details(
            spotify_metadata["yesterday_top_10_id"],
            description=yesterday_top_ten["desc"],
        )

        config.file_logger.info(
            "Refresing top tracks from yesterday for playlist: %s",
            spotify_metadata["yesterday_top_10_id"],
        )
        sp.playlist_replace_items(
            spotify_metadata["yesterday_top_10_id"], yesterday_top_ten["song_ids"]
        )

        config.file_logger.info(
            "Update successful for Spotify playlist: %s",
            spotify_metadata["yesterday_top_10_id"],
        )
    except Exception as e:
        config.file_logger.error(e)


def main() -> None:
    """
    Entry point for the Spotify History CLI application.

    This function is the main entry point for the Spotify History CLI application. The
    CLI allows users to interact with Spotify's API, manage their music history, and
    perform ETL (Extract, Transform, Load) operations on the data. Users can choose from
    various functions such as creating a new Spotify playlist, fetching current song
    details, setting up the database, performing ETL tasks, generating a random playlist,
    summarizing data, and fetching yesterday's top tracks.

    The function parses command-line arguments to determine which specific function to
    execute. It then calls the corresponding function based on the user's choice.

    Args:
        None: This function takes no arguments from outside, but it interacts with the
        command-line arguments provided by the user.

    Raises:
        This function does not explicitly raise any exceptions. Errors related to invalid
        function names or execution issues are handled by displaying appropriate error
        messages.

    Returns:
        None: This function doesn't return any value. It serves as the entry point for
        running the CLI application and executing the chosen functions.
    """
    config = Config()
    parser = argparse.ArgumentParser(
        description="This is the entry point for the Spotify History CLI application. "
        "The CLI allows you to perform various tasks related to Spotify history data, "
        "including extracting recently played tracks, analyzing top songs, and setting "
        "up the database for data storage. By running this CLI, you can interact with "
        "Spotify's API, manage your music history, and perform ETL (Extract, Transform, "
        "Load) operations on the data. Use the provided options to choose which function "
        "you want to execute, and the CLI will guide you through the process. Happy "
        "Spotify history exploration!"
    )
    parser.add_argument(
        "--function",
        choices=[
            "create_new_spotify_playlist",
            "current_song",
            "daily_playlist",
            "db_setup",
            "etl",
            "random_playlist",
            "summary",
            "yesterday",
        ],
        required=True,
        help="Specify the function to call (e.g., etl, current_song)",
    )

    args = parser.parse_args()

    match args.function:
        case "create_new_spotify_playlist":
            create_new_spotify_playlist(config)
        case "current_song":
            current_song(config)
        case "db_setup":
            db_setup(config)
        case "etl":
            etl(config)
        case "random_playlist":
            random_song_playlist(config)
        case "summary":
            summary(config)
        case "yesterday":
            yesterday_top_ten(config)
        case _:
            print(
                "Invalid function name. Use 'etl' for the ETL process or 'current_song' for the current song function."
            )


if __name__ == "__main__":
    main()
