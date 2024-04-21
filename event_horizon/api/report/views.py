from http import HTTPStatus

from apiflask import APIBlueprint, EmptySchema, pagination_builder

from event_horizon.api import PaginationQuery
from event_horizon.api.report.schemas import ReportDTO, ReportRequestDTO
from event_horizon.extensions import db
from event_horizon.models import Report
from event_horizon.utils import generate_links

report_bp = APIBlueprint("reports", __name__)


@report_bp.get("/reports")
@report_bp.input(PaginationQuery, location="query")
@report_bp.output(ReportDTO(many=True))
async def list(query_data):
    paginated_reports = db.paginate(
        db.select(Report), page=query_data["page"], per_page=query_data["per_page"]
    )

    return {
        "data": paginated_reports.items,
        "pagination": pagination_builder(paginated_reports),  # type: ignore
    }


@report_bp.get("/reports/<int:id>")
@report_bp.output(ReportDTO)
async def get(id):
    report = db.get_or_404(Report, id)
    links = (
        generate_links("events", [f"/{event.id}" for event in report.events])  # type: ignore
        if len(report.events) > 0  # type: ignore
        else None
    )
    return {"data": report, **({"links": links} if links else {})}


@report_bp.post("/reports")
@report_bp.input(ReportRequestDTO)
@report_bp.output(ReportDTO, status_code=HTTPStatus.CREATED)
async def create(json_data):
    new_report = Report(**json_data)
    db.session.add(new_report)
    db.session.commit()
    return {"data": new_report}


@report_bp.patch("/reports/<int:id>")
@report_bp.input(ReportRequestDTO(partial=True))
@report_bp.output(ReportDTO)
async def update(id, json_data):
    report = db.get_or_404(Report, id)
    for key, value in json_data.items():
        report.__setattr__(key, value)
    db.session.commit()
    return {"data": report}


@report_bp.delete("/reports/<int:id>")
@report_bp.output(EmptySchema, status_code=HTTPStatus.NO_CONTENT)
async def delete(id):
    report = db.get_or_404(Report, id)
    db.session.delete(report)
    db.session.commit()
    return None
