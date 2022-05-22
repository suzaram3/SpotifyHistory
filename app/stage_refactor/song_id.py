"""
Author : Mitch Suzara <suzaram3@gmail.com>
Date   : 2022-04-14
Purpose: Main driver for ETL
"""
import csv
import json
import logging
import pprint
import sys
import time
from datetime import datetime, timedelta
from dataclasses import dataclass

from config import DevelopmentConfig
from utils.db import Database
from utils.extract import SearchSpotify
from utils.model import SongPlayed

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d %(message)s]",
    datefmt="%d-%m-%Y %H:%M:%S",
    level=logging.INFO,
    filename="/Users/msuzara/Library/Mobile Documents/com~apple~CloudDocs/cloud_workspace/python/SpotifyHistory/app/logs/song_id.log",
)

logger = logging.getLogger("etl")

d = DevelopmentConfig()
db = Database(d)
s = SearchSpotify(d)


@dataclass
class Song:
    song_id: str
    song_name: str
    artist_id: str
    artist_name: str
    album_id: str
    album_name: str
    album_release_year: str
    spotify_url: str

    def __str__(self):
        return f"{self.song_id=}\n{self.song_name=}\n{self.artist_id=}\n{self.artist_name=}\n{self.album_id=}\n{self.album_name=}\n{self.album_release_year=}\n{self.spotify_url=}\n"


def read_csv(file):
    with open(file, "r", newline="") as csvfile:
        csv_reader = csv.reader(csvfile, delimiter="|")
        next(csv_reader, None)
        return list(csv_reader)


def extract_info(song_id: str) -> str:
    return e.search_song_id(song_id)


def filter_current(current):
    return Song(
        song_id=current["item"]["id"],
        song_name=current["item"]["name"],
        artist_id=current["item"]["artists"][0]["id"],
        artist_name=current["item"]["artists"][0]["name"],
        album_id=current["item"]["album"]["id"],
        album_name=current["item"]["album"]["name"],
        album_release_year=current["item"]["album"]["release_date"][:4],
        spotify_url=current["item"]["external_urls"]["spotify"],
    )


def make_song_obj(result):
    return Song(
        song_id=result["id"],
        song_name=result["name"],
        artist_id=result["artists"][0]["id"],
        artist_name=result["artists"][0]["name"],
        album_id=result["album"]["id"],
        album_name=result["album"]["name"],
        album_release_year=result["album"]["release_date"][:4],
        spotify_url=result["external_urls"]["spotify"],
    )


def write_csv(file, song):
    with open(file, "a", newline="") as f:
        writer = csv.writer(f, delimiter="|")
        writer.writerow(
            [
                song.song_id,
                song.song_name,
                song.artist_id,
                song.artist_name,
                song.album_id,
                song.album_name,
                song.album_release_year,
                song.played_at,
                song.spotify_url,
            ]
        )


def one_time():
    out_file = "/Users/msuzara/Library/Mobile Documents/com~apple~CloudDocs/cloud_workspace/python/SpotifyHistory/app/tmp/master_song_data.csv"

    songs = db.query_song_ids()
    songs = [song[0] for song in songs]
    start = songs.index("5RyO8q8ZW60ISvdwSkLWME")

    i, j = start, 0
    for song in songs[start:]:
        if j >= 1000:
            j = 0
            time.sleep(10)
        print(f"iteration: {start}, song_id:{song}")
        result = s.search_id(song)
        song = make_song_obj(result)
        write_csv(out_file, song)
        start += 1
        j += 1


def usage():
    print(f"Usage: {sys.argv[0]} [song_id]")


def main() -> None:
    if len(sys.argv) < 2:
        result = filter_current(s.current_track())
        #query = db.row_update(result)
        print(f"Currentently Playing: {result}")

    else:
        result = s.search_id(sys.argv[1])
        print(make_song_obj(result))


if __name__ == "__main__":
    main()
