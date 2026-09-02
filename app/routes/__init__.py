from flask import Flask
from app.routes.prisoner_routes import bp as prisoner_bp
from app.routes.study_routes import bp as study_bp

def init_app(app: Flask):
    app.register_blueprint(prisoner_bp, url_prefix="/api/prisoners")
    
    app.register_blueprint(study_bp, url_prefix="/api/studies")