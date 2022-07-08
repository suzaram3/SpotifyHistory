import logging
import logging.config

from sqlalchemy.orm import sessionmaker
from session import SessionHandler

from db import DB
from models import Artist, Album, Song, SongStreamed
from transform import TransformData
from spotify import SpotifyHandler

try:
    logging.config.fileConfig(
            "/Users/msuzara/Library/Mobile Documents/com~apple~CloudDocs/cloud_workspace/python/SpotifyHistory/logging.conf"
    )
    file_logger = logging.getLogger("file")
    console_logger = logging.getLogger("console")
except Error as e:
    print(f"ERROR: {e}")


def main() -> None:
    """Main function for the etl program: gets recent songs and inserts them into the music.extract table"""
    # setup
    db = DB("prod")
    engine = db.engine
    Session = sessionmaker(bind=engine)
    session = Session()
    album_session = SessionHandler.create(session, Album)
    artist_session = SessionHandler.create(session, Artist)
    song_session = SessionHandler.create(session, Song)
    stream_session = SessionHandler.create(session, SongStreamed)
    td = TransformData()
    spotify = SpotifyHandler()

    # fetch
    # before_insert = user_session.get_total_count()
    raw_data = spotify.get_recently_played()

    # transform
    transform_raw_data = [td.transform_data(item) for item in raw_data["items"]]

    album_before_count = album_session.get_total_count()
    artist_before_count = artist_session.get_total_count()
    song_before_count = song_session.get_total_count()
    stream_before_count = stream_session.get_total_count()

    song_data = [
        {
            "id": record["song_id"],
            "name": record["song_name"],
            "album_id": record["album_id"],
            "artist_id": record["artist_id"],
            "spotify_url": record["spotify_url"],
        }
        for record in transform_raw_data
    ]
    album_data = [
        {
            "id": record["album_id"],
            "name": record["album_name"],
            "release_year": record["album_release_year"],
            "artist_id": record["artist_id"],
        }
        for record in transform_raw_data
    ]
    artist_data = [
        {
            "id": record["artist_id"],
            "name": record["artist_name"],
        }
        for record in transform_raw_data
    ]
    stream_data = [
        {"song_id": record["song_id"], "played_at": record["played_at"]}
        for record in transform_raw_data
    ]

    # insert
    try:
        album_session.insert_many(album_data)
        artist_session.insert_many(artist_data)
        song_session.insert_many(song_data)
        stream_session.insert_many(stream_data)

        album_after_count = album_session.get_total_count()
        artist_after_count = artist_session.get_total_count()
        song_after_count = song_session.get_total_count()
        stream_after_count = stream_session.get_total_count()

        if album_after_count > album_before_count:
            file_logger.info(
                f"{album_after_count-album_before_count} rows inserted into {album_session.model.__tablename__} "
            )
        if artist_after_count > artist_before_count:
            file_logger.info(
                f"{artist_after_count-artist_before_count} rows inserted into {artist_session.model.__tablename__} "
            )
        if song_after_count > song_before_count:
            file_logger.info(
                f"{song_after_count-song_before_count} rows inserted into {song_session.model.__tablename__} "
            )
        if stream_after_count > stream_before_count:
            file_logger.info(
                f"{stream_after_count-stream_before_count} rows inserted into {stream_session.model.__tablename__} "
            )

        session.commit()
    except Exception as e:
        session.rollback()
        console_logger.info(e)
        raise e
    finally:
        session.close()


if __name__ == "__main__":
    main()
