from apiflask import Schema
from apiflask.fields import DateTime, Integer, String
from apiflask.validators import Length


class EventDTO(Schema):
    id = Integer()
    name = String()
    description = String()
    start_date = DateTime()
    end_date = DateTime()
    created_at = DateTime()
    updated_at = DateTime()


class EventRequestDTO(Schema):
    name = String(required=True, validate=Length(max=100))
    description = String(required=True, validate=Length(max=500))
    start_date = DateTime(required=True)
    end_date = DateTime(required=True)
