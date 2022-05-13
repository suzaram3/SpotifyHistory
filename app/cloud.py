"""
Author : Mitch Suzara <suzaram3@gmail.com>
Date   : 2022-05-12
Purpose: Generate word cloud from top artists in data pipeline
"""
import argparse
import csv
import sys
import random

import matplotlib.pyplot as plt
import numpy as np

from PIL import Image
from wordcloud import WordCloud, ImageColorGenerator

from config import Config

c = Config()


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


def generate_word_cloud(frequency_dict: dict, file_path: str):
    mask = np.array(Image.open(c.WORDCLOUD_MASK_GUITAR))
    wc = WordCloud(
        font_path=c.WORDCLOUD_FONT, mask=mask, max_font_size=256
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


def usage() -> str:
    print(f"Usage: {sys.argv[0]} [artists|songs]")


def main():

    if len(sys.argv) < 2:
        usage()
    elif sys.argv[1] == "artists":
        generate_word_cloud(
            csv_frequency(c.TOP_ARTISTS_FILE_PATH), c.ARTISTS_WORDCLOUD_PATH
        )
    elif sys.argv[1] == "songs":
        generate_word_cloud(
            csv_frequency(c.TOP_SONGS_FILE_PATH), c.SONGS_WORDCLOUD_PATH
        )
    else:
        usage()


if __name__ == "__main__":
    main()
