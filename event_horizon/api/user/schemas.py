from apiflask.fields import Boolean, Email, String
from apiflask.validators import Length

from event_horizon.api import CamelCaseSchema, MetadataSchema


class UserDTO(MetadataSchema):
    fname = String()
    lname = String()
    email = Email(required=True)
    is_admin = Boolean(required=True)


class UserRequestDTO(CamelCaseSchema):
    fname = String(validate=Length(1, 80))
    lname = String(validate=Length(1, 80))
    email = Email(required=True)
    password = String(required=True, validate=Length(10, 24))
