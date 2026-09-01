from marshmallow import Schema, fields


class DayOfWorkSchema(Schema):
    id = fields.Str(dump_only=True)
    date = fields.Date(load_default=None)
    description = fields.Str(required=True)
    prisoner_id = fields.Str(dump_only=True)
