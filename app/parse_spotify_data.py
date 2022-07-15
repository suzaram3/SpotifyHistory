import json
from .. app.spotify import SpotifyHandler

def request_track_data(list_chunk) -> dict:
    return SpotifyHandler().get_tracks(list_chunk)

with open("/home/msuzara/music_data/streams.json", "r") as in_file:
    spotify_history_json = json.load(in_file)

spotify_history_list = list(spotify_history_json)
unique_song_ids = list(set([record['song_id'] for record in spotify_history_list]))
chunked_song_ids = [unique_song_ids[i:i+50] for i in range(0, len(unique_song_ids), 50)]
pool_chunks = [unique_song_ids[i:i+50] for i in range(0, len(unique_song_ids), 50)]




print(F"{len(unique_song_ids)=}")
print(F"{len(unique_song_ids)//50=}")
print(F"{len(chunked_song_ids)=}")


