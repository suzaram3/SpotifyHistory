class TransformData:
    __instance = None

    def __init__(self, scope="user-read-recently-played") -> None:
        """Virtually private constructor"""

        if TransformData.__instance is not None:
            raise Exception("This class is a singleton")
        else:
            TransformData.__instance = self

    def transform_data(self, raw_track_data: list) -> dict:
        """Return dict of desired json data"""
        return {
            "song_id": raw_track_data["track"]["id"],
            "song_name": raw_track_data["track"]["name"],
            "artist_id": raw_track_data["track"]["artists"][0]["id"],
            "artist_name": raw_track_data["track"]["artists"][0]["name"],
            "album_id": raw_track_data["track"]["album"]["id"],
            "album_name": raw_track_data["track"]["album"]["name"],
            "album_release_year": raw_track_data["track"]["album"]["release_date"][:4],
            "played_at": raw_track_data["played_at"][:19],
            "spotify_url": raw_track_data["track"]["external_urls"]["spotify"],
        }
