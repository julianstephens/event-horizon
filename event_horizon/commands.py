from sqlalchemy.orm import configure_mappers

from event_horizon.models import User


def seed(app, db):
    db.drop_all()
    configure_mappers()
    db.create_all()

    if app.config["FLASK_ENV"] == "development":
        user = User(
            username="julians",
            email="julian@julianstephens.net",
            password="thisI5asecurePassword!",
        )
        db.session.add(user)
    if app.config["FLASK_ENV"] != "production":
        for i in range(0, 10):
            user = User(
                username=f"demoUser{i}",
                email=f"demo{i}@your-mail.com",
                password="Password1234!",
            )
            db.session.add(user)

    db.session.commit()

    print(
        f"Initialized the database{'' if app.config['FLASK_ENV'] == 'production' else ' with 10 users'}."
    )


def register_commands(app, db):
    @app.cli.command("initdb")
    def initdb():
        seed(app, db)
