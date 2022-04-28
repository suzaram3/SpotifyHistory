from datetime import date, datetime
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Date

Base = declarative_base()


class Song(Base):
    __tablename__ = "songs_played"

    song_name = Column(String(128), nullable=False)
    song_artist = Column(String(128), nullable=False)
    song_album = Column(String(128), nullable=False)
    album_release_date = Column(Integer, nullable=False)
    timestamp_played = Column(DateTime, primary_key=True)

    def __repr__(self) -> str:
        return f"\n<Song: {self.song_name}, {self.song_artist}, {self.song_album}, {self.album_release_date}, {self.timestamp_played}"
