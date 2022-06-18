"""
Author : Mitch Suzara <suzaram3@gmail.com>
Date   : 2022-04-14
Purpose: Main driver for updating top 100 songs
"""
import base64, configparser, logging, logging.config

from sqlalchemy.orm import sessionmaker
from session import SessionHandler

from db import DB
from models import SongStreamed
from spotify import SpotifyHandler

config = configparser.ConfigParser()
config.read(
    "/Users/msuzara/Library/Mobile Documents/com~apple~CloudDocs/cloud_workspace/python/SpotifyHistory/spotify.conf"
)


def img_base64(in_file: str) -> str:
    """Geneate base64 string from thumbnail image file"""
    with open(in_file, "rb") as img_file:
        return base64.b64encode(img_file.read())


def playlist_driver() -> None:
    """Main function to update the top 100 songs playlist: updates track list and cover image"""

    db = DB("prod")
    engine = db.engine
    Session = sessionmaker(bind=engine)
    session = Session()
    user_session = SessionHandler.create(session, SongStreamed)
    spotify = SpotifyHandler()
    counts = user_session.get_top_songs()
    song_ids = [song[1] for song in counts]
    image_str = img_base64(config["spotify"]["top_100_cover_image"])
    items = {
        "playlist_id": config["spotify"]["top_100"],
        "items": song_ids,
        "image": image_str,
    }
    spotify.update_playlist(**items)


playlist_driver()
