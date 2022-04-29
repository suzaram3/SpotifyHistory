from datetime import date, datetime
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Date

Base = declarative_base()


class SongPlayed(Base):
    __tablename__ = "songs_played"

    song_id = Column(String(128), nullable=False)
    song_name = Column(String(128), nullable=False)
    artist_id = Column(String(128), nullable=False)
    artist_name = Column(String(128), nullable=False)
    album_id = Column(String(128), nullable=False)
    album_name = Column(String(128), nullable=False)
    album_release_date = Column(Integer, nullable=False)
    timestamp_played = Column(DateTime, primary_key=True)

    def __repr__(self) -> str:
        return f"<ExtractSong: song_id: {self.song_id}, song_name: {self.song_name}, artist_id: {self.artist_id}, artist_name: {self.artist_name}, album_id: {self.album_id}, album_name: {self.album_name}, album_release_date: {self.album_release_date}, timestamp_played: {self.timestamp_played}>\n"


class Artist(Base):
    __tablename__ = "artists"

    artist_id = Column(String(128), primary_key=True, nullable=False)
    artist_name = Column(String(128), nullable=False)

    def __repr__(self) -> str:
        return f"<Artist: {self.artist_name}, {artist_id}>"


class Album(Base):
    __tablename__ = "albums"

    album_id = Column(String(128), primary_key=True, nullable=False)
    album_name = Column(String(128), nullable=False)
    artist_id = Column(String(128), ForeignKey("artist.artist_id"))

    def __repr__(self) -> str:
        return f"<Album: {self.album_name}, {album_id}>"


class Song(Base):
    __tablename__ = "songs"

    song_id = Column(String(128), primary_key=True, nullable=False)
    song_name = Column(String(128), nullable=False)
    album_id = Column(String(128), ForeignKey("album.album_id"))
    artist_id = Column(String(128), ForeignKey("artist.artist_id"))

    def __repr__(self) -> str:
        return f"<Song: {self.song_name}, {song_id}>"
