from http import HTTPStatus

from apiflask import APIBlueprint, EmptySchema, HTTPError, pagination_builder
from flask_jwt_extended import jwt_required

from event_horizon.api import admin_required
from event_horizon.api.event.schemas import (
    EventDataDTO,
    EventDataRequestDTO,
    EventDTO,
    EventFilters,
    EventRequestDTO,
)
from event_horizon.extensions import db
from event_horizon.models import Event, EventData
from event_horizon.utils import generate_links, is_valid_uuid

event_bp = APIBlueprint("events", __name__)


@event_bp.get("/events")
@jwt_required()
@event_bp.input(EventFilters, location="query")
@event_bp.output(EventDTO(many=True))
async def list(query_data):
    paginated_events = db.paginate(
        db.select(Event).order_by(Event.created_at.desc())
        if "with_data" in query_data and not query_data["with_data"]
        else db.select(Event).order_by(Event.created_at.desc()).join(EventData),  # type: ignore
        page=query_data["page"],
        per_page=query_data["per_page"],
    )
    return {
        "data": paginated_events.items,
        "pagination": pagination_builder(paginated_events),  # type: ignore
    }


@event_bp.get("/events/<string:id>")
@jwt_required()
@event_bp.input(EventFilters, location="query")
@event_bp.output(EventDTO)
async def get(id, query_data):
    event = {}
    event_data = None

    if id is None or not is_valid_uuid(id):
        raise HTTPError(HTTPStatus.BAD_REQUEST, "invalid event id", detail={"id": id})

    event = db.session.query(Event).filter(Event.resource_id == id).first()  # type: ignore
    if event is None:
        raise HTTPError(
            HTTPStatus.NOT_FOUND,
            "event not found",
            detail={"id": id, **({"query": query_data} if query_data else {})},
        )

    if "with_data" in query_data and query_data["with_data"]:
        event_data = db.session.query(EventData).filter(EventData.event_id == id).all()
        event.event_data = event_data  # type: ignore

    links = (
        generate_links(
            "alerts", [f"/alerts/{alert.resource_id}" for alert in event.alerts]
        )
        if len(event.alerts) > 0  # type: ignore
        else None
    )
    return {
        "data": event,
        **({"links": links} if links else {}),
    }


@event_bp.post("/events")
@jwt_required(fresh=True)
@event_bp.input(EventRequestDTO)
@event_bp.output(EventDTO, status_code=HTTPStatus.CREATED)
async def create(json_data):
    new_event = Event(**json_data)
    db.session.add(new_event)
    db.session.commit()
    return {"data": new_event}


@event_bp.put("/events/<string:id>")
@jwt_required(fresh=True)
@event_bp.input(EventRequestDTO(partial=True))
@event_bp.output(EventDTO)
async def update(id, json_data):
    if id is None or not is_valid_uuid(id):
        raise HTTPError(HTTPStatus.BAD_REQUEST, "invalid event id", detail={"id": id})

    event = db.session.query(Event).filter(Event.resource_id == id).first()  # type: ignore
    if event is None:
        raise HTTPError(HTTPStatus.NOT_FOUND, "event not found")

    for key, value in json_data.items():
        event.__setattr__(key, value)
    db.session.commit()
    return {"data": event}


@event_bp.delete("/events/<string:id>")
@admin_required()
@event_bp.output(EmptySchema, status_code=HTTPStatus.NO_CONTENT)
async def delete(id):
    if id is None or not is_valid_uuid(id):
        raise HTTPError(HTTPStatus.BAD_REQUEST, "invalid event id", detail={"id": id})

    event = db.session.query(Event).filter(Event.resource_id == id).first()  # type: ignore
    if event is None:
        raise HTTPError(HTTPStatus.NOT_FOUND, "event not found")

    db.session.delete(event)
    db.session.commit()
    return None


@event_bp.get("/events/<string:id>/data")
@jwt_required()
@event_bp.output(EventDataDTO)
async def get_data(id):
    if id is None or not is_valid_uuid(id):
        raise HTTPError(HTTPStatus.BAD_REQUEST, "invalid event id", detail={"id": id})

    event_data = db.session.query(EventData).filter(EventData.event_id == id).all()  # type: ignore
    return {"data": event_data}


@event_bp.post("/events/<string:id>/data")
@event_bp.input(EventDataRequestDTO)
@jwt_required(fresh=True)
@event_bp.output(EventDataDTO, status_code=HTTPStatus.CREATED)
async def create_data(id, json_data):
    if id is None or not is_valid_uuid(id):
        raise HTTPError(HTTPStatus.BAD_REQUEST, "invalid event id", detail={"id": id})

    new_event = EventData(**json_data, event_id=id)
    db.session.add(new_event)
    db.session.commit()
    return {"data": new_event}


@event_bp.put("/events/<string:id>/data/<int:data_id>")
@jwt_required(fresh=True)
@event_bp.input(EventDataRequestDTO)
@event_bp.output(EventDataDTO)
async def update_data(id, data_id, json_data):
    if id is None or not is_valid_uuid(id):
        raise HTTPError(HTTPStatus.BAD_REQUEST, "invalid event id", detail={"id": id})
    if data_id is None or not is_valid_uuid(data_id):
        raise HTTPError(
            HTTPStatus.BAD_REQUEST, "invalid event data id", detail={"id": id}
        )

    data = db.session.query(EventData).filter(EventData.resource_id == data_id).first()  # type: ignore
    if data is None:
        raise HTTPError(HTTPStatus.NOT_FOUND, "event data not found")
    for key, value in json_data.items():
        data.__setattr__(key, value)
    db.session.commit()
    return {"data": data}
