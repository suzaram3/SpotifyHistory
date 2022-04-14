"""
Author : Mitch Suzara <suzaram3@gmail.com>
Date   : 2022-04-14
Purpose: Extract songs class 
"""
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import Config
from app.song import Song


class ExtractSongs:
    def __init__(self):
        self.config = Config()
        self.scope = "user-read-recently-played"
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=self.scope))

    def get_recently_played(self) -> list:
        results = self.sp.current_user_recently_played()
        print()
        tracks = results = ["items"]
        return [
            Song(
                item["track"]["name"],
                item["track"]["artists"][0]["name"],
                item["track"]["album"]["name"],
                item["track"]["album"]["release_date"],
                item["played_at"],
            )
            for item in tracks
        ]


if __name__ == "__main__":
    e = ExtractSongs()
    print(e.get_recently_played())
