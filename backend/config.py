import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


class Config:
    SECRET_KEY = os.getenv("FLASK_SECRET_KEY", "dev-secret-change-me")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-dev-secret")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", f"sqlite:///{BASE_DIR / 'cms_ai.db'}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    UPLOAD_FOLDER = BASE_DIR / os.getenv("UPLOAD_FOLDER", "uploads")
    TTS_FOLDER = BASE_DIR / os.getenv("TTS_FOLDER", "uploads/tts")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    TTS_DEFAULT_LANG = os.getenv("TTS_DEFAULT_LANG", "ar")
    TTS_OPENAI_VOICE = os.getenv("TTS_OPENAI_VOICE", "nova")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
