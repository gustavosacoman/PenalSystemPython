from app.extensions import db
from app.models.abstractions.activity import Activity

class Study(Activity):
    __tablename__ = 'studies'
    subject = db.Column(db.String(200), nullable=False)