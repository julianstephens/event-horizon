from sqlalchemy.orm import validates

from event_horizon.extensions import db
from event_horizon.utils import Password


class BaseModel(db.Model):
    __abstract__ = True

    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now()
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


class User(BaseModel):
    __tablename__ = "users"

    fname = db.Column(db.String(80), nullable=True)
    lname = db.Column(db.String(80), nullable=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(Password(rounds=13), nullable=False)
    is_admin = db.Column(db.Boolean, nullable=False, default=False)

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

    name = db.Column(db.String(80), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    author = db.relationship("User", backref=db.backref("events", lazy=True))

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

    event_id = db.Column(
        db.Integer, db.ForeignKey("events.id", ondelete="CASCADE"), nullable=False
    )
    event = db.relationship(
        "Event", backref=db.backref("data", lazy=True, passive_deletes=True)
    )
    data = db.Column(db.JSON, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)

    def __init__(self, event_id, data, timestamp):
        self.event_id = event_id
        self.data = data
        self.timestamp = timestamp

    def __repr__(self):
        return f"<EventData {self.id}>"


class Alert(BaseModel):
    __tablename__ = "alerts"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", backref=db.backref("alerts", lazy=True))
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    event = db.relationship("Event", backref=db.backref("alerts", lazy=True))
    condition = db.Column(db.JSON, nullable=False)

    def __init__(self, user_id, event_id, condition):
        self.user_id = user_id
        self.event_id = event_id
        self.condition = condition

    def __repr__(self):
        return f"<Alert {self.id}>"


class Report(BaseModel):
    __tablename__ = "reports"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", backref=db.backref("reports", lazy=True))
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    event = db.relationship("Event", backref=db.backref("report_data", lazy=True))
    filters = db.Column(db.JSON, nullable=False)
    format = db.Column(db.String(10), nullable=False)

    def __init__(self, user_id, event_id, filters, format):
        self.user_id = user_id
        self.event_id = event_id
        self.filters = filters
        self.format = format

    def __repr__(self):
        return f"<Report {self.id}>"


class Notification(BaseModel):
    __tablename__ = "notifications"

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    user = db.relationship("User", backref=db.backref("notifications", lazy=True))
    event_id = db.Column(db.Integer, db.ForeignKey("events.id"), nullable=False)
    event = db.relationship("Event", backref=db.backref("notif_data", lazy=True))
    message = db.Column(db.String(255), nullable=False)
    read_status = db.Column(db.Boolean, nullable=False, default=False)

    def __init__(self, user_id, event_id, message):
        self.user_id = user_id
        self.event_id = event_id
        self.message = message

    def __repr__(self):
        return f"<Notification {self.id}>"
