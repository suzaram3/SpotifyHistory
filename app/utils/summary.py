from datetime import date
from sqlalchemy import cast, Date, func, select
from SpotifyHistory.config import Config


TODAY = date.today()  # .strftime("%Y-%m-%d")
c = Config()
instance = str(c.engine).split("/")[-1]

freq = {
    "Monday": 0,
    "Tuesday": 0,
    "Wednesday": 0,
    "Thursday": 0,
    "Friday": 0,
    "Saturday": 0,
    "Sunday": 0,
}

with c.session_scope() as session:
    table_counts = [{key: session.query(c.models[key]).count()} for key in c.models]
    stream_count_per_day = (
        session.query(
            func.count(cast(c.models["SongStreamed"].played_at, Date)),
        )
        .group_by(cast(c.models["SongStreamed"].played_at, Date))
        .all()
    )
    freq_by_day = (
        session.query(
            cast(c.models["SongStreamed"].played_at, Date),
            func.count(cast(c.models["SongStreamed"].played_at, Date)),
        )
        .group_by(cast(c.models["SongStreamed"].played_at, Date))
        .order_by(cast(c.models["SongStreamed"].played_at, Date).desc())
        .all()
    )
    play_today = (
        session.query(func.count(c.models["SongStreamed"].song_id))
        .filter(cast(c.models["SongStreamed"].played_at, Date) == TODAY)
        .first()
    )


average_streams_per_day = sum([row[0] for row in stream_count_per_day]) // len(
    stream_count_per_day
)


for day in freq_by_day:
    freq[day[0].strftime("%A")] = freq.get(day[0].strftime("%A")) + day[1]

print(f"\n**SpotifyData[{instance[:-1]}]**\n-Table Counts-")
[print(f"{key}: {value:,}") for item in table_counts for key, value in item.items()]
print("\n*Day Frequency*")
[print(f"{day}: {freq[day]:,}") for day in freq]
print(f"\n*Miscellaneous Data*")
print(f"average_streams_per_day : {average_streams_per_day}")
print(f"Streams Today: {play_today[0]}")
print()
