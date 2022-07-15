from sqlalchemy import cast, Date, func
from config import Config

c = Config()

with c.session_scope() as session:
    table_counts = [{key: session.query(c.models[key]).count()} for key in c.models]
    stream_count_per_day = (
        session.query(
            func.count(cast(c.models["SongStreamed"].played_at, Date)),
        )
        .group_by(cast(c.models["SongStreamed"].played_at, Date))
        .all()
    )
average_streams_per_day = sum([row[0] for row in stream_count_per_day]) // len(
    stream_count_per_day
)

print(f"\n**SpotifyData**\n-Table Counts-")
[print(f"{key}: {value:,}") for item in table_counts for key, value in item.items()]
print(f"\n**Miscellaneous Data**")
print(f"average_streams_per_day : {average_streams_per_day}")
print()
