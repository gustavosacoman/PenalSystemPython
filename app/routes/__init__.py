from flask import Flask
from app.routes.prisoner_routes import bp as prisoner_bp

def init_app(app: Flask):
    app.register_blueprint(prisoner_bp, url_prefix="/api/prisoners")