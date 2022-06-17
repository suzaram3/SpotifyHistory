import json, logging, logging.config, os, time

from sqlalchemy.orm import sessionmaker
from session import SessionHandler

from db import DB
from models import SongPlayed, SongPlayedMaster
from spotify import SpotifyHandler

logging.config.fileConfig(
    "/Users/msuzara/Library/Mobile Documents/com~apple~CloudDocs/cloud_workspace/python/SpotifyHistory/logging.conf"
)
file_logger = logging.getLogger("file")
console_logger = logging.getLogger("console")


def parse_json(filename: str):
    with open(filename, "r") as file:
        return json.load(file)


def compile_json(file_list: list) -> list:
    data = []
    for file in file_list:
        data += parse_json(file)
    return data


def transform_json(data_list: list) -> list:
    return [
        {"song_id": row["spotify_track_uri"].split(":")[2], "played_at": row["ts"][:19]}
        for row in data
        if row["spotify_track_uri"] is not None
    ]


def insert(record_list: list, user_session, session) -> None:
    try:
        user_session.insert_many(test_stuff)
        session.commit()
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()


def query_null_items() -> list:
    user_session = SessionHandler.create(session, SongsStreamed)
    return list(session.query(SongStreamed).all())


def transform(data: dict) -> dict:
    return {
        "song_id": data["id"],
        "song_name": data["name"],
        "artist_id": data["artists"][0]["id"],
        "artist_name": data["artists"][0]["name"],
        "album_id": data["album"]["id"],
        "album_name": data["album"]["name"],
        "album_release_year": data["album"]["release_date"][:4],
        "spotify_url": data["external_urls"]["spotify"],
    }


def main():

    db = DB.create()
    engine = db.engine
    Session = sessionmaker(bind=engine)
    session = Session()
    spotify = SpotifyHandler()

    results = list(
        session.query(SongPlayedMaster)
        .distinct(SongPlayedMaster.song_id)
        .filter(SongPlayedMaster.song_name == None)
        .all()
    )

    i, j = 0, 0
    for result in results:
        if j >= 1000:
            time.sleep(5)
            j = 0
        console_logger.info(
            f"fetching:{result.song_id}|iter:{i}|remaining{len(results)-i}"
        )
        request = spotify.get_track(result.song_id)
        session.query(SongPlayedMaster).filter(
            SongPlayedMaster.song_id == result.song_id
        ).update(transform(request))
        session.commit()
        i += 1
        j += 1

    # with open('outlist.json', 'w') as outfile:
    #    json.dump(new_list, outfile)

    # test_get_track = spotify.get_track(test_track.song_id)
    # test_transform = transform(test_get_track)
    # print(f"{test_transform=}")

    # update_test = session.query(SongPlayedMaster).filter(
    #    SongPlayedMaster.song_id == test_track.song_id
    # ).update(test_transform)
    # print(f"{update_test=}")
    # null_songs = [song[0] for song in results]
    # print(f"{len(set(null_songs))=}")

    # failed on iteration 8316


main()

# file_list = [
#    "/Users/msuzara/Downloads/MyData/endsong_0.json",
#    "/Users/msuzara/Downloads/MyData/endsong_1.json",
#    "/Users/msuzara/Downloads/MyData/endsong_10.json",
#    "/Users/msuzara/Downloads/MyData/endsong_11.json",
#    "/Users/msuzara/Downloads/MyData/endsong_12.json",
#    "/Users/msuzara/Downloads/MyData/endsong_13.json",
#    "/Users/msuzara/Downloads/MyData/endsong_2.json",
#    "/Users/msuzara/Downloads/MyData/endsong_3.json",
#    "/Users/msuzara/Downloads/MyData/endsong_4.json",
#    "/Users/msuzara/Downloads/MyData/endsong_5.json",
#    "/Users/msuzara/Downloads/MyData/endsong_6.json",
#    "/Users/msuzara/Downloads/MyData/endsong_7.json",
#    "/Users/msuzara/Downloads/MyData/endsong_8.json",
#    "/Users/msuzara/Downloads/MyData/endsong_9.json",
# ]
