import os
from http import HTTPStatus

from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.wrappers import Response

from event_horizon import create_app

app = create_app(os.getenv("FLASK_ENV", "development"))

app.wsgi_app = DispatcherMiddleware(
    Response("Not Found", status=HTTPStatus.NOT_FOUND), {"/api": app.wsgi_app}
)
