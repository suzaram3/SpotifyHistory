import configparser
from configparser import ExtendedInterpolation
from contextlib import contextmanager
import logging
import logging.config
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from .models.models import Album, Artist, Song, SongStreamed, create


class Config:

    # conf files
    config = configparser.ConfigParser(interpolation=ExtendedInterpolation())
    config.read(
        [
            "/home/msuzara/SpotifyHistory/settings/db.conf",
            "/home/msuzara/SpotifyHistory/settings/file_paths.conf",
            "/home/msuzara/SpotifyHistory/settings/spotify.conf",
        ]
    )

    # logging setup
    logging.config.fileConfig("/home/msuzara/SpotifyHistory/settings/logging.conf")
    console_logger = logging.getLogger("console")
    file_logger = logging.getLogger("qa")

    engine = create_engine(config["prod"]["db_uri"])