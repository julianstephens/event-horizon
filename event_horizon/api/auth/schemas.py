from apiflask.fields import Email, Nested, String

from event_horizon.api import CamelCaseSchema
from event_horizon.api.user.schemas import UserDTO


class AuthResponseDTO(CamelCaseSchema):
    user = Nested(UserDTO(), required=True)
    access_token = String(required=True)
    refresh_token = String(required=True)


class LoginRequestDTO(CamelCaseSchema):
    email = Email(required=True)
    password = String(required=True)


class RegisterRequestDTO(LoginRequestDTO):
    fname = String()
    lname = String()
    email = Email(required=True)
    password = String(required=True)
