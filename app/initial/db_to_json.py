import json
from sqlalchemy import select
from sqlalchemy.orm import sessionmaker
from SpotifyHistory.config import Config


c = Config()
with c.session_scope() as session:
    streams = session.query(c.models["SongStreamed"]).all()
    json_dict = [
        {
            "song_id": stream[0].song_id,
            "played_at": stream[0].played_at.__str__(),
        }
        for stream in streams
    ]

with open("/home/msuzara/music_data/streams.json", "w") as fo:
    json.dump(json_dict, fo, indent=4)
