from apiflask.fields import Boolean, DateTime, Dict, Integer, Nested, String
from apiflask.validators import Length

from event_horizon.api import CamelCaseSchema, MetadataSchema, PaginationQuery
from event_horizon.api.alert.schemas import AlertDTO


class EventFilters(PaginationQuery):
    with_data = Boolean()
    with_alerts = Boolean()


class EventDataDTO(MetadataSchema):
    data = Dict(required=True)
    timestamp = DateTime(required=True)


class EventDataRequestDTO(CamelCaseSchema):
    data = Dict(required=True)
    timestamp = DateTime(required=True)


class EventDTO(MetadataSchema):
    name = String(required=True)
    description = String(required=True)
    start_date = DateTime(required=True)
    end_date = DateTime(required=True)
    event_data = Nested(EventDataDTO(many=True))
    alerts = Nested(AlertDTO(many=True))


class EventRequestDTO(CamelCaseSchema):
    name = String(required=True, validate=Length(max=100))
    description = String(required=True, validate=Length(max=500))
    start_date = DateTime(required=True)
    end_date = DateTime(required=True)
    author_id = Integer(required=True)
