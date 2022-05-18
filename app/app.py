"""
Author : Mitch Suzara <suzaram3@gmail.com>
Date   : 2022-04-14
Purpose: Main driver for ETL
"""
import logging
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

logger = logging.getLogger("etl")


def main() -> None:
    # setup
    index = None
    config = DevelopmentConfig()
    db = Database(config)
    e = ExtractSongs(config)

    # extract/transform recent songs
    get_recent_songs = e.get_recently_played()
    unique = list(set(get_recent_songs))
    get_recent_songs = unique

    # get last added record
    last_row = db.query_max_record()
    last_row_pk = last_row.played_at

    # make list of timestamps
    get_recent_timestamps = [
        datetime.strptime(song.played_at, "%Y-%m-%dT%H:%M:%S")
        for song in get_recent_songs
    ]

    # check if last row exists in most recent songs
    try:
        index = get_recent_timestamps.index(last_row_pk)
    except ValueError:
        logger.info(f"`last_row_pk` not found in `get_recent_songs`")

    # load songs into database
    if index is not None:
        db.insert_bulk(get_recent_songs[:index])
    else:
        db.insert_bulk(get_recent_songs)


if __name__ == "__main__":
    main()
