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

SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask-Caching
CACHE_TYPE = os.getenv("CACHE_TYPE", "SimpleCache")
CACHE_REDIS_URL = os.getenv("CACHE_REDIS_URL")

RESTPLUS_MASK_SWAGGER = os.getenv("RESTPLUS_MASK_SWAGGER", False)
