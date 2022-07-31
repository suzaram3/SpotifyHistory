from datetime import date, timedelta
import matplotlib.pyplot as plt
import numpy as np
from SpotifyHistory.config import Config
from SpotifyHistory.app.utils.queries import weekly_summary


c = Config()


def get_week_range() -> dict:
    today = date.today()
    start = today - timedelta(days=today.weekday())
    return [
        {
            "day_string": "Monday",
            "week_day": today - timedelta(days=today.weekday()),
            "count": 0,
        },
        {
            "day_string": "Tuesday",
            "week_day": start + timedelta(days=1),
            "count": 0,
        },
        {
            "day_string": "Wednesday",
            "week_day": start + timedelta(days=2),
            "count": 0,
        },
        {
            "day_string": "Thursday",
            "week_day": start + timedelta(days=3),
            "count": 0,
        },
        {
            "day_string": "Friday",
            "week_day": start + timedelta(days=4),
            "count": 0,
        },
        {
            "day_string": "Saturday",
            "week_day": start + timedelta(days=5),
            "count": 0,
        },
        {
            "day_string": "Sunday",
            "week_day": start + timedelta(days=6),
            "count": 0,
        },
    ]


def make_graph(data: list[dict]) -> None:
    x = [key["day_string"][:3] for key in data]
    y = [key["count"] for key in data]
    c_map = plt.get_cmap("viridis")
    rescale = lambda y: (y - np.min(y)) / (np.max(y) - np.min(y))
    plt.bar(x, y, color=c_map(rescale(y)))
    plt.xlabel("DayOfWeek")
    plt.ylabel("StreamsPerDay")
    plt.savefig(
        fname=c.config["file_paths"]["weekly_summary"],
        dpi=600,
    )


def main() -> None:

    week_range = get_week_range()
    week_range_count = weekly_summary(week_range)
    make_graph(week_range_count)


main()
