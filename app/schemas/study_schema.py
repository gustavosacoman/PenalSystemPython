from marshmallow import Schema, fields


class StudySchema(Schema):
    id = fields.Str(dump_only=True)
    prisoner_id = fields.Str(required=True)
    date = fields.Date(load_default=None)
    subject = fields.Str(required=True)
    

