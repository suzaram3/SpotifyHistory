"""
Author : Mitch Suzara <suzaram3@gmail.com>
Date   : 2022-04-14
Purpose: Main driver for ETL
"""
from extract import ExtractSongs

def main() -> None:
    e = ExtractSongs()
    print(e.get_recently_played())


if __name__ == "__main__":
    main()
