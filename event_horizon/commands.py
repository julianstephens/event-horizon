import random

from faker import Faker
from sqlalchemy.orm import configure_mappers

from event_horizon.models import Alert, Event, EventData, User

Faker.seed(random.randint(1000, 5000))
fake = Faker()


# Generate random events and event data
def generate_random_event():
    start_date = fake.date_time_this_year()
    return Event(
        name="Random Event",
        description="This is a randomly generated event",
        start_date=start_date,
        end_date=fake.past_datetime(start_date=start_date),
        author_id=random.randint(1, 11),
    )


def generate_random_event_data(event):
    return EventData(
        event_id=event.id,
        data={"key1": "value1"},
        timestamp=fake.date_time_between_dates(event.start_date, event.end_date),
    )


# Generate random alerts based on events
def generate_random_alert(event):
    if random.randint(0, 1) == 1:
        return Alert(
            condition={"key1": "value1"},
            user_id=random.randint(1, 11),
            event_id=event.id,
        )


def register_commands(app, db):
    @app.cli.command("initdb")
    def initdb():
        db.drop_all()
        configure_mappers()
        db.create_all()
        db.session.commit()

        if app.config["FLASK_ENV"] == "development":
            user = User(
                fname="Julian",
                lname="S",
                email="julian@julianstephens.net",
                password="thisI5asecurePassword!",
            )
            db.session.add(user)
            user.is_admin = True
            db.session.commit()
        if app.config["FLASK_ENV"] != "production":
            seen = set()
            for _ in range(0, 10):
                name = fake.unique.name().split(" ")
                if name[0] not in seen and not seen.add(name[0]):
                    pass
                else:
                    name = fake.unique.name().split(" ")

                pwd = fake.password(length=10, special_chars=True)
                user = User(
                    fname=name[0],
                    lname=name[1],
                    email=f"{name[0]}@your-mail.com",
                    password=pwd,
                )
                print(f"creating user: {user.fname} {user.lname}")
                db.session.add(user)
            db.session.commit()

            for _ in range(0, 100):
                event = generate_random_event()
                db.session.add(event)
                db.session.commit()

                event_data = generate_random_event_data(event)
                db.session.add(event_data)
                db.session.commit()

                alert = generate_random_alert(event)
                if alert:
                    db.session.add(alert)
                    db.session.commit()

        print(
            "Database initialized. You can now run the application using `flask run`."
        )
