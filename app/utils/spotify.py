import spotipy
from spotipy.oauth2 import SpotifyOAuth
from SpotifyHistory.config import Config


c = Config()
credentials = dict(c.config["spotify"])


class SpotifyHandler:
    def __init__(self) -> None:
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                cache_path=credentials["cache_path"],
                client_id=credentials["client_id"],
                client_secret=credentials["client_secret"],
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

    def get_tracks_bulk(self, song_ids: list) -> dict:
        """Return bulk track data"""
        return self.sp.tracks(song_ids)

    def playlist_append(self, playlist_id: str, items: list, index: int) -> None:
        """Update playlist with tracks and cover image"""
        self.sp.playlist_add_items(playlist_id, items, index)

    def update_playlist(self, playlist_id: str, items: list, image: str = None) -> None:
        """Update playlist with tracks and cover image"""
        self.sp.playlist_replace_items(playlist_id, items)
        if image is not None:
            self.sp.playlist_upload_cover_image(playlist_id, image)

    def update_playlist_details(self, playlist_id: str, desc: str) -> None:
        self.sp.playlist_change_details(playlist_id=playlist_id, description=desc)
