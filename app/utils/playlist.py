import base64
from sqlalchemy import cast, Date, func, select
from sqlalchemy.orm import sessionmaker

from SpotifyHistory.config import Config
from .spotify import SpotifyHandler


# def playlist_driver() -> None:
"""Main function to update the top 100 songs playlist: updates track list and cover image"""
c, sp = Config(), SpotifyHandler()

with c.session_scope() as session:
    tuples = (
        session.query(c.models["SongStreamed"].song_id)
        .group_by(c.models["SongStreamed"].song_id)
        .order_by(func.count(c.models["SongStreamed"].song_id).desc())
        .limit(300)
        .all()
    )

with open(c.config["spotify"]["top_100_cover_image"], "rb") as img_file:
    image_str = base64.b64encode(img_file.read())

song_ids = [song[0] for song in tuples]

chunked_ids = [song_ids[_ : _ + 100] for _ in range(0, len(song_ids), 100)]

sp.update_playlist(
    c.config["spotify"]["top_songs_playlist_id"], chunked_ids[0], image_str
)
sp.playlist_append(c.config["spotify"]["top_songs_playlist_id"], chunked_ids[1], 100)
sp.playlist_append(c.config["spotify"]["top_songs_playlist_id"], chunked_ids[2], 200)

c.file_logger.info(f"Playlist: {c.config['spotify']['top_songs_playlist_id']} updated.")
