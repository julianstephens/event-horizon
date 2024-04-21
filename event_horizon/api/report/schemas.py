from apiflask.fields import Dict, Integer, String

from event_horizon.api import CamelCaseSchema, MetadataSchema


class ReportDTO(MetadataSchema):
    filters = Dict()
    format = String()


class ReportRequestDTO(CamelCaseSchema):
    user_id = Integer(required=True)
    event_id = Integer(required=True)
    condition = Dict(required=True)
