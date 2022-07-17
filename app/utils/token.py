import spotipy
from spotipy.cache_handler import CacheFileHandler
from SpotifyHistory.config import Config


ch = CacheFileHandler(
    cache_path="/home/msuzara/.spotify_history_token", username="larrydickman"
)

token = ch.get_cached_token()
print(f"{token=}")
