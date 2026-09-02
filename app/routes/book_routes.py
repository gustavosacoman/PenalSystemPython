from flask import Blueprint, request, jsonify
from app.services import book_service
from app.schemas.book_schema import BookSchema, UpdateBookSchema

bp = Blueprint("books", __name__)

book_schema = BookSchema()
books_schema = BookSchema(many=True)
patch_schema = UpdateBookSchema(partial=True)

@bp.get("/books/")
def get_all():
    books = book_service.get_all()
    return jsonify(books_schema.dump(books)), 200

@bp.get("/books/<book_id>")
def get_one(book_id: str):
    book = book_service.get_by_id(book_id)
    return jsonify(book_schema.dump(book)), 200

@bp.get("/prisoners/<identifier>/books")
def get_by_prisoner(identifier: str):
    books = book_service.get_by_prisoner(identifier)
    return jsonify(books_schema.dump(books)), 200

@bp.post("/prisoners/<identifier>/books")
def create(identifier: str):
    data = book_schema.load(request.json)
    book = book_service.create(identifier, data)
    return jsonify({"message": "Book registered successful!", "data": book_schema.dump(book)}), 201

@bp.put("/books/<book_id>")
def update(book_id: str):
    data = UpdateBookSchema().load(request.json)
    book = book_service.update(book_id, data)
    return jsonify({"message": "Book updated successful!", "data": book_schema.dump(book)}), 200

@bp.patch("/books/<book_id>")
def patch(book_id: str):
    data = patch_schema.load(request.json)
    book = book_service.update(book_id, data)
    return jsonify({"message": "Book updated successful!", "data": book_schema.dump(book)}), 200

@bp.delete("/books/<book_id>")
def delete(book_id: str):
    book_service.delete(book_id)
    return "", 204
