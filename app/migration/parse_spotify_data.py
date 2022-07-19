import json
from SpotifyHistory.app.utils.queries import update


with open("/home/msuzara/music_data/response.json", "r") as in_file:
    spotify_data = json.load(in_file)

# [print(len(spotify_data[0])) for _ in spotify_data]
# single track 4 chunks -> chunks of 50 -> single track
# print(spotify_data[0][0]['tracks'][0]['id'])
# print(spotify_data[0][0]['tracks'][0]['duration_ms'])

for q in spotify_data:
    for chunk in q:
        for song in chunk["tracks"]:
            update(song["id"], song["duration_ms"])
            # print(f"{song['id']=}")
            # print(f"{song['duration_ms']=}")
