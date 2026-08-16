import os

from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key-change-me")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL") or "sqlite:///task_manager.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_SECURE = os.getenv("FLASK_ENV") == "production"
    JSON_SORT_KEYS = False
    PROPAGATE_EXCEPTIONS = False
