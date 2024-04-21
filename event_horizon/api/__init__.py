from apiflask import PaginationSchema, Schema
from apiflask.fields import Field, Integer, List, Nested, String
from apiflask.validators import Range


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
    id = Integer()
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
