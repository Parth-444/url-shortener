import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    # DEBUG = True
    # SQLALCHEMY_DATABASE_URI = "postgresql://postgres:12345@localhost:5432/url_shortener"
    # SQLALCHEMY_TRACK_MODIFICATIONS = False
    # RATELIMIT_STORAGE_URI = "redis://localhost:6379"


    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379")
    RATELIMIT_STORAGE_URI = REDIS_URL
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")