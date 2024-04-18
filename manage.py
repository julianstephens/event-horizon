from sqlalchemy.orm import configure_mappers

from event_horizon import create_app
from event_horizon.extensions import db
from event_horizon.models import User

app = create_app()


@app.cli.command("initdb")
def initdb():
    db.drop_all()
    configure_mappers()
    db.create_all()

    for _ in range(1, 2):
        user = User(
            username="Demo User",
            email="demo@your-mail.com",
            password="demopassword",
        )
        db.session.add(user)

    db.session.commit()

    print("Initialized the database with 1 user.")
