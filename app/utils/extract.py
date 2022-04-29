"""
Author : Mitch Suzara <suzaram3@gmail.com>
Date   : 2022-04-14
Purpose: Extract songs class 
"""
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from .model import SongPlayed


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
            SongPlayed(
                song_id=item["track"]["id"],
                song_name=item["track"]["name"],
                artist_id=item["track"]["artists"][0]["id"],
                artist_name=item["track"]["artists"][0]["name"],
                album_id=item["track"]["album"]["id"],
                album_name=item["track"]["album"]["name"],
                album_release_date=item["track"]["album"]["release_date"][:4],
                timestamp_played=item["played_at"][:19],
            )
            for item in tracks
        ]
