import json, logging, logging.config, requests, time

from dataclasses import asdict
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import sessionmaker
from session import SessionHandler

from db import DB
from models import AlbumSong, SongPlayed, Albums
from spotify import SpotifyHandler

logging.config.fileConfig(
    "/Users/msuzara/Library/Mobile Documents/com~apple~CloudDocs/cloud_workspace/python/SpotifyHistory/logging.conf"
)
extract_logger = logging.getLogger("extract")
console_logger = logging.getLogger("console")
db = DB.create()
engine = db.engine
Session = sessionmaker(bind=engine)
session = Session()
user_session = SessionHandler.create(session, AlbumSong)
spotify = SpotifyHandler()


def add_many(model, record_list):
    return session.add_all([model(**record_dict) for record_dict in record_list])
    # session.commit()


def extract(album_id: str) -> dict:
    return spotify.get_album(album_id)


def insert_many(record_list, model=AlbumSong):
    statements = [
        insert(model).values(record_dict).on_conflict_do_nothing()
        for record_dict in record_list
    ]
    return [session.execute(statement) for statement in statements]


def transform_data(data: dict) -> dict:
    song_list = data["tracks"]["items"]
    base_info = {
        "artist_id": data["artists"][0]["id"],
        "artist_name": data["artists"][0]["name"],
        "album_id": data["id"],
        "album_name": data["name"],
    }
    song_data = [
        {
            "song_length": song["duration_ms"],
            "song_id": song["id"],
            "song_name": song["name"],
            "song_number": song["track_number"],
        }
        for song in song_list
    ]
    return [{**base_info, **song} for song in song_data]


def get_albums(model) -> list[SongPlayed]:
    results = session.query(model).all()
    return [asdict(result) for result in results]


file = {
    "in_file": "/Users/msuzara/Library/Mobile Documents/com~apple~CloudDocs/cloud_workspace/python/SpotifyHistory/app/album.json",
}
# album_json = read_json(**file)
# console_logger.info(album_json)


def album_data() -> None:

    albums = get_albums(Albums)
    album_list = []

    i, j = 0, 0
    for album in albums:
        if j > 1000:
            time.sleep(5)
            j = 0
        console_logger.info(
            f"Getting album info on {album['album_id']}, albums to go:{len(albums) - i}, iteration{i}"
        )
        try:
            result = extract(album["album_id"])
        except requests.exceptions.ReadTimeout as e:
            extract_logger.info(e)
        td = transform_data(result)
        album_list.append(td)
        i += 1
        j += 1
    print(f"{(album_list[0])=}")
    with open("../data/albumsongs.json", "w") as fp:
        json.dump(album_list, fp)


def load_data():
    with open("../data/albumsongs.json", "r") as fp:
        data = json.load(fp)
        try:
            insert_many(data)
            session.commit()
        except Exception as e:
            session.rollback()
            console_logger.info(e)
            # raise e
        finally:
            session.close()


load_data()


# data_to_insert = transorm_data(album_json)
# result = add_many(AlbumSong, data_to_insert)
# console_logger.info(result)
