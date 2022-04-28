"""
Author : Mitch Suzara <suzaram3@gmail.com>
Date   : 2022-04-14
Purpose: Extract songs class 
"""
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from .model import Song


class ExtractSongs:
    def __init__(self, config, song_limit=50, after_timestamp=None):
        self.config = config
        self.scope = "user-read-recently-played"
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=self.scope))
        self.song_limit = song_limit
        self.after_timestamp = after_timestamp

    def get_recently_played(self) -> list:
        results = self.sp.current_user_recently_played(
            limit=self.song_limit, after=self.after_timestamp
        )
        tracks = results["items"]
        return [
            Song(
                song_name=item["track"]["name"],
                song_artist=item["track"]["artists"][0]["name"],
                song_album=item["track"]["album"]["name"],
                album_release_date=item["track"]["album"]["release_date"][:4],
                timestamp_played=item["played_at"][:19],
            )
            for item in tracks
        ]
