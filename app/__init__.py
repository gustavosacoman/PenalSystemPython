from flask import Flask

from app.config import get_config
from app.errors import register_error_handlers
from app.extensions import db, ma, migrate
from app.routes import init_app as register_routes

import app.models

def create_app(config_name: str | None = None) -> Flask:
    app = Flask(__name__)

    config_cls = get_config(config_name)
    app.config.from_object(config_cls)
    config_cls.init_app(app)

    db.init_app(app)
    migrate.init_app(app, db)
    ma.init_app(app)

    register_error_handlers(app)
    register_routes(app)

    @app.get("/health")
    def health():
        return {"status": "ok"}, 200

    return app