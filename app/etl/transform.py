class TransformData:
    def transform_data(self, raw_track_data=list) -> dict:
        """Return dict of desired json data"""
        return {
            "song_id": raw_track_data["track"]["id"],
            "song_name": raw_track_data["track"]["name"],
            "song_length": raw_track_data["track"]["duration_ms"],
            "artist_id": raw_track_data["track"]["artists"][0]["id"],
            "artist_name": raw_track_data["track"]["artists"][0]["name"],
            "album_id": raw_track_data["track"]["album"]["id"],
            "album_name": raw_track_data["track"]["album"]["name"],
            "album_release_year": raw_track_data["track"]["album"]["release_date"][:4],
            "played_at": raw_track_data["played_at"][:19],
            "spotify_url": raw_track_data["track"]["external_urls"]["spotify"],
        }

    def compile_model_lists(self, data_list: list) -> list:
        return (
            [
                {
                    "id": record["album_id"],
                    "name": record["album_name"],
                    "release_year": record["album_release_year"],
                    "artist_id": record["artist_id"],
                }
                for record in data_list
            ],
            [
                {
                    "id": record["artist_id"],
                    "name": record["artist_name"],
                }
                for record in data_list
            ],
            [
                {
                    "id": record["song_id"],
                    "name": record["song_name"],
                    "album_id": record["album_id"],
                    "artist_id": record["artist_id"],
                    "spotify_url": record["spotify_url"],
                    "length": record["song_length"],
                }
                for record in data_list
            ],
            [
                {"song_id": record["song_id"], "played_at": record["played_at"]}
                for record in data_list
            ],
        )
