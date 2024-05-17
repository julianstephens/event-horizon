# -*- coding: utf-8 -*-

import typing
import logging
import os
from datetime import timedelta

base_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
secret_key = os.getenv("SECRET_KEY")


class BaseConfig(object):
    PROJECT_ROOT = base_dir

    DEBUG = False
    TESTING = False

    SECRET_KEY = secret_key

    # Flask-Sqlalchemy
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Flask-JWT
    JWT_SECRET_KEY = secret_key
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=1)

    # Flask-cache
    CACHE_TYPE = "simple"
    CACHE_DEFAULT_TIMEOUT = 60

    # Flask-API
    SYNC_LOCAL_SPEC = True
    LOCAL_SPEC_PATH = os.path.join(base_dir, "openapi.json")
    INFO: typing.ClassVar = {
        "title": "Event Horizon",
        "version": "0.1",
        "description": "A simple event management API",
    }


class Development(BaseConfig):
    FLASK_ENV = "development"
    DEBUG = True

    PGHOST = os.getenv("PGHOST", "localhost")
    PGDATABASE = os.getenv("PGDATABASE", "eventhorizon")
    PGUSER = os.getenv("PGUSER", "postgres")
    PGPASSWORD = os.getenv("PGPASSWORD", "pass")
    SQLALCHEMY_DATABASE_URI = (
        f"postgresql+psycopg2://{PGUSER}:{PGPASSWORD}@{PGHOST}/{PGDATABASE}"
    )

    LOG_FILE = os.path.join(base_dir, "logs", "app.log")
    LOG_LEVEL = logging.INFO
    LOG_SIZE = 1024 * 1024


class Production(BaseConfig):
    FLASK_ENV = "production"


class Test(BaseConfig):
    FLASK_ENV = "test"
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_TEST", "postgresql+psycopg2:///postgres@localhost/eventhorizon_test"
    )
