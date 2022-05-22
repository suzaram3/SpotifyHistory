"""
Author : Mitch Suzara <suzaram3@gmail.com>
Date   : 2022-05-12
Purpose: Generate word cloud from top artists in data pipeline
"""
import csv, random, sys
from email.mime import base
from configparser import ConfigParser, ExtendedInterpolation

import matplotlib.pyplot as plt
import numpy as np

from PIL import Image
from wordcloud import WordCloud

config = ConfigParser(interpolation=ExtendedInterpolation())
config.read(
    [
        "/Users/msuzara/Library/Mobile Documents/com~apple~CloudDocs/cloud_workspace/python/SpotifyHistory/db.conf",
        "/Users/msuzara/Library/Mobile Documents/com~apple~CloudDocs/cloud_workspace/python/SpotifyHistory/settings.conf",
    ]
)


def grey_color_func(
    word, font_size, position, orientation, random_state=None, **kwargs
):
    return "hsl(0, 0%%, %d%%)" % random.randint(60, 100)


def csv_frequency(file_path: str) -> dict:
    frequency_dict = {}
    with open(file_path, newline="") as csvfile:
        music_reader = csv.reader(csvfile, delimiter="|")
        next(music_reader, None)
        for k, v in music_reader:
            frequency_dict[k] = int(v)
    return frequency_dict


def generate_word_cloud(frequency_dict: dict, file_path: str, mask_image: str) -> None:
    mask = np.array(Image.open(mask_image))
    wc = WordCloud(
        font_path=config["mask_fonts"]["wordcloud_font"], mask=mask, max_font_size=256
    ).generate_from_frequencies(frequency_dict)

    plt.imshow(
        wc.recolor(color_func=grey_color_func, random_state=3),
        interpolation="bilinear",
    )

    plt.axis("off")
    plt.savefig(
        file_path,
        bbox_inches="tight",
        pad_inches=0,
        dpi=1200,
    )


def generate_thumbnail(in_file: str, size=(1024, 1024)) -> None:
    with Image.open(in_file) as tn:
        tn.thumbnail(size)
        tn.copy().save(f"{in_file}.thumbnail", "JPEG")


def usage() -> str:
    print(f"Usage: {sys.argv[0]} [artists|songs]")


def main():
    options = [option for option in config["mask_images"]]
    random_mask = random.choice(options)
    if len(sys.argv) < 2:
        usage()
    elif sys.argv[1] == "artists":
        generate_word_cloud(
            csv_frequency(config["file_paths"]["top_artists_csv"]),
            config["file_paths"]["top_artists_image"],
            config["mask_images"][random_mask],
        )

    elif sys.argv[1] == "songs":
        generate_word_cloud(
            csv_frequency(config["file_paths"]["top_songs_csv"]),
            config["file_paths"]["top_songs_image"],
            config["mask_images"][random_mask],
        )
        generate_thumbnail(config["file_paths"]["top_songs_image"])
    else:
        usage()


if __name__ == "__main__":
    main()
