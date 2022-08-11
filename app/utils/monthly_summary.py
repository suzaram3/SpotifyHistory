import matplotlib.pyplot as plt
import numpy as np
from datetime import date, datetime, timedelta
from SpotifyHistory.config import Config
from SpotifyHistory.app.utils.queries import monthly_summary


c = Config()


def make_graph(data: dict) -> None:
    x = [key["day"] for key in data["data"]]
    y = [key["count"] for key in data["data"]]
    plt.plot(x, y, '*--g', )
    plt.grid(visible=True)
    plt.title(
        f"{data['date'].strftime('%B %Y')} Data"
    )
    plt.xlabel(f"Total: {sum([day['count'] for day in data['data']])}")
    plt.xticks(rotation=45)
    plt.tick_params(axis='x', which='major', labelsize=8)
    plt.savefig(
        fname=f"{c.config['file_paths']['monthly_summary']}/{data['date'].strftime('%y_%m')}.png",
        dpi=600,
    )


def main() -> None:
    first_day_of_current_month = date.today().replace(day=1)
    date_of_last_month = first_day_of_current_month - timedelta(days=1)
    counts = monthly_summary(date_of_last_month)
    make_graph({"date": date_of_last_month, "data": counts})


main()
