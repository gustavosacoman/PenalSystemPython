from flask import Flask
from app.routes.prisoner_routes import bp as prisoner_bp
from app.routes.book_routes import bp as book_bp
from app.routes.day_of_work_routes import bp as day_of_work_bp

def init_app(app: Flask):
    app.register_blueprint(prisoner_bp, url_prefix="/api/prisoners")
    app.register_blueprint(book_bp, url_prefix="/api")
    app.register_blueprint(day_of_work_bp, url_prefix="/api")
