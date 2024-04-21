from apiflask.fields import Email, String

from event_horizon.api import CamelCaseSchema


class LoginRequestDTO(CamelCaseSchema):
    email = Email(required=True)
    password = String(required=True)


class RegisterRequestDTO(LoginRequestDTO):
    fname = String()
    lname = String()
    email = Email(required=True)
    password = String(required=True)
