from datetime import date, datetime
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Date

Base = declarative_base()


class SongPlayed(Base):
    __tablename__ = "extract"

    song_id = Column(String(256), nullable=False)
    song_name = Column(String(256), nullable=False)
    artist_id = Column(String(256), nullable=False)
    artist_name = Column(String(256), nullable=False)
    album_id = Column(String(256), nullable=False)
    album_name = Column(String(256), nullable=False)
    album_release_year = Column(String(4), nullable=False)
    played_at = Column(DateTime, primary_key=True)
    spotify_url = Column(String(256), nullable=False)

    __table_args__ = {"schema": "music"}

    def __repr__(self) -> str:
        return f"<ExtractSong: song_id: {self.song_id}, song_name: {self.song_name}, artist_id: {self.artist_id}, artist_name: {self.artist_name}, album_id: {self.album_id}, album_name: {self.album_name}, album_release_date: {self.album_release_year}, timestamp_played: {self.played_at}, url: {self.spotify_url}>\n"
