from spotify import SpotifyHandler


def parse_result(data: dict) -> dict:
    """Parse dict for desired data from raw data input"""
    return {
        "song_id": data["item"]["id"],
        "song_name": data["item"]["name"],
        "artist_id": data["item"]["artists"][0]["id"],
        "artist_id": data["item"]["artists"][0]["name"],
        "album_id": data["item"]["album"]["id"],
        "album_name": data["item"]["album"]["name"],
        "album_release_year": data["item"]["album"]["release_date"][:4],
        "spotify_url": data["item"]["external_urls"]["spotify"],
    }


def current_song() -> None:
    """Main function to get currently playing song from Spotify"""

    spotify = SpotifyHandler()

    raw_data = spotify.get_current_track()

    print(f"CurrentSong:{parse_result(raw_data)=}")


if __name__ == "__main__":
    current_song()
