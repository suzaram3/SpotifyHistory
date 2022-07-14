import configparser
import logging
import logging.config
from configparser import ConfigParser, ExtendedInterpolation
from db import DB


class Config:

    # conf files
    config = configparser.ConfigParser(interpolation=ExtendedInterpolation())
    config.read(
        [
            "/home/msuzara/SpotifyHistory/db.conf",
            "/home/msuzara/SpotifyHistory/settings.conf",
            "/home/msuzara/SpotifyHistory/spotify.conf",
        ]
    )

    # logging setup
    logging.config.fileConfig("/home/msuzara/SpotifyHistory/logging.conf")
    console_logger = logging.getLogger("console")


class DevelopmentConfig(Config):
    file_logger = logging.getLogger("qa")
    db = DB(Config.config["qa"]["db_uri"])
    engine = db.engine


class ProductionConfig(Config):
    file_logger = logging.getLogger("file")
    db = DB(Config.config["prod"]["db_uri"])
    engine = db.engine
