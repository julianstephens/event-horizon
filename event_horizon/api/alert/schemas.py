from apiflask.fields import Dict, Integer, String

from event_horizon.api import CamelCaseSchema, MetadataSchema


class AlertDTO(MetadataSchema):
    condition = Dict()
    updated_at = String()


class AlertRequestDTO(CamelCaseSchema):
    user_id = Integer(required=True)
    event_id = Integer(required=True)
    condition = Dict(required=True)
