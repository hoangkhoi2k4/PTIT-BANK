import os
from datetime import timedelta

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    SECRET_KEY = "your_secret_key"
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///ptit_database.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    PERMANENT_SESSION_LIFETIME = timedelta(minutes=15)
