from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from sqlalchemy import String, Text
from sqlalchemy.orm import DeclarativeBase, registry

from event_horizon.types import str_16, str_36, str_80, str_120, str_255, text


class Base(DeclarativeBase):
    registry = registry(
        type_annotation_map={
            str_16: String(16),
            str_36: String(36),
            str_80: String(80),
            str_120: String(120),
            str_255: String(255),
            text: String().with_variant(Text, "postgresql"),
        }
    )


db = SQLAlchemy(model_class=Base)
csrf = CSRFProtect()
migrate = Migrate()
session = Session()
jwt_manager = JWTManager()
