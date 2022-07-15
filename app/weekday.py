from sqlalchemy import cast, Date, func
from config import Config

c = Config()

with c.session_scope() as session:
    stream_count_per_day = (
        session.query(
            cast(c.models["SongStreamed"].played_at, Date),
            func.count(cast(c.models["SongStreamed"].played_at, Date)),
        )
        .group_by(cast(c.models["SongStreamed"].played_at, Date))
        .all()
    )

freq = {
    "Monday": 0,
    "Tuesday": 0,
    "Wednesday": 0,
    "Thursday": 0,
    "Friday": 0,
    "Saturday": 0,
    "Sunday": 0,
}

for day in stream_count_per_day:
    freq[day[0].strftime("%A")] = freq.get(day[0].strftime("%A")) + day[1]

print("\n**Day Frequency**")
[print(f"{day}: {freq[day]:,}") for day in freq]
print()
