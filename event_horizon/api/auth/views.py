from http import HTTPStatus

from apiflask import APIBlueprint, EmptySchema, HTTPError
from flask import session

from event_horizon.api.auth.schemas import LoginRequestDTO, RegisterRequestDTO
from event_horizon.api.user.schemas import UserDTO
from event_horizon.extensions import db
from event_horizon.models import User

auth_bp = APIBlueprint("auth", __name__)


@auth_bp.get("/register")
@auth_bp.input(RegisterRequestDTO)
@auth_bp.output(UserDTO, status_code=HTTPStatus.CREATED)
def register(json_data):
    new_user = User(**json_data)
    user_exists = (
        db.session.query(User).filter(User.email == new_user.email).first() is not None  # type: ignore
    )

    if user_exists:
        raise HTTPError(HTTPStatus.BAD_REQUEST, f"{new_user.__repr__} already exists")

    db.session.add(new_user)
    db.session.commit()

    session["user"] = new_user.id

    return {"data": new_user}


@auth_bp.get("/login")
@auth_bp.input(LoginRequestDTO)
@auth_bp.output(UserDTO)
def login(json_data):
    user = db.session.query(User).filter(User.email == json_data["email"]).first()  # type: ignore

    if user is None:
        raise HTTPError(HTTPStatus.BAD_REQUEST, "user not found")

    if not user.password == json_data["password"]:
        raise HTTPError(HTTPStatus.UNAUTHORIZED, "incorrect password")

    session["user"] = user.id

    return {"data": user}


@auth_bp.get("/logout")
@auth_bp.output(EmptySchema, status_code=HTTPStatus.NO_CONTENT)
def logout():
    session.pop("user")
    return None


@auth_bp.get("/me")
@auth_bp.output(UserDTO)
def current_user():
    user_id = session.get("user")
    if user_id is None:
        raise HTTPError(HTTPStatus.UNAUTHORIZED, "user not logged in")

    user = db.get_or_404(User, user_id)

    return {"data": user}
