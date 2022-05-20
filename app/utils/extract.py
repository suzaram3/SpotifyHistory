"""
Author : Mitch Suzara <suzaram3@gmail.com>
Date   : 2022-04-14
Purpose: Extract songs class 
"""
import logging
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from spotipy.oauth2 import SpotifyClientCredentials
from .model import SongPlayed

logger = logging.getLogger("etl.extract")


class ExtractSongs:
    def __init__(self, config, song_limit=50):
        self.config = config
        self.scope = "user-read-recently-played"
        self.sp = spotipy.Spotify(
            auth_manager=SpotifyOAuth(scope=self.scope, requests_timeout=10)
        )
        self.song_limit = song_limit

    def get_recently_played(self) -> list:
        results = self.sp.current_user_recently_played(limit=self.song_limit)
        tracks = results["items"]
        return [
            SongPlayed(
                song_id=item["track"]["id"],
                song_name=item["track"]["name"],
                artist_id=item["track"]["artists"][0]["id"],
                artist_name=item["track"]["artists"][0]["name"],
                album_id=item["track"]["album"]["id"],
                album_name=item["track"]["album"]["name"],
                album_release_year=item["track"]["album"]["release_date"][:4],
                played_at=item["played_at"][:19],
                spotify_url=item["track"]["external_urls"]["spotify"],
            )
            for item in tracks
        ]


class SearchSpotify:
    def __init__(self, config):
        self.config = config
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth())

    def search(self, song_list: list) -> list:
        new_songs_list = []
        try:
            for song in song_list:
                query = (
                    "track:"
                    + song.song_name.replace("'", "")
                    + " "
                    + "+artist:"
                    + song.song_artist
                )
                raw_data = self.sp.search(q=query, type="track")
                s = SongPlayed(
                    song_id=raw_data["tracks"]["items"][0]["id"],
                    song_name=song.song_name,
                    artist_id=raw_data["tracks"]["items"][0]["artists"][0]["id"],
                    artist_name=song.song_artist,
                    album_id=raw_data["tracks"]["items"][0]["album"]["id"],
                    album_name=song.song_album,
                    album_release_date=song.album_release_date,
                    played_at=song.timestamp_played,
                )
                new_songs_list.append(s)
        except IndexError:
            print(f"failure on query: {query}")
        return new_songs_list

    def search_single(self, song, artist) -> list:
        query = f"track:{song} +artist:{artist}"
        return self.sp.search(q=query, type="track")

    def search_id(self, song_id) -> str:
        return self.sp.track(song_id)

    def current_track(self) -> str:
        return self.sp.current_user_playing_track()


"""
Author : Mitch Suzara <suzaram3@gmail.com>
Date   : 2022-04-14
Purpose: Create playlist from top 100
"""


class MakePlaylist:
    def __init__(self, config, songs, scope="playlist-modify-private"):
        self.config = config
        self.scope = scope
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=self.scope))
        self.songs = songs
        self.playlist_name = "Top 100 Songs"
        self.description = "LarryDickman Top Live 100 Songs"

    def get_top_100_playlist(self) -> dict:
        playlists = self.sp.user_playlists(self.sp.me()["id"])
        print(f"{playlists=}")
        # for playlist in playlists['items']:
        #    print(playlist['name'])

    def create_top_100_playlist(self) -> bool:
        self.sp.user_playlist_create(
            self.sp.me()["id"],
            self.playlist_name,
            public=False,
            collaborative=False,
            description=self.description,
        )

    def update_100_playlist(self, playlist_id, songs) -> bool:

        self.sp.user_playlist_add_tracks(
            user=self.sp.me(), playlist_id=playlist["id"], tracks=songs
        )
