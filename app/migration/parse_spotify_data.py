import json
# from SpotifyHistory.app.utils.queries import update

file_path = "/home/msuzara/music_data"

with open(f"{file_path}/endsong_0.json", "r") as in_file:
    spotify_data = json.load(in_file)

with open(f"{file_path}/endsong_1.json", "r") as in_file:
    spotify_data += json.load(in_file)

keys = [
    {
        "played_at": data["ts"],
        "song_id": data["spotify_track_uri"].split(":")[2],
    }
    for data in spotify_data
    if data["spotify_track_uri"] is not None
]

song_ids = set([record['song_id'] for record in keys])

print(f"{len(keys):,}")
print(f"{len(song_ids):,}")


# [print(len(spotify_data[0])) for _ in spotify_data]
# single track 4 chunks -> chunks of 50 -> single track
# print(spotify_data[0][0]['tracks'][0]['id'])
# print(spotify_data[0][0]['tracks'][0]['duration_ms'])

# for q in spotify_data:
#     for chunk in q:
#         for song in chunk["tracks"]:
#             update(song["id"], song["duration_ms"])
# print(f"{song['id']=}")
# print(f"{song['duration_ms']=}")
