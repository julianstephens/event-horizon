from typing import Annotated, Optional
from sqlalchemy import JSON, ForeignKey, String, Text, TypeDecorator
import datetime
from sqlalchemy import text as sa_text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import (
    registry,
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    validates,
)
import uuid as uid

from event_horizon.extensions import db
from event_horizon.utils import PasswordHash


class Password(TypeDecorator):
    """Allows storing and retrieving password hashes using PasswordHash."""

    impl = Text

    def __init__(self, **kwds):
        super(Password, self).__init__(**kwds)

    def process_bind_param(self, value, dialect):
        """Ensure the value is a PasswordHash and then return its hash."""
        ph = self._convert(value)
        if ph is None:
            return None
        return ph.hash

    def process_result_value(self, value, dialect):
        """Convert the hash to a PasswordHash, if it's non-NULL."""
        if value is not None:
            return PasswordHash(value)

    def validator(self, password):
        """Provides a validator/converter for @validates usage."""
        if len(password) < 8 or len(password) > 24:
            raise ValueError("Password must be between 8 and 24 characters.")
        elif not any(char.isdigit() for char in password):
            raise ValueError("Password must contain at least one digit.")
        elif not any(char.islower() for char in password):
            raise ValueError("Password must contain at least one lowercase letter.")
        elif not any(char.isupper() for char in password):
            raise ValueError("Password must contain at least one uppercase letter.")
        elif not any(char in "!@#$%^&*()-+" for char in password):
            raise ValueError("Password must contain at least one special character.")

        return self._convert(password)

    def _convert(self, value) -> PasswordHash | None:
        """Returns a PasswordHash from the given string.

        PasswordHash instances or None values will return unchanged.
        Strings will be hashed and the resulting PasswordHash returned.
        Any other input will result in a TypeError.
        """
        if isinstance(value, PasswordHash):
            return value
        elif isinstance(value, str):
            return PasswordHash.new(value)
        elif value is not None:
            raise TypeError("Cannot convert {} to a PasswordHash".format(type(value)))


str_16 = Annotated[str, 16]
str_36 = Annotated[str, 36]
str_80 = Annotated[str, 80]
str_120 = Annotated[str, 120]
str_255 = Annotated[str, 255]
text = Annotated[str, mapped_column(Text())]


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


class BaseModel(db.Model):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    resource_id: Mapped[uid.UUID] = mapped_column(
        UUID(as_uuid=True), unique=True, server_default=sa_text("uuid_generate_v4()")
    )
    created_at: Mapped[datetime.datetime] = mapped_column(server_default=db.func.now())
    updated_at: Mapped[datetime.datetime] = mapped_column(
        server_default=db.func.now(), onupdate=db.func.now()
    )

    def update(self, **kwargs):
        for key, value in kwargs.items():
            try:
                getattr(self, key)
                setattr(self, key, value)
            except AttributeError:
                pass

    def as_dict(self):
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}  # type: ignore


class TokenBlocklist(BaseModel):
    __tablename__ = "token_blocklist"

    jti: Mapped[str_36] = mapped_column(index=True)
    type: Mapped[str_16] = mapped_column()
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))

    def __init__(self, jti, ttype, user_id=None) -> None:
        self.jti = jti
        self.type = ttype
        if user_id:
            self.user_id = user_id


class User(BaseModel):
    __tablename__ = "users"

    fname: Mapped[Optional[str_80]]
    lname: Mapped[Optional[str_80]]
    email: Mapped[Optional[str_120]] = mapped_column(unique=True)
    password = mapped_column(Password())
    is_admin: Mapped[bool] = mapped_column(default=False)

    def __init__(self, email, password, fname=None, lname=None):
        self.fname = fname
        self.lname = lname
        self.email = email
        self.password = password

    @validates("password")
    def _validate_password(self, key, password):
        return getattr(type(self), key).type.validator(password)

    def __repr__(self):
        return f"<User {self.email}>"


class Event(BaseModel):
    __tablename__ = "events"

    name: Mapped[str_80]
    description: Mapped[text]
    start_date: Mapped[datetime.datetime]
    end_date: Mapped[datetime.datetime]
    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped["User"] = relationship(back_populates="events")

    def __init__(self, name, description, start_date, end_date, author_id):
        self.name = name
        self.description = description
        self.start_date = start_date
        self.end_date = end_date
        self.author_id = author_id

    def __repr__(self):
        return f"<Event {self.name}>"


class EventData(BaseModel):
    __tablename__ = "event_data"

    event_id: Mapped[int] = mapped_column(ForeignKey("events.id", ondelete="CASCADE"))
    event: Mapped["Event"] = relationship(
        back_populates="event_data", cascade="all, delete-orphan", passive_deletes=True
    )
    data: Mapped[JSON] = mapped_column(type_=JSON)
    timestamp: Mapped[datetime.datetime]

    def __init__(self, event_id, data, timestamp):
        self.event_id = event_id
        self.data = data
        self.timestamp = timestamp

    def __repr__(self):
        return f"<EventData {self.id}>"


class Alert(BaseModel):
    __tablename__ = "alerts"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="alerts")
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))
    event: Mapped["Event"] = relationship(back_populates="alerts")
    condition: Mapped[JSON] = mapped_column(type_=JSON)

    def __init__(self, user_id, event_id, condition):
        self.user_id = user_id
        self.event_id = event_id
        self.condition = condition

    def __repr__(self):
        return f"<Alert {self.id}>"


class Report(BaseModel):
    __tablename__ = "reports"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="reports")
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))
    event: Mapped["Event"] = relationship(back_populates="reports")
    filters: Mapped[JSON] = mapped_column(type_=JSON)
    format: Mapped[str_16]

    def __init__(self, user_id, event_id, filters, format):
        self.user_id = user_id
        self.event_id = event_id
        self.filters = filters
        self.format = format

    def __repr__(self):
        return f"<Report {self.id}>"


class Notification(BaseModel):
    __tablename__ = "notifications"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="notifications")
    event_id: Mapped[int] = mapped_column(ForeignKey("events.id"))
    event: Mapped["Event"] = relationship(back_populates="notifications")
    message: Mapped[str_255]
    read_status: Mapped[bool] = mapped_column(default=False)

    def __init__(self, user_id, event_id, message):
        self.user_id = user_id
        self.event_id = event_id
        self.message = message

    def __repr__(self):
        return f"<Notification {self.id}>"
