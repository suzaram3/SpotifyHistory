import logging, logging.config

from sqlalchemy.orm import sessionmaker
from db import DB
from session import SessionHandler
from models import SongPlayed

from spotify import SpotifyHandler

logging.config.fileConfig(
    "/Users/msuzara/Library/Mobile Documents/com~apple~CloudDocs/cloud_workspace/python/SpotifyHistory/logging.conf"
)
file_logger = logging.getLogger("file")
console_logger = logging.getLogger("console")


def update(session, model, query_dict, update_dict):
    # return session.query(model).filter_by(**query_dict).update(update_dict)
    session.query(model).filter_by(**query_dict).update(update_dict)
    session.commit()


def temp() -> None:
    spotify = SpotifyHandler()
    result = spotify.get_current_track()
    update_data = {
        "song_id": result["item"]["id"],
        "song_name": result["item"]["name"],
        "artist_id": result["item"]["artists"][0]["id"],
        "artist_id": result["item"]["artists"][0]["name"],
        "album_id": result["item"]["album"]["id"],
        "album_name": result["item"]["album"]["name"],
        "album_release_year": result["item"]["album"]["release_date"][:4],
        "spotify_url": result["item"]["external_urls"]["spotify"],
    }

    console_logger.info(update_data)

    invalid_data = {"song_id": "2HbKqm4o0w5wEeEFXm2sD4"}

    count = update(session, SongPlayed, invalid_data, update_data)
    console_logger.info(count)


def one_time() -> None:

    db = DB.create()
    engine = db.engine
    Session = sessionmaker(bind=engine)
    session = Session()
    sp = SessionHandler.create(session, SongPlayed)
    streams = sp.get_all(
        {"song_id": SongPlayed.song_id, "played_at": SongPlayed.played_at}
    )
    console_logger.info(f"{streams[0]=}")


if __name__ == "__main__":
    one_time()
