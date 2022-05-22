"""
Author : Mitch Suzara <suzaram3@gmail.com>
Date   : 2022-04-14
Purpose: Spotify handler for setting up Spotipy 
"""
import configparser, logging

import spotipy
from spotipy.oauth2 import SpotifyOAuth

config = configparser.ConfigParser()
config.read(
    "/Users/msuzara/Library/Mobile Documents/com~apple~CloudDocs/cloud_workspace/python/SpotifyHistory/spotify.conf"
)
credentials = dict(config.items("spotify"))


class SpotifyHandler:
    __instance = None

    def __init__(self) -> None:
        """Virtually private constructor"""

        if SpotifyHandler.__instance is not None:
            raise Exception("This class is a singleton")
        else:
            SpotifyHandler.__instance = self
            self.sp = spotipy.Spotify(
                auth_manager=SpotifyOAuth(
                    cache_path=credentials["cache_path"],
                    client_id=credentials["spotipy_client_id"],
                    client_secret=credentials["spotipy_client_secret"],
                    open_browser=False,
                    redirect_uri=credentials["redirect_uri"],
                    scope=credentials["scope"],
                )
            )

    def create_playlist(self, **kwargs):
        self.sp.user_playlist_create(**kwargs)

    def get_current_track(self):
        return self.sp.current_user_playing_track()

    def get_playlists(self):
        return self.sp.current_user_playlists()

    def get_recently_played(self) -> list:
        return self.sp.current_user_recently_played()

    def get_user(self) -> str:
        return self.sp.current_user()

    def update_playlist(self, *args):
        self.sp.playlist_replace_items(*args)
