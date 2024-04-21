from http import HTTPStatus

from apiflask import APIBlueprint, EmptySchema, pagination_builder

from event_horizon.api import PaginationQuery
from event_horizon.api.event.schemas import (
    EventDataDTO,
    EventDataRequestDTO,
    EventDTO,
    EventRequestDTO,
)
from event_horizon.extensions import db
from event_horizon.models import Event, EventData
from event_horizon.utils import generate_links

event_bp = APIBlueprint("events", __name__)


@event_bp.get("/events")
@event_bp.input(PaginationQuery, location="query")
@event_bp.output(EventDTO(many=True))
async def list(query_data):
    paginated_events = db.paginate(
        db.select(Event).order_by(Event.created_at.desc()),
        page=query_data["page"],
        per_page=query_data["per_page"],
    )
    return {
        "data": paginated_events.items,
        "pagination": pagination_builder(paginated_events),  # type: ignore
    }


@event_bp.get("/events/<int:id>")
@event_bp.output(EventDTO)
async def get(id):
    event = db.get_or_404(Event, id)
    links = (
        generate_links("alerts", [f"/alerts/{alert.id}" for alert in event.alerts])  # type: ignore
        if len(event.alerts) > 0  # type: ignore
        else None
    )
    return {"data": event, **({"links": links} if links else {})}


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
    event = db.get_or_404(Event, id)
    for key, value in json_data.items():
        event.__setattr__(key, value)
    db.session.commit()
    return {"data": event}


@event_bp.delete("/events/<int:id>")
@event_bp.output(EmptySchema, status_code=HTTPStatus.NO_CONTENT)
async def delete(id):
    event = db.get_or_404(Event, id)
    db.session.delete(event)
    db.session.commit()
    return None


@event_bp.get("/events/<int:id>/data")
@event_bp.output(EventDataDTO)
async def get_data(id):
    event_data = db.session.query(EventData).filter(EventData.event_id == id).all()  # type: ignore
    return {"data": event_data}


@event_bp.post("/events/<int:id>/data")
@event_bp.input(EventDataRequestDTO)
@event_bp.output(EventDataDTO, status_code=HTTPStatus.CREATED)
async def create_data(id, json_data):
    new_event = EventData(**json_data, event_id=id)
    db.session.add(new_event)
    db.session.commit()
    return {"data": new_event}


@event_bp.put("/events/<int:id>/data/<int:data_id>")
@event_bp.input(EventDataRequestDTO)
@event_bp.output(EventDataDTO)
async def update_data(id, data_id, json_data):
    data = db.get_or_404(EventData, data_id)
    for key, value in json_data.items():
        data.__setattr__(key, value)
    db.session.commit()
    return {"data": data}
