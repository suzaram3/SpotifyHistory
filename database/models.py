import datetime
from dataclasses import dataclass, asdict
from sqlalchemy import (
    Column,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    DateTime,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


@dataclass
class DictMixin:
    def as_dict(self):
        return asdict(self)


@dataclass
class Artist(Base, DictMixin):
    """Class to represent a record in the artists table"""

    __tablename__ = "artists"
    __table_args__ = {"schema": "music"}

    id: str = Column(
        String(32),
        primary_key=True,
        comment="Artist ID  example: `{6eUKZXaKkcviH0Ku9w2n3V}`",
    )
    name: str = Column(String(256), nullable=False, comment="Artist Name")


@dataclass
class ArtistGenre(Base, DictMixin):
    """Class to represent an artist genre"""
    __tablename__ = "artist_genres"
    __table_args__ = {"schema": "music"}

    artist_id: str = Column(
        String(32),
        primary_key=True,
        comment="Artist ID  example: `{6eUKZXaKkcviH0Ku9w2n3V}`",
    )
    genre: str = Column(
        String(64),
        primary_key=True,
        comment="Artist genre category",
    )


@dataclass
class Album(Base, DictMixin):
    """Class to represent a record in the albums table"""

    __tablename__ = "albums"
    __table_args__ = {"schema": "music"}

    id: str = Column(String(32), primary_key=True, unique=True, comment="Album ID")
    name: str = Column(String(256), nullable=False, comment="Album Name")
    release_year: str = Column(String(4), nullable=False, comment="Album release year")


@dataclass
class AlbumArtist(Base, DictMixin):
    """Class to represent a record in the albums table"""

    __tablename__ = "album_artists"
    __table_args__ = {"schema": "music"}

    album_id: str = Column(
        String(32),
        ForeignKey(Album.id, ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        nullable=False,
        comment="Album ID that references albums table",
    )
    artist_id: str = Column(
        String(32),
        ForeignKey(Artist.id, ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        nullable=False,
        comment="Artist ID that references artists table",
    )


@dataclass
class Song(Base, DictMixin):
    """Class to represent a record in the songs table"""

    __tablename__ = "songs"
    __table_args__ = ({"schema": "music"},)  # Define the schema for the table

    id: str = Column(String(32), primary_key=True, comment="Song ID")
    name: str = Column(String(256), nullable=False, comment="Song Name")
    album_id: str = Column(
        String(32),
        ForeignKey(Album.id, ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        comment="Album ID that references albums table",
    )
    length: int = Column(Integer, default=0)


@dataclass
class SongArtist(Base, DictMixin):
    """Class to represent a record in the song_artists table"""

    __tablename__ = "song_artists"
    __table_args__ = {"schema": "music"}

    song_id: str = Column(
        String(32),
        ForeignKey(Song.id, ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        comment="Song ID that references songs table",
    )
    artist_id: str = Column(
        String(256),
        ForeignKey(Artist.id, ondelete="CASCADE", onupdate="CASCADE"),
        primary_key=True,
        comment="Artist ID that references artists table",
    )


@dataclass
class SongStreamed(Base, DictMixin):
    """Class to represent a record in the streams table"""

    __tablename__ = "streams"
    __table_args__ = {"schema": "music"}

    song_id: str = Column(
        String(32),
        ForeignKey(Song.id),
        primary_key=True,
        comment="Song ID that refrences songs table",
    )
    played_at: datetime.datetime = Column(
        DateTime, primary_key=True, comment="Timestamp of when stream occured"
    )


@dataclass
class StreamHistory(Base, DictMixin):
    """Class to represent a record in the streams table"""

    __tablename__ = "stream_history"
    __table_args__ = {"schema": "music"}

    song_id: str = Column(
        String(32),
        primary_key=True,
        comment="Song ID that refrences songs table",
    )
    played_at: datetime.datetime = Column(
        DateTime, primary_key=True, comment="Timestamp of when stream occurred"
    )


@dataclass
class CurrentSong(DictMixin):
    song_id: str
    song_name: str
    song_url: str
    song_artist_id: str
    song_artist_name: str
    song_album_id: str
    song_album: str
