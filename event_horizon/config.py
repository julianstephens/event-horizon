# -*- coding: utf-8 -*-


import logging
import os

base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))


class BaseConfig(object):
    PROJECT_ROOT = base_dir

    DEBUG = False
    TESTING = False

    SECRET_KEY = os.environ.get("SECRET_KEY")


class DefaultConfig(BaseConfig):
    DEBUG = True

    # Flask-Sqlalchemy
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # POSTGRESQL for production
    PGHOST = os.environ.get("PGHOST", "localhost")
    PGDATABASE = os.environ.get("PGDATABASE", "eventhorizon")
    PGUSER = os.environ.get("PGUSER", "postgres")
    PGPASSWORD = os.environ.get("PGPASSWORD", "pass")
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{PGUSER}:{PGPASSWORD}@{PGHOST}/{PGDATABASE}"
    )

    # Flask-cache
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 60

    LOG_FILE = os.path.join(base_dir, "logs", "app.log")
    LOG_LEVEL = logging.INFO
    LOG_SIZE = 1024 * 1024
