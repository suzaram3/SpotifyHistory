from enum import unique
import json
from SpotifyHistory.models.models import Artist, Song
from SpotifyHistory.app.utils import queries as sql
from SpotifyHistory.app.etl.transform import TransformData
from SpotifyHistory.app.utils.spotify import SpotifyHandler
from models.models import Album


MAX_RECORDS = 50


def chunk_list(lst: list) -> list[list]:
    return [lst[i : i + MAX_RECORDS] for i in range(0, len(lst), MAX_RECORDS)]


def write_file(data: dict) -> None:
    with open(data["filename"], "w") as fp:
        json.dump(data["data"], fp, indent=2)


s, t = SpotifyHandler(), TransformData()
song_data = {
    "artists": {"model": Artist, "data": []},
    "albums": {"model": Album, "data": []},
    "songs": {"model": Song, "data": []},
}

print("Getting unique songs...\n")
unique_songs = sql.distinct_songs()
print("Chunking songs list...\n")
chunked_songs = chunk_list(unique_songs)

print("Requesting spotify song data...\n")
for chunk in chunked_songs:
    x = s.get_tracks_bulk(chunk)
    for song in x["tracks"]:
        song_data["artists"]["data"].append(
            Artist(
                id=song["artists"][0]["id"],
                name=song["artists"][0]["name"],
            )
        )
        song_data["albums"]["data"].append(
            Album(
                id=song["album"]["id"],
                name=song["album"]["name"],
                release_year=song["album"]["release_date"][:4],
                artist_id=song["artists"][0]["id"],
            )
        )
        song_data["songs"]["data"].append(
            Song(
                id=song["id"],
                name=song["name"],
                album_id=song["album"]["id"],
                artist_id=song["artists"][0]["id"],
                spotify_url=song["external_urls"]["spotify"],
                length=song["duration_ms"],
            )
        )


print("Inserting artist data...\n")
sql.add_artists(song_data["artists"])
print("Inserting album data...\n")
sql.add_albums(song_data["albums"])
print("Inserting song data...\n")
sql.add_songs(song_data["songs"])
