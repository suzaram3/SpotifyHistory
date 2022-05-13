"""
Author : Mitch Suzara <suzaram3@gmail.com>
Date   : 2022-05-12
Purpose: Generate word cloud from top artists in data pipeline
"""
import csv
import matplotlib.pyplot as plt
import numpy as np
import random
from PIL import Image
from wordcloud import WordCloud, ImageColorGenerator
from config import Config

c = Config()

def grey_color_func(
    word, font_size, position, orientation, random_state=None, **kwargs
):
    return "hsl(0, 0%%, %d%%)" % random.randint(60, 100)


def main():

    d = {}
    with open(c.TOP_ARTISTS_FILE_PATH, newline="") as csvfile:
        music_reader = csv.reader(csvfile, delimiter="|")
        next(music_reader, None)
        for k, v in music_reader:
            d[k] = int(v)

    mask = np.array(Image.open(c.WORDCLOUD_MASK))
    wordcloud = WordCloud(
        background_color="white",
        font_path=c.WORDCLOUD_FONT,
        mask=mask,
        max_font_size=256,
    ).generate_from_frequencies(d)
    wordcloud = WordCloud(
        font_path=c.WORDCLOUD_FONT, mask=mask, max_font_size=256
    ).generate_from_frequencies(d)

    plt.imshow(
        wordcloud.recolor(color_func=grey_color_func, random_state=3),
        interpolation="bilinear",
    )
    plt.axis("off")
    plt.savefig(
        c.SAVE_WORDCLOUD_PATH,
        bbox_inches="tight",
        pad_inches=0,
        dpi=1200,
    )


if __name__ == "__main__":
    main()
