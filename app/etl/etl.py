from sqlalchemy.dialects.postgresql import insert as pg_insert
from SpotifyHistory.config import Config
from SpotifyHistory.models.models import Album, Artist, Song, SongStreamed
from SpotifyHistory.app.utils.spotify import SpotifyHandler
from SpotifyHistory.app.utils.queries import load_tables, table_counts
from .transform import TransformData


# setup
c, sp, td = Config(), SpotifyHandler(), TransformData()

# fetch
spotify_response = sp.get_recently_played()

# transform
transform_raw_data = [td.transform_data(item) for item in spotify_response["items"]]
record_insert_list = td.compile_model_lists(transform_raw_data)

# compile table dicts
record_dicts = [
    {
        "model": Artist,
        "records": record_insert_list[1],
    },
    {"model": Song, "records": record_insert_list[2]},
    {"model": SongStreamed, "records": record_insert_list[3]},
    {"model": Album, "records": record_insert_list[0]},
]

# get pre counts, add records, and get post counts
pre_insert = table_counts()
load_tables(record_dicts)
post_insert = table_counts()

# log amount of records loaded
[
    c.file_logger.info(f"{post['count'] - pre['count']} rows added to {post['model'].__name__}")
    for post, pre in zip(post_insert, pre_insert)
    if post["count"] > pre["count"]
]
