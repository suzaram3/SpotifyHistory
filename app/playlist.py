"""
Author : Mitch Suzara <suzaram3@gmail.com>
Date   : 2022-04-14
Purpose: Main driver for updating top 100 songs
"""
import base64, configparser, io, logging, logging.config

from PIL import Image
from sqlalchemy.orm import sessionmaker
from session import SessionHandler

from db import DB
from models import SongPlayed
from spotify import SpotifyHandler

config = configparser.ConfigParser()
config.read(
    "/Users/msuzara/Library/Mobile Documents/com~apple~CloudDocs/cloud_workspace/python/SpotifyHistory/spotify.conf"
)
logging.config.fileConfig(
    "/Users/msuzara/Library/Mobile Documents/com~apple~CloudDocs/cloud_workspace/python/SpotifyHistory/logging.conf"
)
file_logger = logging.getLogger("file")
console_logger = logging.getLogger("console")


def img_base64(in_file: str) -> str:
    with open(in_file, "rb") as img_file:
        return base64.b64encode(img_file.read())


def playlist_driver() -> None:

    db = DB.create()
    engine = db.engine
    Session = sessionmaker(bind=engine)
    session = Session()
    user_session = SessionHandler.create(session, SongPlayed)
    spotify = SpotifyHandler()
    counts = user_session.get_top_songs()
    song_ids = [song[1] for song in counts]
    image_str = img_base64(config["spotify"]["top_100_cover_image"])
    items = {
        "id": config["spotify"]["top_100"],
        "items": song_ids,
        "image_b64": image_str,
    }
    spotify.update_playlist(**items)


if __name__ == "__main__":
    playlist_driver()
