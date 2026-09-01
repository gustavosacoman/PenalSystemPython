import os
from multiprocessing.pool import CLOSE
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "insecure-dev-key")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", "mysql+pymysql://root:root@localhost:3306/penal_system"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    @classmethod
    def init_app(cls, app) -> None:
        pass
class DevelopmentConfig(Config):
    DEBUG = True
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", "0") == "1"
class TestingConfig(Config):
    TESTING = True

    SQLALCHEMY_DATABASE_URI = "sqlite+pysqlite:///:memory:"

CONFIG_BY_NAME = {
    "development": DevelopmentConfig,
    "testing": TestingConfig,
}
def get_config(name: str | None = None):
    name = name or os.getenv("APP_ENV", "development")
    return CONFIG_BY_NAME.get(name, DevelopmentConfig)