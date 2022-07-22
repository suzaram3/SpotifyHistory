from datetime import date
from sqlalchemy import cast, Date, func, select
from SpotifyHistory.config import Config
from SpotifyHistory.app.utils.queries import summary, engine


c = Config()
instance = str(engine).split("/")[-1]

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

print(f"\n**SpotifyData[\033[1m{instance[:-1]}\033[0m]**\n-TableCounts-")
[
    print(f"{model['model'].__name__}: {model['count']:,}")
    for model in query_results["table_counts"]
]
print("\n*TotalDayFrequency*")
[print(f"{day}: {freq[day]:,}") for day in freq]
print(f"\n*MiscellaneousData*")
print(f"AverageStreamsPerDay : {average_streams_per_day}")
print(f"StreamsToday: {query_results['play_today'][0]}")
if query_results["top_song_today"][0] > 1:
    print(
        f"TodayTopSong: {query_results['top_song_today'][0]} plays | \"{query_results['top_song_today'][1]}\" - \033[1m{query_results['top_song_today'][2]}\033[0m"
    )
print(f"StreamsThisYear: {query_results['year_count']:,}")
print(f"StreamTimeInDays: {(query_results['days'][0] // 1000) // 86400}")
print()
