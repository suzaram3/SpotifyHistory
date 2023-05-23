from .spotify import SpotifyHandler
from SpotifyHistory.config import Config
from SpotifyHistory.app.utils.queries import random_songs

c, sp = Config(), SpotifyHandler()
data = random_songs()
sp.update_playlist(c.config["spotify"]["random_playlist"], data["song_ids"])
sp.update_playlist_details(c.config["spotify"]["random_playlist"], f"100 random songs last updated: {data['today']}")
c.file_logger.info(
    f"{c.config['spotify']['random_playlist']} random songs playlist updated"
)