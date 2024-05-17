from http import HTTPStatus

from apiflask import APIBlueprint, EmptySchema, HTTPError, pagination_builder
from flask_jwt_extended import jwt_required

from event_horizon.api import admin_required
from event_horizon.api.user.schemas import UserDTO, UserFilters, UserRequestDTO
from event_horizon.extensions import db
from event_horizon.models import Report, User
from event_horizon.utils import is_valid_uuid

user_bp = APIBlueprint("users", __name__)


@user_bp.get("/users")
@admin_required()
@user_bp.input(UserFilters, location="query")
@user_bp.output(UserDTO(many=True))
@user_bp.doc(security="BearerAuth")
async def list(query_data):
    paginated_users = db.paginate(
        db.select(User)
        if "with_reports" not in query_data or query_data["with_reports"] is False
        else db.select(User).join(Report),
        page=query_data["page"],
        per_page=query_data["per_page"],
    )

    return {
        "data": paginated_users.items,
        "pagination": pagination_builder(paginated_users),  # type: ignore
    }


@user_bp.get("/users/<string:id>")
@jwt_required()
@user_bp.input(UserFilters, location="query")
@user_bp.output(UserDTO)
@user_bp.doc(security="BearerAuth")
async def get(id, query_data):
    if id is None or not is_valid_uuid(id):
        raise HTTPError(HTTPStatus.BAD_REQUEST, "invalid user id", detail={"id": id})

    user = db.session.query(User).filter(User.resource_id == id).first()  # type: ignore
    if user is None:
        raise HTTPError(
            HTTPStatus.NOT_FOUND,
            "user not found",
            detail={"id": id, **({"query": query_data} if query_data else {})},
        )

    if query_data.get("with_reports"):
        user.reports = db.session.query(Report).filter(Report.user_id == user.id).all()
        user.reports = user.reports  # type: ignore

    return {"data": user}


@user_bp.post("/users")
@admin_required()
@user_bp.input(UserRequestDTO)
@user_bp.output(UserDTO, status_code=HTTPStatus.CREATED)
@user_bp.doc(security="BearerAuth")
async def create(json_data):
    new_user = User(**json_data)
    db.session.add(new_user)
    db.session.commit()
    return {"data": new_user}


@user_bp.patch("/users/<string:id>")
@jwt_required(fresh=True)
@user_bp.input(UserRequestDTO(partial=True))
@user_bp.output(UserDTO)
@user_bp.doc(security="BearerAuth")
async def update(id, json_data):
    if id is None or not is_valid_uuid(id):
        raise HTTPError(HTTPStatus.BAD_REQUEST, "invalid user id", detail={"id": id})

    user = db.session.query(User).filter(User.resource_id == id).first()  # type: ignore
    if user is None:
        raise HTTPError(HTTPStatus.NOT_FOUND, "user not found")

    for key, value in json_data.items():
        user.__setattr__(key, value)
    db.session.commit()
    return {"data": user}


@user_bp.delete("/users/<string:id>")
@admin_required()
@user_bp.output(EmptySchema, status_code=HTTPStatus.NO_CONTENT)
@user_bp.doc(security="BearerAuth")
async def delete(id):
    if id is None or not is_valid_uuid(id):
        raise HTTPError(HTTPStatus.BAD_REQUEST, "invalid user id", detail={"id": id})

    user = db.session.query(User).filter(User.resource_id == id).first()  # type: ignore
    if user is None:
        raise HTTPError(HTTPStatus.NOT_FOUND, "user not found")

    db.session.delete(user)
    db.session.commit()
    return
