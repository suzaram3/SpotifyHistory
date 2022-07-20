from .spotify import SpotifyHandler


spotify = SpotifyHandler()
data = spotify.get_current_track()
if data['is_playing']:
    song_dict = {
        "song_id": data["item"]["id"],
        "song_name": data["item"]["name"],
        "artist_id": data["item"]["artists"][0]["id"],
        "artist_name": data["item"]["artists"][0]["name"],
        "album_id": data["item"]["album"]["id"],
        "album_name": data["item"]["album"]["name"],
        "album_release_year": data["item"]["album"]["release_date"][:4],
        "spotify_url": data["item"]["external_urls"]["spotify"],
    }
    print(f"\nCurrent_Song:")
    [print(f"{k} : {v}") for k, v in song_dict.items()]
    print()
else:
    print("Current_Song: None")