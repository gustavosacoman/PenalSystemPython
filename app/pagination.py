from flask import request

from app.extensions import db
from app.errors import AppError

DEFAULT_PER_PAGE = 20
MAX_PER_PAGE = 100


def _positive_int(name: str, default: int) -> int:
    raw = request.args.get(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError:
        raise AppError(f"Query parameter '{name}' must be an integer", 400)
    if value < 1:
        raise AppError(f"Query parameter '{name}' must be greater than zero", 400)
    return value


def paginate(query, schema) -> dict:
    page = _positive_int("page", 1)
    per_page = min(_positive_int("per_page", DEFAULT_PER_PAGE), MAX_PER_PAGE)

    result = db.paginate(query, page=page, per_page=per_page, error_out=False)

    return {
        "data": schema.dump(result.items),
        "pagination": {
            "page": result.page,
            "per_page": result.per_page,
            "total": result.total,
            "pages": result.pages,
            "has_next": result.has_next,
            "has_prev": result.has_prev,
        },
    }
