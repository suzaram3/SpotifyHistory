from models import SongPlayed, TestSongPlayed
from spotify import SpotifyHandler


class ExtractData:
    __instance = None

    def __init__(self, scope="user-read-recently-played") -> None:
        """Virtually private constructor"""

        if ExtractData.__instance is not None:
            raise Exception("This class is a singleton")
        else:
            ExtractData.__instance = self
            self.spotify = SpotifyHandler()

    def extract(self):
        return self.spotify.get_recently_played()
