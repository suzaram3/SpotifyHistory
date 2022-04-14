"""
Author : Mitch Suzara <suzaram3@gmail.com>
Date   : 2022-04-14
Purpose: Rock the Casbah
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # CLIENT_ID = os.environ.get("CLIENT_ID")
    # CLIENT_SECRET = os.environ.get("CLIENT_SECRET")
    # REDIRECT_URI = os.environ.get("REDIRECT_URI")
    # OAUTH_TOKEN = os.environ.get("CLIENT_SECRET")
    SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID")
    SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET")
    SPOTIPY_REDIRECT_URI = os.getenv("SPOTIPY_REDIRECT_URI")


class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get("DEV_DATABASE_URL")


config = {
    "development": DevelopmentConfig,
    "default": DevelopmentConfig,
}
