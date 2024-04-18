import logging
import logging.handlers

from flask import Flask

from event_horizon.config import DefaultConfig

from .extensions import csrf, db, migrate

__all__ = ["create_app"]


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(DefaultConfig)

    handler = logging.handlers.RotatingFileHandler(
        app.config["LOG_FILE"], maxBytes=app.config["LOG_SIZE"]
    )
    handler.setLevel(app.config["LOG_LEVEL"])
    handler.setFormatter(
        logging.Formatter(
            "[%(asctime)s] %(levelname)s [%(pathname)s at %(lineno)s]: %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )
    )
    app.logger.addHandler(handler)

    csrf.init_app(app)
    db.init_app(app)
    migrate.init_app(app, db)

    return app
