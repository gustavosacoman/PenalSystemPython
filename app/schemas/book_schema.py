from datetime import date
from marshmallow import Schema, fields, validates, ValidationError

class BookSchema(Schema):

    id = fields.Str(dump_only=True)
    prisoner_id = fields.Str(dump_only=True)
    date = fields.Date(load_default=None)
    isbn = fields.Str(required=True)
    title = fields.Str(required=True)
    author = fields.Str(required=True)

    @validates("date")
    def validate_date(self, value, **kwargs):
        if value is not None and value > date.today():
            raise ValidationError("Reading date cannot be in the future.")

class UpdateBookSchema(BookSchema):
    prisoner_id = fields.Str(required=False)
