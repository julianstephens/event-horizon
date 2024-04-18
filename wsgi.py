import os

from event_horizon import create_app

app = create_app(os.getenv("FLASK_ENV", "development"))
