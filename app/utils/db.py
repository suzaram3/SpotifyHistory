import logging
import os
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from .model import Base, Album, Artist, Song, SongPlayed


logger = logging.getLogger("etl.load")


class Database:
    def __init__(self, config):
        self.engine = create_engine(config.SQLALCHEMY_DATABASE_URI)
        Base.metadata.create_all(self.engine)

    # create session and add objects
    def insert_bulk(self, songs: list[Song]):
        with Session(self.engine) as session:
            try:
                session.add_all(songs)
                session.commit()
                logger.info(f"{len(songs)} rows added to database.")
            except SQLAlchemyError as e:
                logger.error(f"{e.__dict__['orig']}")
                session.rollback()

    def query_songs(self):
        logger.info("Get all songs query")
        with Session(self.engine) as session:
            query = session.query(Song).order_by(Song.timestamp_played.desc())
            songs = query.all()
        return songs

    def query_max_record(self):
        with Session(self.engine) as session:
            descending_query = session.query(Song).order_by(
                Song.timestamp_played.desc()
            )
            last_record = descending_query[0]
        return last_record
