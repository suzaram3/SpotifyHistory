import datetime
from dataclasses import dataclass
from sqlalchemy import Column, Integer, String, DateTime, UniqueConstraint, func
from sqlalchemy.ext.declarative import declarative_base
from db import DB

db = DB.create()
engine = db.engine
Base = declarative_base()


@dataclass
class SongPlayed(Base):
    __tablename__ = "extract"

    song_id: str = Column(String(256), nullable=False)
    song_name: str = Column(String(256), nullable=False)
    artist_id: str = Column(String(256), nullable=False)
    artist_name: str = Column(String(256), nullable=False)
    album_id: str = Column(String(256), nullable=False)
    album_name: str = Column(String(256), nullable=False)
    album_release_year: str = Column(String(4), nullable=False)
    played_at: datetime.datetime = Column(DateTime, primary_key=True)
    spotify_url: str = Column(String(256), nullable=False)

    __table_args__ = {"schema": "music"}

    def __repr__(self) -> str:
        return f"<ExtractSong: song_id: {self.song_id}, song_name: {self.song_name}, artist_id: {self.artist_id}, artist_name: {self.artist_name}, album_id: {self.album_id}, album_name: {self.album_name}, album_release_date: {self.album_release_year}, played_at: {self.played_at}, url: {self.spotify_url}>\n"


@dataclass
class AlbumSong(Base):
    __tablename__ = "album_songs"

    song_number: int = Column(Integer, primary_key=True)
    song_id: str = Column(String(256), primary_key=True)
    song_name: str = Column(String(256), nullable=False)
    song_length: int = Column(Integer, nullable=False)
    album_id: str = Column(String(256), primary_key=True)
    album_name: str = Column(String(256), nullable=False)
    artist_id: str = Column(String(256), primary_key=True)
    artist_name: str = Column(String(256), nullable=False)

    __table_args__ = {"schema": "music"}

    def __repr__(self) -> str:
        return f"<AlbumSong: song_number: {self.song_number},\
            song_id: {self.song_id}, song_name: {self.song_name},\
            song_length: {self.song_length}, artist_id: {self.artist_id},\
            album_id: {self.album_id}, album_name: {self.album_name},\
            artist_name: {self.artist_name},\n"


@dataclass
class Albums(Base):
    __tablename__ = "master_albums"

    album_id: str = Column(String(256), primary_key=True)
    album_name: str = Column(String(256), nullable=False)
    album_release_year: str = Column(String(256), nullable=False)
    artist_id: str = Column(String(256), primary_key=True)
    artist_name: str = Column(String(256), nullable=False)

    __table_args__ = {"schema": "music"}


# create table if it does not exist, if you change the model,
# you have to drop the table first for this code to alter it in the db
Base.metadata.create_all(engine)
