from .spotify import SpotifyHandler
from SpotifyHistory.config import Config
from SpotifyHistory.app.utils.queries import yesterday_top_ten

c, sp = Config(), SpotifyHandler()
data = yesterday_top_ten()
sp.update_playlist(c.config["spotify"]["yesterday_top_10_id"], data["song_ids"])
sp.update_playlist_details(c.config["spotify"]["yesterday_top_10_id"], data["desc"])
c.file_logger.info(F"{c.config['spotify']['yesterday_top_10_id']} top ten playlist updated")