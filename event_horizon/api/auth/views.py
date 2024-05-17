from http import HTTPStatus

from apiflask import APIBlueprint, HTTPError
from apiflask.fields import String
from flask import session
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    current_user,
    get_jwt,
    jwt_required,
)

from event_horizon.api.auth.schemas import (
    AuthResponseDTO,
    LoginRequestDTO,
    RegisterRequestDTO,
)
from event_horizon.api.user.schemas import UserDTO
from event_horizon.extensions import db
from event_horizon.models import TokenBlocklist, User

auth_bp = APIBlueprint("auth", __name__, url_prefix="/auth")


@auth_bp.post("/register")
@auth_bp.input(RegisterRequestDTO)
@auth_bp.output(AuthResponseDTO, status_code=HTTPStatus.CREATED)
def register(json_data):
    user_exists = (
        db.session.query(User).filter(User.email == json_data["email"]).first()  # type: ignore
        is not None
    )
    if user_exists:
        raise HTTPError(
            HTTPStatus.ACCEPTED,
            "user already exists",
            detail={"email": json_data["email"]},
        )

    new_user = User(**json_data)
    access_token = create_access_token(
        identity=new_user.email,
        additional_claims={"is_admin": new_user.is_admin},
        fresh=True,
    )
    refresh_token = create_refresh_token(
        identity=new_user.email, additional_claims={"is_admin": new_user.is_admin}
    )

    try:
        db.session.add(new_user)
        db.session.commit()
        session["user"] = new_user.id
    except Exception as ex:
        db.session.rollback()
        raise HTTPError(HTTPStatus.UNAUTHORIZED, "failed to create user") from ex
    else:
        return {
            "data": {
                "user": new_user,
                "access_token": access_token,
                "refresh_token": refresh_token,
            }
        }


@auth_bp.post("/login")
@auth_bp.input(LoginRequestDTO)
@auth_bp.output(AuthResponseDTO)
def login(json_data):
    user = db.session.query(User).filter(User.email == json_data["email"]).first()  # type: ignore
    del user.reports

    if user is None:
        raise HTTPError(
            HTTPStatus.BAD_REQUEST,
            "user not found",
            detail={"email": json_data["email"]},
        )

    if user.password != json_data["password"]:
        raise HTTPError(HTTPStatus.UNAUTHORIZED, "incorrect password")

    access_token = create_access_token(
        identity=user.email, additional_claims={"is_admin": user.is_admin}, fresh=True
    )
    refresh_token = create_refresh_token(
        identity=user.email, additional_claims={"is_admin": user.is_admin}
    )

    return {
        "data": {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    }


@auth_bp.post("/refresh")
@jwt_required(refresh=True)
@auth_bp.output(
    {"access_token": String(required=True)}, schema_name="RefreshReponseDTO"
)
def refresh():
    access_token = create_access_token(identity=current_user, fresh=False)
    return {"data": {"access_token": access_token}}


@auth_bp.delete("/logout")
@jwt_required(verify_type=False)
@auth_bp.output({"message": String(required=True)}, schema_name="LogoutResponseDTO")
@auth_bp.doc(security="BearerAuth")
def logout():
    token = get_jwt()
    jti = token["jti"]
    ttype = token["type"]
    db.session.add(TokenBlocklist(jti=jti, ttype=ttype))
    db.session.commit()

    return {"data": {"message": f"{ttype.capitalize()} token successfully revoked"}}


@auth_bp.get("/me")
@jwt_required()
@auth_bp.output(UserDTO)
def whoami():
    user = db.session.query(User).filter(User.email == current_user.email).first()  # type: ignore
    return {"data": user}
