import logging
import logging.config

from models import Artist, Album, Song, SongStreamed
from session import SessionHandler
from spotify import SpotifyHandler
from transform import TransformData

logging.config.fileConfig("/home/msuzara/SpotifyHistory/logging.conf")
file_logger = logging.getLogger("file")
console_logger = logging.getLogger("console")


def etl() -> None:
    """Main function for the etl program: gets recent songs and inserts them into the music.extract table"""
    # setup
    sh, sp, td = SessionHandler(), SpotifyHandler(), TransformData()

    # fetch
    spotify_response = sp.get_recently_played()

    # transform
    transform_raw_data = [td.transform_data(item) for item in spotify_response["items"]]
    record_insert_list = td.compile_model_lists(transform_raw_data)

    record_dicts = [
        {
            "model": Artist,
            "records": record_insert_list[1],
        },
        {"model": Song, "records": record_insert_list[2]},
        {"model": SongStreamed, "records": record_insert_list[3]},
        {"model": Album, "records": record_insert_list[0]},
    ]

    with sh.session_scope() as session:
        pre_insert = [
            sh.get_table_count(session, model["model"]) for model in record_dicts
        ]
        results = [sh.insert_many(session, model) for model in record_dicts]

    [
        file_logger.info(
            f"{x['count'] - y['count']} rows added to {x['model'].__tablename__}"
        )
        for x, y in zip(results, pre_insert)
        if x["count"] > y["count"]
    ]


etl()
