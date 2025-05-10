import logging
from functools import wraps

from flask import request, abort

from api_service.config import SECRET_KEY

logger = logging.getLogger(__name__)


def require_api_key(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if request.headers.get('X-API-KEY') != SECRET_KEY:
            abort(401, description='Invalid or missing API key')
        return func(*args, **kwargs)

    return wrapper
