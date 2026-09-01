from app.extensions import db
from app.models.abstractions.activity import Activity

class DayOfWork(Activity):
    __tablename__ = 'days_of_work'

    description = db.Column(db.String(200), nullable=False)
