from http import HTTPStatus

from apiflask import APIBlueprint, EmptySchema, pagination_builder

from event_horizon.api import PaginationQuery
from event_horizon.api.user.schemas import UserDTO, UserRequestDTO
from event_horizon.extensions import db
from event_horizon.models import User

user_bp = APIBlueprint("user", __name__)


@user_bp.get("/users")
@user_bp.input(PaginationQuery, location="query")
@user_bp.output(UserDTO(many=True))
async def list(query_data):
    paginated_users = db.paginate(
        db.select(User), page=query_data["page"], per_page=query_data["per_page"]
    )

    return {
        "data": paginated_users.items,
        "pagination": pagination_builder(paginated_users),  # type: ignore
    }


@user_bp.get("/users/<int:id>")
@user_bp.output(UserDTO)
async def get(id):
    user = db.get_or_404(User, id)
    return {"data": user}


@user_bp.post("/users")
@user_bp.input(UserRequestDTO)
@user_bp.output(UserDTO, status_code=HTTPStatus.CREATED)
async def create(json_data):
    new_user = User(**json_data)
    db.session.add(new_user)
    db.session.commit()
    return {"data": new_user}


@user_bp.patch("/users/<int:id>")
@user_bp.input(UserRequestDTO(partial=True))
@user_bp.output(UserDTO)
async def update(id, json_data):
    user = db.get_or_404(User, id)
    for key, value in json_data.items():
        user.__setattr__(key, value)
    db.session.commit()
    return {"data": user}


@user_bp.delete("/users/<int:id>")
@user_bp.output(EmptySchema, status_code=HTTPStatus.NO_CONTENT)
async def delete(id):
    user = db.get_or_404(User, id)
    db.session.delete(user)
    db.session.commit()
    return None
