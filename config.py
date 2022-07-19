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
    file_logger = logging.getLogger("prod")
    qa_file_logger = logging.getLogger("qa")

    models = {
        "Album": Album,
        "Artist": Artist,
        "Song": Song,
        "SongStreamed": SongStreamed,
    }

    engine = create_engine(config["prod"]["db_uri"])

    @contextmanager
    def session_scope(self):
        Session = sessionmaker(Config.engine, expire_on_commit=False)
        session = Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            Config.file_logger.error("rollback transaction")
            Config.file_logger.error(f"{e}")
            raise
        finally:
            session.expunge_all()
            session.close()

#create(Config().engine)