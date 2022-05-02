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

    def insert_bulk(self, data_list: list):
        if data_list:
            with Session(self.engine) as session:
                try:
                    session.add_all(data_list)
                    session.commit()
                    logger.info(
                        f"{len(data_list)} rows added to table {data_list[0].__tablename__}."
                    )
                except SQLAlchemyError as e:
                    logger.error(f"{e.__dict__['orig']}")
                    session.rollback()

    def query_extract(self):
        with Session(self.engine) as session:
            query = session.query(SongPlayed).order_by(SongPlayed.played_at.desc())
            songs = query.all()
        return songs

    def query_max_record(self):
        with Session(self.engine) as session:
            descending_query = session.query(SongPlayed).order_by(
                SongPlayed.played_at.desc()
            )
            last_record = descending_query[0]
        return last_record

    def query_artists(self):
        with Session(self.engine) as session:
            query = session.query(SongPlayed).distinct(SongPlayed.artist_id)
            artist_ids = query.all()
        return artist_ids
