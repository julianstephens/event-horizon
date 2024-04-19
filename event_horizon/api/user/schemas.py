from apiflask.fields import Email, String
from apiflask.validators import Length

from event_horizon.api import CamelCaseSchema


class UserDTO(CamelCaseSchema):
    id = String()
    username = String()
    email = Email()
    created_at = String()
    updated_at = String()


class UserRequestDTO(CamelCaseSchema):
    username = String(validate=Length(1, 20))
    email = Email()
    password = String(validate=Length(10, 24))
