"""
Author : Mitch Suzara <suzaram3@gmail.com>
Date   : 2022-04-14
Purpose: Main driver for updating top 100 songs
"""
from asyncio.log import logger
import configparser, logging, logging.config

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


def main() -> None:

    db = DB.create()
    engine = db.engine
    Session = sessionmaker(bind=engine)
    session = Session()
    user_session = SessionHandler.create(session, SongPlayed)
    spotify = SpotifyHandler()
    counts = user_session.get_top_songs()
    song_ids = [song[1] for song in counts]
    spotify.update_playlist(config["spotify"]["top_100"], song_ids)


if __name__ == "__main__":
    main()
