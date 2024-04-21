import importlib as il
import logging
import logging.handlers
import os

from apiflask import APIFlask
from apiflask.fields import String
from flask_cors import CORS

from event_horizon.api import ResponseSchema
from event_horizon.commands import register_commands
from event_horizon.config import Development, Production, Test
from event_horizon.extensions import db, migrate, session

__all__ = ["create_app"]


def create_app(env=None, db_uri=None):
    if not env:
        env = os.getenv("FLASK_ENV", "development")

    app = APIFlask(__name__, instance_relative_config=True)

    register_config(app, env)
    if db_uri:
        app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    if env != "test":
        register_logger(app)

    @app.get("/")
    @app.output(
        {"name": String(), "version": String(), "description": String()},
        schema_name="InfoSchema",
    )
    def index():
        """
        API info
        """
        return {
            "data": {
                "name": "Event Horizon",
                "version": "0.1",
                "description": "A simple event management API",
            }
        }

    register_blueprints(app)
    register_extensions(app)
    register_commands(app, db)

    return app


def register_config(app, env):
    if env == "production":
        app.config.from_object(Production)
    elif env == "test":
        app.config.from_object(Test)
    else:
        app.config.from_object(Development)

    app.config["BASE_RESPONSE_SCHEMA"] = ResponseSchema


def register_logger(app):
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


def register_extensions(app):
    db.init_app(app)
    app.config["SESSION_SQLALCHEMY"] = db
    session.init_app(app)
    migrate.init_app(app, db)


def register_blueprints(app):
    for mod_name in ("user", "event", "alert"):
        mod = il.import_module(f"{__package__}.api.{mod_name}.views", __name__)
        blueprint = getattr(mod, f"{mod_name}_bp")
        CORS(blueprint)
        app.register_blueprint(blueprint)
