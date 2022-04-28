"""
Author : Mitch Suzara <suzaram3@gmail.com>
Date   : 2022-04-14
Purpose: Main driver for ETL
"""
import logging
import re
import time
from datetime import datetime, timedelta
from config import DevelopmentConfig
from utils.db import Database
from utils.extract import ExtractSongs

logging.basicConfig(
    format="%(asctime)s %(levelname)-8s [%(filename)s:%(lineno)d %(message)s]",
    datefmt="%d-%m-%Y %H:%M:%S",
    level=logging.INFO,
    filename="/Users/msuzara/Library/Mobile Documents/com~apple~CloudDocs/cloud_workspace/python/etl_practice/app/logs/logs.log",
)

logger = logging.getLogger("etl")  # singleton pattern


def main() -> None:
    config = DevelopmentConfig()
    db = Database(config)
    e = ExtractSongs(config)
    get_recent_songs = e.get_recently_played()

    last_row = db.query_max_record()
    last_row_pk = last_row.timestamp_played

    #first_song = get_recent_songs[0]
    #strdate = first_song.timestamp_played 
    #datetimeobj = datetime.strptime(strdate, "%Y-%m-%dT%H:%M:%S.%fZ")
    #print(f"{datetimeobj=}")

    get_recent_timestamps = [datetime.strptime(song.timestamp_played, "%Y-%m-%dT%H:%M:%S.%fZ") for song in get_recent_songs]
    index = get_recent_timestamps.index(last_row_pk)
    if index > 0:
        db.insert_bulk(get_recent_songs[:index])
    else:
        db.insert_bulk(get_recent_songs)

if __name__ == "__main__":
    main()
