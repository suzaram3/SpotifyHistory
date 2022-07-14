"""
Author : Mitch Suzara <suzaram3@gmail.com>
Date   : 2022-04-14
Purpose: Spotify handler for setting up Spotipy 
"""
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from config import Config


c = Config()
credentials = dict(c.config["spotify"])


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
                ),
                requests_timeout=10,
                retries=5,
            )

    def create_playlist(
        self, user: str, name: str, public: bool = True, description: str = ""
    ) -> None:
        """Create new playlist wrapper"""
        self.sp.user_playlist_create(user, name, public, description)

    def get_album(self, album_id: str) -> dict:
        """Return dict info from album id"""
        return self.sp.album(album_id)

    def get_current_track(self) -> dict:
        """Return dict of current playing song"""
        return self.sp.current_user_playing_track()

    def get_playlists(self) -> dict:
        """Return dict of user profile playlists"""
        return self.sp.current_user_playlists()

    def get_recently_played(self) -> dict:
        """Return dict of user recently played songs"""
        return self.sp.current_user_recently_played()

    def get_user(self) -> dict:
        """Return dict of user profile"""
        return self.sp.current_user()

    def get_genre_seeds(self) -> list:
        """Return a list of genre seeds"""
        return self.sp.recommendation_genre_seeds()

    def get_recommendations(self, artists: list, genres: list, tracks: list) -> list:
        """Return a list of recommendations base of artist, track, and genre seed"""
        return self.sp.recommendations(
            seed_artists=artists, seed_genres=genres, seed_tracks=tracks, limit=100
        )

    def get_track(self, track_id: str) -> dict:
        """Return track data"""
        return self.sp.track(track_id)

    def playlist_append(self, playlist_id: str, items: list, index: int) -> None:
        """Update playlist with tracks and cover image"""
        self.sp.playlist_add_items(playlist_id, items, index)

    def update_playlist(self, playlist_id: str, items: list, image: str = None) -> None:
        """Update playlist with tracks and cover image"""
        self.sp.playlist_replace_items(playlist_id, items)
        if image is not None:
            self.sp.playlist_upload_cover_image(playlist_id, image)
