import configparser
from configparser import ExtendedInterpolation
import logging
import logging.config
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine

from models.models import Album, Artist, Song, SongStreamed


class Config:

    # conf files
    config = configparser.ConfigParser(interpolation=ExtendedInterpolation())
    config.read(
        [
            "/home/msuzara/SpotifyHistory/settings/db.conf",
            "/home/msuzara/SpotifyHistory/settings/settings.conf",
            "/home/msuzara/SpotifyHistory/settings/spotify.conf",
        ]
    )

    # logging setup
    logging.config.fileConfig("/home/msuzara/SpotifyHistory/settings/logging.conf")
    console_logger = logging.getLogger("console")
    file_logger = logging.getLogger("qa")

    models = {
        "Album": Album,
        "Artist": Artist,
        "Song": Song,
        "SongStreamed": SongStreamed,
    }


engine = create_engine(Config.config["prod"]["db_uri"])
Session = sessionmaker(bind=engine)
