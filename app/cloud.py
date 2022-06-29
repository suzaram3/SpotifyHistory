"""
Author : Mitch Suzara <suzaram3@gmail.com>
Date   : 2022-05-12
Purpose: Generate word cloud from top artists in data warehouse
"""
import csv
import random
import sys
from configparser import ConfigParser, ExtendedInterpolation

import matplotlib.pyplot as plt
import numpy as np

from PIL import Image
from wordcloud import ImageColorGenerator, WordCloud

config = ConfigParser(interpolation=ExtendedInterpolation())
config.read(
    [
        "/Users/msuzara/Library/Mobile Documents/com~apple~CloudDocs/cloud_workspace/python/SpotifyHistory/settings.conf",
    ]
)


def grey_color_func(
    word, font_size, position, orientation, random_state=None, **kwargs
) -> str:
    """Returns grey color for word cloud font"""
    return "hsl(0, 0%%, %d%%)" % random.randint(60, 100)


def csv_frequency(file_path: str) -> dict:
    """Read CSV file and returns a dict of frequencies"""
    frequency_dict = {}
    with open(file_path, newline="") as csvfile:
        music_reader = csv.reader(csvfile, delimiter="|")
        next(music_reader, None)
        for k, v in music_reader:
            frequency_dict[k] = int(v)
    return frequency_dict


def generate_word_cloud(
    frequency_dict: dict, file_path: str, mask_image: str, multi_flag=False
) -> None:
    """Generates a multi plot word cloud from frequency_dict,
    and mask_image. Stores result in file_path"""
    mask = np.array(Image.open(mask_image))

    wc = WordCloud(
        background_color="black",
        font_path=config["mask_fonts"]["epoxy"],
        mask=mask,
        max_font_size=256,
    ).generate_from_frequencies(frequency_dict)

    if multi_flag:
        image_colors = ImageColorGenerator(mask)
        fig, axes = plt.subplots(1, 3)
        axes[0].imshow(wc, interpolation="bilinear")
        axes[1].imshow(wc.recolor(color_func=image_colors), interpolation="bilinear")
        axes[2].imshow(mask, cmap=plt.cm.gray, interpolation="bilinear")
        for ax in axes:
            ax.set_axis_off()
        plt.axis("off")
        plt.savefig(
            file_path,
            bbox_inches="tight",
            pad_inches=0,
            dpi=1200,
        )
    else:
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
    """Generates a thumbnail image from the word cloud plot"""
    with Image.open(in_file) as tn:
        tn.thumbnail(size)
        tn.copy().save(f"{in_file}.thumbnail", "JPEG")


def usage() -> str:
    """Shows usage of the cloud.py program"""
    print(f"Usage: {sys.argv[0]} [artists|multi|songs]")


def cloud_driver() -> None:
    """Main function for the cloud.py program"""
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
        generate_thumbnail(config["file_paths"]["top_artists_image"])

    elif sys.argv[1] == "songs":
        generate_word_cloud(
            csv_frequency(config["file_paths"]["top_songs_csv"]),
            config["file_paths"]["top_songs_image"],
            config["mask_images"][random_mask],
        )
        generate_thumbnail(config["file_paths"]["top_songs_image"])
    elif sys.argv[1] == "multi":
        generate_word_cloud(
            csv_frequency(config["file_paths"]["top_artists_csv"]),
            config["file_paths"]["top_artists_image_multi"],
            config["mask_images"][random_mask],
            multi_flag=True,
        )
        generate_word_cloud(
            csv_frequency(config["file_paths"]["top_songs_csv"]),
            config["file_paths"]["top_songs_image_multi"],
            config["mask_images"][random_mask],
            multi_flag=True,
        )
    else:
        usage()


cloud_driver()
