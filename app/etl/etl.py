from sqlalchemy.dialects.postgresql import insert as pg_insert
from SpotifyHistory.config import Config
from SpotifyHistory.app.utils.spotify import SpotifyHandler
from . transform import TransformData


def get_table_counts(session: Config.Session, model: object) -> dict:
    return {"model": model, "table_count": session.query(model).count()}


"""Main function for the etl program: gets recent songs and inserts them into the music.extract table"""
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
        "model": c.models["Artist"],
        "records": record_insert_list[1],
    },
    {"model": c.models["Song"], "records": record_insert_list[2]},
    {"model": c.models["SongStreamed"], "records": record_insert_list[3]},
    {"model": c.models["Album"], "records": record_insert_list[0]},
]

# get pre counts, add records, and get post counts
with c.session_scope() as session:
    pre_insert = [get_table_counts(session, c.models[model]) for model in c.models]
    statements = [
        pg_insert(chunk["model"]).values(record).on_conflict_do_nothing()
        for chunk in record_dicts
        for record in chunk["records"]
    ]
    [session.execute(statement) for statement in statements]
    post_insert = [get_table_counts(session, c.models[model]) for model in c.models]

# log amount of records loaded
[
    c.file_logger.info(
        f"{post['table_count'] - pre['table_count']} rows added to {post['model'].__tablename__}"
    )
    for post, pre in zip(post_insert, pre_insert)
    if post["table_count"] > pre["table_count"]
]
