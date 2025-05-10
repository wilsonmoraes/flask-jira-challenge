"""Default configuration

Use env var to override
"""
import os

from dotenv import load_dotenv

load_dotenv(".flaskenv")

ENV = os.getenv("FLASK_ENV")
DEBUG = ENV == "development"
SECRET_KEY = os.getenv("SECRET_KEY")
PROPAGATE_EXCEPTIONS = True

SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URI")
SQLALCHEMY_TRACK_MODIFICATIONS = False

JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "super-jwt-secret")
JWT_TOKEN_LOCATION = ["headers"]
JWT_ACCESS_TOKEN_EXPIRES = 3600  # 1 hour
JWT_REFRESH_TOKEN_EXPIRES = 86400  # 1 day
JWT_HEADER_NAME = "Authorization"
JWT_HEADER_TYPE = "Bearer"
JWT_VERIFY_SUB = False

# Flask-Caching
CACHE_TYPE = "SimpleCache"  # Can be moved to Redis only changing this line to "RedisCache" and adding CACHE_REDIS_URL config
CACHE_DEFAULT_TIMEOUT = 300  # seconds