from apiflask.fields import Boolean, Email, String
from apiflask.validators import Length

from event_horizon.api import CamelCaseSchema, MetadataSchema


class UserDTO(MetadataSchema):
    username = String()
    email = Email()
    is_admin = Boolean()


class UserRequestDTO(CamelCaseSchema):
    username = String(validate=Length(1, 20))
    email = Email()
    password = String(validate=Length(10, 24))
