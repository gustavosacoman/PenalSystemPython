from flask import Flask, jsonify
from marshmallow import ValidationError
from werkzeug.exceptions import HTTPException

from app.extensions import db

class AppError(Exception):
    status_code = 400

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        if status_code is not None:
            self.status_code = status_code

class ResourceNotFound(AppError):
    status_code = 404

class BusinessRuleViolation(AppError):
    status_code = 409

class InvalidReference(AppError):
    status_code = 422

def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(AppError)
    def handle_domain_error(error: AppError):
        db.session.rollback()
        return (
            jsonify(
                {
                    "code": error.status_code,
                    "message": type(error).__name__,
                    "description": error.message,
                }
            ),
            error.status_code,
        )

    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError):
        return (
            jsonify(
                {
                    "code": 422,
                    "name": "Unprocessable Entity",
                    "description": "Payload validation failed.",
                    "errors": error.messages,
                }
            ),
            422,
        )

    @app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        return (
            jsonify(
                {
                    "code": error.code,
                    "name": error.name,
                    "description": error.description,
                }
            ),
            error.code,
        )

    @app.errorhandler(Exception)
    def handle_generic_exception(error: Exception):
        db.session.rollback()
        app.logger.exception("Unhandled server error")
        if app.debug or app.testing:
            raise error
        return (
            jsonify(
                {
                    "code": 500,
                    "name": "Internal Server Error",
                    "description": "An unexpected internal server error occurred.",
                }
            ),
            500,
        )