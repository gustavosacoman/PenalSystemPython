from app.extensions import db
from app.models.abstractions.activity import Activity


class Book(Activity):
    __tablename__ = "books"

    isbn = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(150), nullable=False)

    def __repr__(self):
        return f"<Book {self.title} - Prisoner: {self.prisoner_id}>"