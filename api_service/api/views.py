# encoding: utf-8

from flask import Blueprint, jsonify
from flask_restful import Api
from marshmallow import ValidationError

from api_service.api import resources
from api_service.auth.resources import LoginResource, RefreshTokenResource

api_bp = Blueprint("api", __name__, url_prefix="/api/v1")
api = Api(api_bp)

api.add_resource(resources.StockQuery, "/stock", endpoint="stock")
api.add_resource(resources.History, "/users/history", endpoint="users-history")
api.add_resource(resources.Stats, "/stats", endpoint="stats")

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
auth_api = Api(auth_bp)

auth_api.add_resource(LoginResource, "/login")
auth_api.add_resource(RefreshTokenResource, "/refresh")


def handle_marshmallow_error(e):
    return jsonify(e.messages), 400


api_bp.register_error_handler(ValidationError, handle_marshmallow_error)

auth_bp.register_error_handler(ValidationError, handle_marshmallow_error)
