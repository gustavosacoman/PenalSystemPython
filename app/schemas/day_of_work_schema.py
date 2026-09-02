from datetime import date
from marshmallow import Schema, fields, validates, ValidationError


class DayOfWorkSchema(Schema):
    id = fields.Str(dump_only=True)
    date = fields.Date(load_default=None)
    description = fields.Str(required=True)
    prisoner_id = fields.Str(dump_only=True)

    @validates("date")
    def validate_date(self, value, **kwargs):
        if value is not None and value > date.today():
            raise ValidationError("Work date cannot be in the future.")


class UpdateDayOfWorkSchema(DayOfWorkSchema):
    pass
