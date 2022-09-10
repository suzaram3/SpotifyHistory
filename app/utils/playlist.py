import base64
from .spotify import SpotifyHandler
from SpotifyHistory.config import Config
from SpotifyHistory.app.utils.queries import playlist


c, sp = Config(), SpotifyHandler()
query_results = playlist()
with open(c.config["spotify"]["top_100_cover_image"], "rb") as img_file:
    image_str = base64.b64encode(img_file.read())

sp.update_playlist(
    c.config["spotify"]["top_songs_playlist_id"], query_results, image_str
)
c.file_logger.info(
    f"Top 100 playlist: {c.config['spotify']['top_songs_playlist_id']} updated."
)
