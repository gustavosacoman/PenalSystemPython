from datetime import date
from marshmallow import Schema, fields, validates, ValidationError


class StudySchema(Schema):
    id = fields.Str(dump_only=True)
    prisoner_id = fields.Str(required=True)
    date = fields.Date()
    subject = fields.Str(required=True)

    @validates("date")
    def validate_date(self, value, **kwargs):
        if value is not None and value > date.today():
            raise ValidationError("Study date cannot be in the future.")
    

