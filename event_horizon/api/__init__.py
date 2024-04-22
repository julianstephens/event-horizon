from functools import wraps
from http import HTTPStatus

from apiflask import HTTPError, PaginationSchema, Schema
from apiflask.fields import Field, Integer, List, Nested, String
from apiflask.validators import Range
from flask_jwt_extended import verify_jwt_in_request


def camelcase(s):
    parts = iter(s.split("_"))
    return next(parts) + "".join(i.title() for i in parts)


class CamelCaseSchema(Schema):
    """Schema that uses camel-case for its external representation
    and snake-case for its internal representation.
    """

    def on_bind_field(self, field_name, field_obj):
        field_obj.data_key = camelcase(field_obj.data_key or field_name)


class MetadataSchema(CamelCaseSchema):
    resource_id = String(data_key="id")
    created_at = String()
    updated_at = String()


class PaginationQuery(CamelCaseSchema):
    page = Integer(load_default=1)
    per_page = Integer(load_default=20, validate=Range(1, 100))


class RelationSchema(CamelCaseSchema):
    rel = String()
    href = String()


class ResponseSchema(CamelCaseSchema):
    links = List(Nested(RelationSchema))
    data = Field()
    pagination = Nested(PaginationSchema)


def admin_required():
    def wrapper(fn):
        @wraps(fn)
        def decorator(*args, **kwargs):
            (_, jwt_data) = verify_jwt_in_request(fresh=True)
            if jwt_data["is_admin"]:
                return fn(*args, **kwargs)
            else:
                raise HTTPError(HTTPStatus.FORBIDDEN, "admin required")

        return decorator

    return wrapper
