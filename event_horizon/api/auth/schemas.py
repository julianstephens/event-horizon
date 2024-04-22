from apiflask.fields import Email, String

from event_horizon.api import CamelCaseSchema
from event_horizon.api.user.schemas import UserDTO


class AuthResponseDTO(CamelCaseSchema):
    user = UserDTO()
    access_token = String()
    refresh_token = String()


class LoginRequestDTO(CamelCaseSchema):
    email = Email(required=True)
    password = String(required=True)


class RegisterRequestDTO(LoginRequestDTO):
    fname = String()
    lname = String()
    email = Email(required=True)
    password = String(required=True)
