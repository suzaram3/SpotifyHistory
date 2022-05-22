"""
Author : Mitch Suzara <suzaram3@gmail.com>
Date   : 2022-04-14
Purpose: Main driver for ETL
"""
import csv
import logging
import time
from datetime import datetime, timedelta
from config import DevelopmentConfig
from utils.db import Database
from utils.extract import SearchSpotify
from utils.model import SongPlayed

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d %(message)s]",
    datefmt="%d-%m-%Y %H:%M:%S",
    level=logging.INFO,
    filename="/Users/msuzara/Library/Mobile Documents/com~apple~CloudDocs/cloud_workspace/python/etl_practice/app/logs/search.log",
)

logger = logging.getLogger("etl")

d = DevelopmentConfig()
e = SearchSpotify(d)


def read_csv(file):
    with open(file, "r", newline="") as csvfile:
        csv_reader = csv.reader(csvfile, delimiter="|")
        next(csv_reader, None)
        return list(csv_reader)


def extract_info(song):
    return e.search_single(song[1], song[2])


def make_song_obj(song, result):
    return SongPlayed(
        song_id=result["tracks"]["items"][0]["id"],
        song_name=song[1],
        artist_id=result["tracks"]["items"][0]["artists"][0]["id"],
        artist_name=song[2],
        album_id=result["tracks"]["items"][0]["album"]["id"],
        album_name=result["tracks"]["items"][0]["album"]["name"],
        album_release_year=result["tracks"]["items"][0]["album"]["release_date"][:4],
        played_at=song[0],
        spotify_url=result["tracks"]["items"][0]["external_urls"]["spotify"],
    )


def write_csv(file, song):
    header = [
        "song_id",
        "song_name",
        "artist_id",
        "artist_name",
        "album_id",
        "album_name",
        "album_release_year",
        "played_at",
        "spotify_url",
    ]
    with open(file, "a", newline="") as f:
        writer = csv.writer(f, delimiter="|")
        # writer.writerow(header)
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


def main() -> None:
    # setup
    in_file = "/Users/msuzara/Library/Mobile Documents/com~apple~CloudDocs/cloud_workspace/python/etl_practice/app/tmp/data.csv"
    out_file = "/Users/msuzara/Library/Mobile Documents/com~apple~CloudDocs/cloud_workspace/python/etl_practice/app/tmp/master_song_data.csv"

    rows = read_csv(in_file)
    master_song_list = []

    i = 0
    j = 0
    for song in rows:
        if j > 1000:
            j = 0
            time.sleep(10)
        print(f"iteration: {i}, song:{song}\n")
        data = extract_info(song)
        if data["tracks"]["items"]:
            write_csv(out_file, make_song_obj(song, data))
        else:
            logger.info(f"no data found for {song}")
        # write_csv(out_file, row)
        i += 1
        j += 1


if __name__ == "__main__":
    main()
