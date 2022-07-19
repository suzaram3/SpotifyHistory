import datetime
from dataclasses import dataclass
from email.policy import default
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.exc import OperationalError

Base = declarative_base()


@dataclass
class Artist(Base):
    """Class to represent a record in the artists table"""

    __tablename__ = "artists"

    id: str = Column(String(32), primary_key=True)
    name: str = Column(String(256), nullable=False)

    __table_args__ = {"schema": "music"}


@dataclass
class Album(Base):
    """Class to represent a record in the albums table"""

    __tablename__ = "albums"

    id: str = Column(String(32), primary_key=True)
    name: str = Column(String(256), nullable=False)
    release_year: str = Column(String(4), nullable=False)
    artist_id: str = Column(
        String(32), ForeignKey(Artist.id, ondelete="CASCADE"), nullable=False
    )

    __table_args__ = {"schema": "music"}


@dataclass
class Song(Base):
    """Class to represent a record in the songs table"""

    __tablename__ = "songs"

    id: str = Column(String(32), primary_key=True)
    name: str = Column(String(256), nullable=False)
    album_id: str = Column(
        String(32), ForeignKey(Album.id, ondelete="CASCADE"), nullable=False
    )
    artist_id: str = Column(
        String(32), ForeignKey(Artist.id, ondelete="CASCADE"), nullable=False
    )
    spotify_url: str = Column(String(64), nullable=False)
    length: int = Column(Integer, default=0)

    __table_args__ = {"schema": "music"}


@dataclass
class SongStreamed(Base):
    """Class to represent a record in the streams table"""

    __tablename__ = "streams"

    song_id: str = Column(String(32), ForeignKey(Song.id), primary_key=True)
    played_at: datetime.datetime = Column(DateTime, primary_key=True)

    __table_args__ = {"schema": "music"}


# @dataclass
# class Token(Base):
#     """Class to represent a record in the streams table"""

#     __tablename__ = "token"

#     id: int = Column(Integer, primary_key=True)
#     token_type: str = Column(String(16), nullable=False)
#     access_token: str = Column(String(256), nullable=False)
#     refresh_token: str = Column(String(256), nullable=False)
#     expires_in: int = Column(Integer, nullable=False)
#     scope: str = Column(String(256))


#     __table_args__ = {"schema": "config"}


# create table if it does not exist, if you change the model,
# you have to drop the table first for this code to alter it in the db
def create(engine: str) -> None:
    try:
        Base.metadata.create_all(engine)
    except OperationalError as error:
        print(f"ERROR: {error}")