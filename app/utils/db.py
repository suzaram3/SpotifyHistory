import logging
import os
from datetime import datetime
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from .model import Base, SongPlayed


logger = logging.getLogger("SpotifyHistory")


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

    def query_song_ids(self):
        with Session(self.engine) as session:
            query = session.query(SongPlayed.song_id).distinct(SongPlayed.song_id)
            song_ids = query.all()
        return song_ids

    def row_update(self, song):
        with Session(self.engine) as session:
            try:
                query = (
                    session.query(SongPlayed)
                    .filter(
                        SongPlayed.song_name == song.song_name,
                        SongPlayed.artist_name == song.artist_name,
                    )
                    .update(
                        {
                            SongPlayed.song_id: song.song_id,
                            SongPlayed.artist_id: song.artist_id,
                            SongPlayed.album_id: song.album_id,
                            SongPlayed.album_name: song.album_name,
                            SongPlayed.album_release_year: song.album_release_year,
                            SongPlayed.spotify_url: song.spotify_url,
                        },
                        synchronize_session=False,
                    )
                )
                session.commit()
                logger.info(
                    f"{query} rows updated on table {SongPlayed.__tablename__}."
                )
            except SQLAlchemyError as e:
                logger.error(f"{e.__dict__['orig']}")
                session.rollback()
        print(f"{query=}")
