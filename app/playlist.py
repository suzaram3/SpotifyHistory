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
    "/home/msuzara/SpotifyHistory/spotify.conf"
)
logging.config.fileConfig(
    "/home/msuzara/SpotifyHistory/logging.conf"
)
console_logger = logging.getLogger("console")
file_logger = logging.getLogger("playlist")


# def img_base64(in_file: str) -> str:
#     """Geneate base64 string from thumbnail image file"""
#     with open(in_file, "rb") as img_file:
#         return base64.b64encode(img_file.read())


# def playlist_driver() -> None:
"""Main function to update the top 100 songs playlist: updates track list and cover image"""
sh, sp = SessionHandler(), SpotifyHandler()

with sh.session_scope() as session:
    counts = sh.get_top_records(session, SongStreamed.song_id, 200)

with open(config["spotify"]["top_100_cover_image"], "rb") as img_file:
    image_str = base64.b64encode(img_file.read())

song_ids = [song[0] for song in counts]
chunked_ids = [song_ids[i : i + 100] for i in range(0, len(song_ids), 100)]


items = {
    "playlist_id": config["spotify"]["top_100"],
    "items": chunked_ids[0],
    "image": image_str,
}

sp.update_playlist(**items)

sp.playlist_append(items['playlist_id'], chunked_ids[1])

file_logger.info(f"Playlist: {items['playlist_id']} updated.")