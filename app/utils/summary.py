from datetime import date
from sqlalchemy import cast, Date, func, select
from SpotifyHistory.config import Config
from SpotifyHistory.app.utils.queries import summary


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

query_results = summary()

average_streams_per_day = sum(
    [row[0] for row in query_results["stream_count_per_day"]]
) // len(query_results["stream_count_per_day"])
for day in query_results["freq_by_day"]:
    freq[day[0].strftime("%A")] = freq.get(day[0].strftime("%A")) + day[1]

print(f"\n**SpotifyData[{instance[:-1]}]**\n-Table Counts-")
[
    print(f"{model['model'].__name__}: {model['count']:,}")
    for model in query_results["table_counts"]
]
print("\n*Day Frequency*")
[print(f"{day}: {freq[day]:,}") for day in freq]
print(f"\n*Miscellaneous Data*")
print(f"average_streams_per_day : {average_streams_per_day}")
print(f"Streams Today: {query_results['play_today'][0]}")
print(
    f"TodayTopSong: {query_results['top_song_today'][0]} plays | {query_results['top_song_today'][1]} by {query_results['top_song_today'][2]}"
)
print(f"Streams This Year: {query_results['year_count']:,}")
print(f"Streamed Time in Days: {(query_results['days'][0] // 1000) // 86400}")
print()
