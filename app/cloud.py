"""
Author : Mitch Suzara <suzaram3@gmail.com>
Date   : 2022-05-12
Purpose: Generate word cloud from top artists in data warehouse
"""
import csv
import os
import random
import time
from matplotlib import artist
import matplotlib.pyplot as plt
import numpy as np
from multiprocessing import Process
from PIL import Image
from sqlalchemy import func
from wordcloud import ImageColorGenerator, WordCloud
from qa_config import Config, Session


def grey_color_func(
    word, font_size, position, orientation, random_state=None, **kwargs
) -> str:
    """Returns grey color for word cloud font"""
    return "hsl(0, 0%%, %d%%)" % random.randint(60, 100)


def generate_word_cloud(
    frequency_dict: dict, file_path: str, mask_image: str, multi_flag: bool
) -> None:
    """Generates a multi plot word cloud from frequency_dict,
    and mask_image. Stores result in file_path"""
    mask = np.array(Image.open(mask_image))

    wc = WordCloud(
        background_color="black",
        font_path=c.config["mask_fonts"]["epoxy"],
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


# setup
c = Config()

# query top artists and songs
with Session() as session:
    top_song_list = (
        session.query(
            c.models["Song"].name, func.count(c.models["SongStreamed"].song_id)
        )
        .join(
            c.models["Song"],
            c.models["Song"].id == c.models["SongStreamed"].song_id,
        )
        .group_by(c.models["SongStreamed"].song_id, c.models["Song"].name)
        .order_by(func.count(c.models["SongStreamed"].song_id).desc())
        .all()
    )

    top_artist_list = (
        session.query(c.models["Artist"].name, func.count(c.models["Artist"].id))
        .join(
            c.models["Song"],
            c.models["Song"].artist_id == c.models["Artist"].id,
            isouter=True,
        )
        .join(
            c.models["SongStreamed"],
            c.models["SongStreamed"].song_id == c.models["Song"].id,
            isouter=True,
        )
        .group_by(c.models["Artist"].id, c.models["Artist"].name)
        .order_by(func.count(c.models["Artist"].id).desc())
        .all()
    )

top_artist_average = sum([artist[1] for artist in top_artist_list]) // len(
    top_artist_list
)
top_artist_frequencies = {
    artist[0]: artist[1] for artist in top_artist_list if artist[1] > 23
}

top_song_average = sum([song[1] for song in top_song_list]) // len(top_artist_list)
top_song_frequencies = {song[0]: song[1] for song in top_song_list if song[1] > 23}

# random mask image
<<<<<<< HEAD
options = [option for option in pc.config["mask_images"]]
#random_mask = random.choice(options)

=======
options = [option for option in c.config["mask_images"]]
>>>>>>> major_refactor

# generate word clouds and thumbnails
cpu = os.cpu_count()
pool = [
    Process(
        target=generate_word_cloud,
        args=(
            top_artist_frequencies,
<<<<<<< HEAD
            pc.config["file_paths"]["top_artists_image"],
            pc.config["mask_images"][random.choice(options)],
=======
            c.config["file_paths"]["top_artists_image"],
            c.config["mask_images"][random.choice(options)],
>>>>>>> major_refactor
            False,
        ),
    ),
    Process(
        target=generate_word_cloud,
        args=(
            top_song_frequencies,
<<<<<<< HEAD
            pc.config["file_paths"]["top_songs_image"],
            pc.config["mask_images"][random.choice(options)],
=======
            c.config["file_paths"]["top_songs_image"],
            c.config["mask_images"][random.choice(options)],
>>>>>>> major_refactor
            False,
        ),
    ),
    Process(
        target=generate_word_cloud,
        args=(
            top_artist_frequencies,
<<<<<<< HEAD
            pc.config["file_paths"]["top_artists_image_multi"],
            pc.config["mask_images"][random.choice(options)],
=======
            c.config["file_paths"]["top_artists_image_multi"],
            c.config["mask_images"][random.choice(options)],
>>>>>>> major_refactor
            True,
        ),
    ),
    Process(
        target=generate_word_cloud,
        args=(
            top_song_frequencies,
<<<<<<< HEAD
            pc.config["file_paths"]["top_songs_image_multi"],
            pc.config["mask_images"][random.choice(options)],
=======
            c.config["file_paths"]["top_songs_image_multi"],
            c.config["mask_images"][random.choice(options)],
>>>>>>> major_refactor
            True,
        ),
    ),
]
for p in pool:
    p.start()

for p in pool:
    p.join()

# generate thumbnails
generate_thumbnail(c.config["file_paths"]["top_artists_image"])
generate_thumbnail(c.config["file_paths"]["top_songs_image"])
