from http import HTTPStatus

from apiflask import APIBlueprint, EmptySchema, pagination_builder

from event_horizon.api import PaginationQuery
from event_horizon.api.event.schemas import EventDTO, EventRequestDTO
from event_horizon.extensions import db
from event_horizon.models import Event

event_bp = APIBlueprint("event", __name__)


@event_bp.get("/events")
@event_bp.input(PaginationQuery, location="query")
@event_bp.output(EventDTO(many=True))
async def list(query_data):
    paginated_events = Event.query.paginate(
        page=query_data["page"], per_page=query_data["per_page"]
    )
    return {
        "data": paginated_events.items,
        "pagination": pagination_builder(paginated_events),  # type: ignore
    }


@event_bp.get("/events/<int:id>")
@event_bp.output(EventDTO)
async def get(id):
    event = Event.query.get_or_404(id)
    return {"data": event}


@event_bp.post("/events")
@event_bp.input(EventRequestDTO)
@event_bp.output(EventDTO, status_code=HTTPStatus.CREATED)
async def create(json_data):
    new_event = Event(**json_data)
    db.session.add(new_event)
    db.session.commit()
    return {"data": new_event}


@event_bp.put("/events/<int:id>")
@event_bp.input(EventRequestDTO(partial=True))
@event_bp.output(EventDTO)
async def update(id, json_data):
    event = Event.query.get_or_404(id)
    for key, value in json_data.items():
        event.__setattr__(key, value)
    db.session.commit()
    return {"data": event}


@event_bp.delete("/events/<int:id>")
@event_bp.output(EmptySchema, status_code=HTTPStatus.NO_CONTENT)
async def delete(id):
    event = Event.query.get_or_404(id)
    db.session.delete(event)
    db.session.commit()
    return None
