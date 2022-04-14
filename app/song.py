from datetime import date, datetime
from dataclasses import dataclass


@dataclass
class Song:
    song_name: str
    song_artist: str
    song_album: str
    album_release_date: date
    timestamp_played: datetime
