from datetime import date, timedelta

from app.extensions import db
from app.models.book import Book
from app.services.prisoner_service import get_by_id as get_prisoner_by_id, get_by_cpf
from app.errors import ResourceNotFound, BusinessRuleViolation

MAX_BOOKS_PER_YEAR = 12
DAYS_REDUCTION = 3


def _resolve_prisoner(identifier: str):
    if len(identifier) == 36:
        return get_prisoner_by_id(identifier)
    return get_by_cpf(identifier)


def _reset_counter_if_new_year(prisoner) -> None:
    current_year = date.today().year
    if prisoner.current_year != current_year:
        prisoner.books_counter = 0
        prisoner.current_year = current_year


def _register_reading(prisoner) -> None:
    _reset_counter_if_new_year(prisoner)

    if prisoner.books_counter >= MAX_BOOKS_PER_YEAR:
        raise BusinessRuleViolation(
            f"Prisoner reached the maximum of {MAX_BOOKS_PER_YEAR} books this year"
        )

    prisoner.books_counter += 1
    prisoner.updated_release_date -= timedelta(days=DAYS_REDUCTION)


def _unregister_reading(prisoner) -> None:
    prisoner.books_counter -= 1
    prisoner.updated_release_date += timedelta(days=DAYS_REDUCTION)


def build_query(filters: dict, prisoner_id: str | None = None):
    query = db.select(Book)

    if prisoner_id:
        query = query.where(Book.prisoner_id == prisoner_id)

    title = filters.get("title")
    if title:
        query = query.where(Book.title.ilike(f"%{title}%"))

    author = filters.get("author")
    if author:
        query = query.where(Book.author.ilike(f"%{author}%"))

    isbn = filters.get("isbn")
    if isbn:
        query = query.where(Book.isbn == isbn)

    return query.order_by(Book.date.desc())


def build_query_for_prisoner(identifier: str, filters: dict):
    prisoner = _resolve_prisoner(identifier)
    return build_query(filters, prisoner_id=prisoner.id)


def get_all() -> list[Book]:
    return list(db.session.scalars(db.select(Book)))


def get_by_id(book_id: str) -> Book:
    book = db.session.get(Book, book_id)
    if not book:
        raise ResourceNotFound("Book not found")
    return book


def get_by_prisoner(identifier: str) -> list[Book]:
    prisoner = _resolve_prisoner(identifier)
    return list(
        db.session.scalars(db.select(Book).where(Book.prisoner_id == prisoner.id))
    )


def create(identifier: str, data: dict) -> Book:
    prisoner = _resolve_prisoner(identifier)

    isbn = data["isbn"]
    if db.session.scalar(db.select(Book).where(Book.isbn == isbn)):
        raise BusinessRuleViolation("Book with this ISBN already registered")

    book = Book(
        isbn=isbn,
        title=data["title"],
        author=data["author"],
        date=data.get("date"),
        prisoner_id=prisoner.id,
    )

    _register_reading(prisoner)

    db.session.add(book)
    db.session.commit()
    return book


def update(book_id: str, data: dict) -> Book:
    book = get_by_id(book_id)

    new_isbn = data.get("isbn")
    if new_isbn and new_isbn != book.isbn:
        if db.session.scalar(db.select(Book).where(Book.isbn == new_isbn)):
            raise BusinessRuleViolation("Book with this ISBN already registered")

    new_prisoner_id = data.get("prisoner_id")
    if new_prisoner_id and new_prisoner_id != book.prisoner_id:
        old_prisoner = get_prisoner_by_id(book.prisoner_id)
        new_prisoner = get_prisoner_by_id(new_prisoner_id)

        _register_reading(new_prisoner)
        _unregister_reading(old_prisoner)

    for key, value in data.items():
        setattr(book, key, value)

    db.session.commit()
    return book


def delete(book_id: str) -> None:
    book = get_by_id(book_id)
    prisoner = get_prisoner_by_id(book.prisoner_id)

    _unregister_reading(prisoner)

    db.session.delete(book)
    db.session.commit()
