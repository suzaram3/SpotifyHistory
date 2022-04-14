"""
Author : Mitch Suzara <suzaram3@gmail.com>
Date   : 2022-04-14
Purpose: Rock the Casbah
"""
import os
import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from song import Song

load_dotenv()

SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")

scope = "user-read-recently-played"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

results = sp.current_user_recently_played()
tracks = results["items"]

songs = [
    Song(
        item["track"]["name"],
        item["track"]["artists"][0]["name"],
        item["track"]["album"]["name"],
        item["track"]["album"]["release_date"],
        item["played_at"],
    )
    for item in tracks
]

for song in songs:
    print(f"{song=}\n")
