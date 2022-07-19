import base64
from sqlalchemy import cast, Date, func, select
from sqlalchemy.orm import sessionmaker

from .spotify import SpotifyHandler
from SpotifyHistory.config import Config
from SpotifyHistory.app.utils import playlist_query


c, sp = Config(), SpotifyHandler()
query_results = playlist_query()
with open(c.config["spotify"]["top_100_cover_image"], "rb") as img_file:
    image_str = base64.b64encode(img_file.read())
song_ids = [song[0] for song in query_results["top_songs"]]
chunked_ids = [song_ids[_ : _ + 100] for _ in range(0, len(song_ids), 100)]

sp.update_playlist(
    c.config["spotify"]["top_songs_playlist_id"], chunked_ids[0], image_str
)
sp.playlist_append(c.config["spotify"]["top_songs_playlist_id"], chunked_ids[1], 100)
sp.playlist_append(c.config["spotify"]["top_songs_playlist_id"], chunked_ids[2], 200)

c.file_logger.info(f"Playlist: {c.config['spotify']['top_songs_playlist_id']} updated.")
