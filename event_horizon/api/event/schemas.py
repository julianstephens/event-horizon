from apiflask.fields import DateTime, Dict, Integer, String
from apiflask.validators import Length

from event_horizon.api import CamelCaseSchema, MetadataSchema


class EventDTO(MetadataSchema):
    name = String()
    description = String()
    start_date = DateTime()
    end_date = DateTime()


class EventRequestDTO(CamelCaseSchema):
    name = String(required=True, validate=Length(max=100))
    description = String(required=True, validate=Length(max=500))
    start_date = DateTime(required=True)
    end_date = DateTime(required=True)
    author_id = Integer(required=True)


class EventDataDTO(MetadataSchema):
    data = Dict()
    timestamp = DateTime()


class EventDataRequestDTO(CamelCaseSchema):
    data = Dict(required=True)
    timestamp = DateTime(required=True)
