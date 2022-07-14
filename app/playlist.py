"""
Author : Mitch Suzara <suzaram3@gmail.com>
Date   : 2022-04-14
Purpose: Main driver for updating top 100 songs
"""
import base64
from collections import Counter
from sqlalchemy.orm import sessionmaker
from session import SessionHandler

from config import ProductionConfig
from models import SongStreamed
from spotify import SpotifyHandler


# def playlist_driver() -> None:
"""Main function to update the top 100 songs playlist: updates track list and cover image"""
pc, sh, sp = ProductionConfig(), SessionHandler(), SpotifyHandler()

with open(pc.config["spotify"]["top_100_cover_image"], "rb") as img_file:
    image_str = base64.b64encode(img_file.read())

with sh.session_scope(pc.engine) as session:
    counts = sh.get_top_song_ids(session, 300)

song_ids = [song[0] for song in counts]

chunked_ids = [song_ids[_ : _ + 100] for _ in range(0, len(song_ids), 100)]

sp.update_playlist(
    pc.config["spotify"]["top_songs_playlist_id"], chunked_ids[0], image_str
)
sp.playlist_append(pc.config["spotify"]["top_songs_playlist_id"], chunked_ids[1], 100)
sp.playlist_append(pc.config["spotify"]["top_songs_playlist_id"], chunked_ids[2], 200)

pc.file_logger.info(
    f"Playlist: {pc.config['spotify']['top_songs_playlist_id']} updated."
)
