import logging, logging.config

from sqlalchemy.orm import sessionmaker
from session import SessionHandler
from db import DB
from models import SongPlayed
from transform import TransformData
from extract import ExtractData

logging.config.fileConfig(
    "/Users/msuzara/Library/Mobile Documents/com~apple~CloudDocs/cloud_workspace/python/SpotifyHistory/logging.conf"
)
file_logger = logging.getLogger("file")
console_logger = logging.getLogger("console")


def main() -> None:

    db = DB.create()
    engine = db.engine
    Session = sessionmaker(bind=engine)
    session = Session()
    td = TransformData()
    ed = ExtractData()
    user_session = SessionHandler.create(session, SongPlayed)

    before_insert = user_session.get_total_count()

    track_raw_data = ed.extract()
    song_list = [td.make_song_objects(item) for item in track_raw_data["items"]]

    try:
        user_session.insert_many(song_list)
        session.commit()
        after_insert = user_session.get_total_count()
        if after_insert > before_insert:
            file_logger.info(
                f"{after_insert-before_insert} rows inserted into {user_session.model.__tablename__} "
            )
    except Exception as e:
        session.rollback()
        file_logger.info(e)
        raise e
    finally:
        session.close()


if __name__ == "__main__":
    main()
