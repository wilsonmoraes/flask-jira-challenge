# encoding: utf-8
from flask_caching import Cache
from flask_sqlalchemy import SQLAlchemy
from passlib.context import CryptContext
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate


db = SQLAlchemy()
ma = Marshmallow()
migrate = Migrate()
pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
cache = Cache()