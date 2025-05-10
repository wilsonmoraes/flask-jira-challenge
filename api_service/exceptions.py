# api_service/exceptions.py

class APIConflict(Exception):
    """409 - Conflict"""


class APINotFound(Exception):
    """404 - Not Found"""


class APIBadRequest(Exception):
    """400 - Bad Request"""
