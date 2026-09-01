from datetime import date
from marshmallow import Schema, fields, validates, ValidationError

class PrisonerSchema(Schema):

    id = fields.Str(dump_only=True)
    name = fields.Str(required=True)
    cpf = fields.Str(required=True)
    birth_date = fields.Date(required=True)
    arrival_date = fields.Date(required=True)
    original_release_date = fields.Date(required=True)
    updated_release_date = fields.Date(dump_only=True)
    books_counter = fields.Int(dump_only=True)
    current_year = fields.Int(dump_only=True)

    @validates("arrival_date")
    def validate_arrival_date(self, value, **kwargs):
        if value < date.today():
            raise ValidationError("Arrival date cannot be in the past.")

    @validates("original_release_date")
    def validate_release_date(self, value, **kwargs):
        if value < date.today():
            raise ValidationError("Original release date cannot be in the past.")

class UpdatePrisonerSchema(PrisonerSchema):
    pass