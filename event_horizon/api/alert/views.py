from http import HTTPStatus

from apiflask import APIBlueprint, EmptySchema, HTTPError, pagination_builder

from event_horizon.api import PaginationQuery
from event_horizon.api.alert.schemas import AlertDTO, AlertRequestDTO
from event_horizon.extensions import db
from event_horizon.models import Alert

alert_bp = APIBlueprint("alerts", __name__)


@alert_bp.get("/alerts")
@alert_bp.input(PaginationQuery, location="query")
@alert_bp.output(AlertDTO(many=True))
async def list(query_data):
    paginated_alerts = db.paginate(
        db.select(Alert), page=query_data["page"], per_page=query_data["per_page"]
    )

    return {
        "data": paginated_alerts.items,
        "pagination": pagination_builder(paginated_alerts),  # type: ignore
    }


@alert_bp.get("/alerts/<string:id>")
@alert_bp.output(AlertDTO)
async def get(id):
    alert = db.session.query(Alert).filter(Alert.resource_id == id).first()  # type: ignore
    if alert is None:
        raise HTTPError(HTTPStatus.NOT_FOUND, "alert not found")
    return {"data": alert}


@alert_bp.post("/alerts")
@alert_bp.input(AlertRequestDTO)
@alert_bp.output(AlertDTO, status_code=HTTPStatus.CREATED)
async def create(json_data):
    new_alert = Alert(**json_data)
    db.session.add(new_alert)
    db.session.commit()
    return {"data": new_alert}


@alert_bp.patch("/alerts/<string:id>")
@alert_bp.input(AlertRequestDTO(partial=True))
@alert_bp.output(AlertDTO)
async def update(id, json_data):
    alert = db.session.query(Alert).filter(Alert.resource_id == id).first()  # type: ignore
    if alert is None:
        raise HTTPError(HTTPStatus.NOT_FOUND, "alert not found")

    for key, value in json_data.items():
        alert.__setattr__(key, value)
    db.session.commit()
    return {"data": alert}


@alert_bp.delete("/alerts/<string:id>")
@alert_bp.output(EmptySchema, status_code=HTTPStatus.NO_CONTENT)
async def delete(id):
    alert = db.session.query(Alert).filter(Alert.resource_id == id).first()  # type: ignore
    if alert is None:
        raise HTTPError(HTTPStatus.NOT_FOUND, "alert not found")

    db.session.delete(alert)
    db.session.commit()
    return None
