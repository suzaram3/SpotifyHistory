import os
import random
import matplotlib.pyplot as plt
import numpy as np
from multiprocessing import Process
from PIL import Image
from sqlalchemy import func
from wordcloud import ImageColorGenerator, WordCloud
from SpotifyHistory.config import Config
from SpotifyHistory.app.utils.queries import cloud


def grey_color_func(
    word, font_size, position, orientation, random_state=None, **kwargs
) -> str:
    """Returns grey color for word cloud font"""
    return "hsl(0, 0%%, %d%%)" % random.randint(60, 100)


def generate_word_cloud(**kwargs) -> Image:
    """Generates a multi plot word cloud from frequency_dict,
    and mask_image. Stores result in file_path"""
    mask = np.array(Image.open(kwargs["mask_image"]))

    wc = WordCloud(
        background_color="black",
        font_path=c.config["mask_fonts"]["epoxy"],
        mask=mask,
        # max_font_size=256,
    ).generate_from_frequencies(kwargs["freq_dict"])

    if kwargs["multi_flag"]:
        image_colors = ImageColorGenerator(mask)
        fig, axes = plt.subplots(1, 3)
        axes[0].imshow(wc, interpolation="bilinear")
        axes[1].imshow(wc.recolor(color_func=image_colors), interpolation="bilinear")
        axes[2].imshow(mask, cmap=plt.cm.gray, interpolation="bilinear")
        for ax in axes:
            ax.set_axis_off()
        plt.axis("off")
        plt.savefig(
            kwargs["outfile_path"],
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
            kwargs["outfile_path"],
            bbox_inches="tight",
            pad_inches=0,
            dpi=1200,
        )


def generate_thumbnail(in_file: str, size=(512, 512)) -> None:
    """Generates a thumbnail image from the word cloud plot"""
    try:
        with Image.open(in_file) as tn:
            tn.thumbnail(size)
            tn.copy().save(f"{in_file}.thumbnail", "PNG")
    except FileNotFoundError as e:
        c.file_logger.error(f"No file found at {in_file}...")


# setup
c = Config()

# query top artists and songs
query_results = cloud()

top_artist_list = query_results["top_artist_list"]
top_song_list = query_results["top_song_list"]
top_artist_average = sum([artist[1] for artist in top_artist_list]) // len(
    top_artist_list
)
top_artist_frequencies = {
    artist[0]: artist[1] for artist in top_artist_list if artist[1] > 23
}
top_song_average = sum([song[1] for song in top_song_list]) // len(top_artist_list)
top_song_frequencies = {song[0]: song[1] for song in top_song_list if song[1] > 23}

# random mask image
options = [option for option in c.config["mask_images"]]

# generate word clouds and thumbnails
cpu = os.cpu_count()
pool = [
    Process(
        target=generate_word_cloud,
        kwargs={
            "freq_dict": top_artist_frequencies,
            "outfile_path": c.config["file_paths"]["top_artists_image"],
            "mask_image": c.config["mask_images"][random.choice(options)],
            "multi_flag": False,
        },
    ),
    Process(
        target=generate_word_cloud,
        kwargs={
            "freq_dict": top_artist_frequencies,
            "outfile_path": c.config["file_paths"]["top_artists_image_multi"],
            "mask_image": c.config["mask_images"][random.choice(options)],
            "multi_flag": True,
        },
    ),
    Process(
        target=generate_word_cloud,
        kwargs={
            "freq_dict": top_song_frequencies,
            "outfile_path": c.config["file_paths"]["top_songs_image"],
            "mask_image": c.config["mask_images"][random.choice(options)],
            "multi_flag": False,
        },
    ),
    Process(
        target=generate_word_cloud,
        kwargs={
            "freq_dict": top_song_frequencies,
            "outfile_path": c.config["file_paths"]["top_songs_image_multi"],
            "mask_image": c.config["mask_images"][random.choice(options)],
            "multi_flag": True,
        },
    ),
]
for p in pool:
    p.start()

for p in pool:
    p.join()

# generate thumbnails
generate_thumbnail(c.config["file_paths"]["top_artists_image"])
generate_thumbnail(c.config["file_paths"]["top_songs_image"])
