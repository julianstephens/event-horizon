from flask_jwt_extended import JWTManager
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect
from event_horizon.models import Base

db = SQLAlchemy(model_class=Base)
csrf = CSRFProtect()
migrate = Migrate()
session = Session()
login_manager = LoginManager()
jwt_manager = JWTManager()
