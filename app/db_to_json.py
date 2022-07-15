import json
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from config import DevelopmentConfig
from app.session import SessionHandler

dc, sh = DevelopmentConfig(), SessionHandler()
stmt = select(dc.models['song_streamed'])
Session = sessionmaker(bind=dc.engine)
session = Session()
streams = list(session.execute(stmt))
json_dict = [{
    "song_id": stream[0].song_id,
    "played_at": stream[0].played_at.__str__(),
} for stream in streams]
with open("/home/msuzara/music_data/streams.json", "w") as fo:
    json.dump(json_dict, fo, indent=4)

