import configparser
from configparser import ExtendedInterpolation
import logging
import logging.config


class Config:

    # conf files
    config = configparser.ConfigParser(interpolation=ExtendedInterpolation())
    config.read(
        [
            "/root/SpotifyHistory/settings/db.conf",
            "/root/SpotifyHistory/settings/file_paths.conf",
            "/root/SpotifyHistory/settings/spotify.conf",
        ]
    )

    # logging setup
    logging.config.fileConfig("/root/SpotifyHistory/settings/logging.conf")
    console_logger = logging.getLogger("console")
    file_logger = logging.getLogger("prod")
