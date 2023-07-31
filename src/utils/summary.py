from datetime import datetime


def summary_main(query_results: dict) -> None:
    freq = {
        "Monday": 0,
        "Tuesday": 0,
        "Wednesday": 0,
        "Thursday": 0,
        "Friday": 0,
        "Saturday": 0,
        "Sunday": 0,
    }

    average_streams_per_day = sum(
        [row[0] for row in query_results["stream_count_per_day"]]
    ) // len(query_results["stream_count_per_day"])

    for day in query_results["freq_by_day"]:
        freq[day[0].strftime("%A")] = freq.get(day[0].strftime("%A")) + day[1]


    top_song_msg = ""
    print(f"\n\033[1mUTC\033[0m: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\n**SpotifyData[\033[1m\033[0m]**\n-TableCounts-")
    [
        print(f"{model['model'].__name__}: {model['count']:,}")
        for model in query_results["table_counts"]
    ]
    print("\n*TotalDayFrequency*")
    [print(f"{day}: {freq[day]:,}") for day in freq]
    print(f"\n*MiscellaneousData*")
    print(f"AverageStreamsPerDay : {average_streams_per_day}")
    print(f"StreamTimeInDays: {(query_results['days'][0] // 1000) // 86400}")
    print(f"StreamsThisYear: {query_results['year_count']:,}")
    print(f"\n*TodayData*")
    print(f"StreamsToday: {query_results['play_today'][0]}")
    if query_results["top_song_today"] and query_results["top_song_today"][0] > 1:
        top_song_msg = (
            f"TodayTopSong: {query_results['top_song_today'][0]} "
            f"plays | {query_results['top_song_today'][1]}"
            f"- \033[1m{query_results['top_song_today'][2]}\033[0m\n"
        )
        print(top_song_msg)
    print(f"\n*YearData*")
    print(
        f"TopArtistThisYear: {query_results['top_artist_year'][1]} | Plays : {query_results['top_artist_year'][0]}"
    )
    print(
        f"TopSongThisYear: {query_results['top_song_year'][1]} | Plays: {query_results['top_song_year'][0]} | Artist: {query_results['top_song_year'][2]}"
    )
    print()