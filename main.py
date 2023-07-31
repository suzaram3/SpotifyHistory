import argparse
import concurrent.futures
import json
from functools import partial
import random
from sqlalchemy import create_engine, exc as SQLAlchemyError


from dev_config import DevConfig
from database.utils import (
    create_database,
    get_distinct_song_ids,
    get_song_id_count,
    insert_rows_with_conflict_handling,
    summary_queries,
)
from src.lib import (
    create_spotify_client,
    chunk_list,
    get_item_data,
    get_top_songs_and_artists,
    parse_current_song,
    parse_recent_tracks,
    summary_main,
    write_song_data,
    yesterday_top_ten,
)


def current_song(config: DevConfig) -> None:
    """
    Get the currently playing song from the Spotify API and print its information.

    Parameters:
        config (DevConfig): The configuration object containing database and API credentials.

    Raises:
        Exception: If there is an error while fetching or processing the song data.

    Returns:
        None
    """
    try:
        engine = create_engine(config.db_config["db_uri"])
        spotify_credentials = dict(config.config["spotify"])
        sp = create_spotify_client(spotify_credentials)
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



def daily_playlist(config: DevConfig) -> None:
    db_config = config.get_db_config()
    engine = create_engine(db_config["db_uri"])

    results = yesterday_top_ten(engine)
    print(f"{results=}")


def db_setup(config: DevConfig) -> None:
    try:
        config.file_logger.info("Attempting database creation")
        create_database(config.db_config["db_uri"])

    except SQLAlchemyError as e:
        config.file_logger.error(f"An error occurred while creating the database: {e}")

    except Exception as e:
        config.file_logger.error(f"An unexpected error occurred: {e}")


def etl(config: DevConfig) -> None:
    try:
        spotify_credentials = dict(config.config["spotify"])
        file_paths = dict(config.config["file_paths"])

        if not spotify_credentials:
            raise ValueError("Spotify credentials not found in config.")

        if not file_paths:
            raise ValueError("File paths not found in config.")

        engine = create_engine(config.db_config["db_uri"])

        sp = create_spotify_client(spotify_credentials)
        recent_tracks = sp.current_user_recently_played()

        if recent_tracks and "items" in recent_tracks:
            with open(file_paths["recent_songs"], "w", encoding="utf-8") as fp:
                json.dump(recent_tracks["items"], fp)

            data_tuple = parse_recent_tracks(file_paths["recent_songs"])
            if data_tuple is not None:
                write_song_data(data_tuple[0])
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
                                    "%s: %s rows inserted.", model_name, count
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


def streaming_history(config: DevConfig) -> None:
    engine = create_engine(config.db_config["db_uri"])

    spotify_credentials = dict(config.config["spotify"])
    sp = create_spotify_client(spotify_credentials)

    distinct_ids = get_distinct_song_ids(engine)

    chunked_ids = chunk_list(distinct_ids, 50)

    all_item_data = []

    num_threads = 8
    with concurrent.futures.ThreadPoolExecutor(max_workers=num_threads) as executor:
        # Use functools.partial to pass the 'sp' object to the get_item_data function
        partial_get_item_data = partial(get_item_data, sp=sp)

        future_to_item = {
            executor.submit(partial_get_item_data, chunk): chunk
            for chunk in chunked_ids
        }

        all_item_data = []
        for future in concurrent.futures.as_completed(future_to_item):
            chunk = future_to_item[future]
            try:
                item_data = future.result()
                if item_data:
                    all_item_data.extend(item_data["tracks"])
            except Exception as e:
                print(f"An error occurred: {e}")

    # Write all_item_data to a JSON file
    output_file = "item_data.json"
    with open(output_file, "w") as f:
        json.dump(all_item_data, f, indent=4)

    print(f"Data written to '{output_file}'.")


def summary(config: DevConfig) -> None:
    engine = create_engine(config.db_config["db_uri"])
    summary_results = summary_queries(engine)
    summary_main(summary_results)


def main() -> None:
    config = DevConfig()
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
            "current_song",
            "daily_playlist",
            "db_setup",
            "etl",
            "streaming_history",
            "summary",
        ],
        required=True,
        help="Specify the function to call (e.g., etl, current_song)",
    )

    args = parser.parse_args()

    match args.function:
        case "current_song":
            current_song(config)
        case "daily_playlist":
            daily_playlist(config)
        case "db_setup":
            db_setup(config)
        case "etl":
            etl(config)
        case "streaming_history":
            streaming_history(config)
        case "summary":
            summary(config)
        case _:
            print(
                "Invalid function name. Use 'etl' for the ETL process or 'current_song' for the current song function."
            )


if __name__ == "__main__":
    main()
