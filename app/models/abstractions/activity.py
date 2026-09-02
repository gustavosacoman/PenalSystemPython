import uuid
from datetime import date
from sqlalchemy.orm import declared_attr
from app.extensions import db

class Activity(db.Model):
    __abstract__ = True

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    date = db.Column(db.Date, nullable=False, default=date.today)

    @declared_attr
    def prisoner_id(cls):
        return db.Column(db.String(36), db.ForeignKey("prisoners.id"), nullable=False)

    @declared_attr
    def prisoner(cls):
        return db.relationship("Prisoner", back_populates=cls.__tablename__)