import uuid
from datetime import date
from email.policy import default

from app.extensions import db


class Prisoner(db.Model):
    __tablename__ = "prisoners"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))

    name = db.Column(db.String(150), nullable=False)
    birth_date = db.Column(db.Date, nullable=False)
    cpf = db.Column(db.String(14), unique=True, nullable=False)

    arrival_date = db.Column(db.Date, nullable=False)
    original_release_date = db.Column(db.Date, nullable=False)
    updated_release_date = db.Column(db.Date, nullable=False)
    books_counter = db.Column(db.Integer, default=0,  nullable=False)
    current_year = db.Column(db.Integer, nullable=False)

    def __repr__(self):
        return f"<Prisoner {self.name} - CPF: {self.cpf}>"