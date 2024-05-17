import importlib as il
import logging
import logging.handlers
import os
from datetime import datetime, timedelta, timezone

from apiflask import APIFlask
from apiflask.fields import String
from flask_cors import CORS
from flask_jwt_extended import (
    create_access_token,
    get_jwt,
    get_jwt_identity,
    set_access_cookies,
)

from event_horizon.api import ResponseSchema
from event_horizon.commands import register_commands
from event_horizon.config import Development, Production, Test
from event_horizon.extensions import db, jwt_manager, migrate
from event_horizon.models import TokenBlocklist, User

__all__ = ["create_app"]


def create_app(env=None, db_uri=None):
    if not env:
        env = os.getenv("FLASK_ENV", "development")

    app = APIFlask(__name__, title="Event Horizon", instance_relative_config=True)
    app.security_schemes = {
        "BearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
    }

    register_config(app, env)
    if db_uri:
        app.config["SQLALCHEMY_DATABASE_URI"] = db_uri
    if env != "test":
        register_logger(app)

    @jwt_manager.user_lookup_loader
    def user_lookup_callback(_jwt_header, jwt_data):
        identity = jwt_data["sub"]
        return db.session.query(User).filter(User.email == identity).first()  # type: ignore

    @jwt_manager.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload: dict) -> bool:
        jti = jwt_payload["jti"]
        token = db.session.query(TokenBlocklist).filter_by(jti=jti).first()
        return token is not None

    @app.after_request
    def refresh_expiring_jwts(response):
        try:
            exp_timestamp = get_jwt()["exp"]
            now = datetime.now(timezone.utc)
            target_timestamp = datetime.timestamp(now + timedelta(minutes=30))
            if target_timestamp > exp_timestamp:
                access_token = create_access_token(identity=get_jwt_identity())
                set_access_cookies(response, access_token)
        except (RuntimeError, KeyError):
            # Case where there is not a valid JWT. Just return the original response
            return response
        else:
            return response

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
    jwt_manager.init_app(app)
    migrate.init_app(app, db)


def register_blueprints(app):
    for mod_name in ("user", "event", "alert", "auth", "report"):
        mod = il.import_module(f"{__package__}.api.{mod_name}.views", __name__)
        blueprint = getattr(mod, f"{mod_name}_bp")
        CORS(blueprint)
        app.register_blueprint(blueprint)
