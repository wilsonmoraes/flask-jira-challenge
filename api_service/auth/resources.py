from flask import request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
from flask_restful import Resource

from api_service.extensions import pwd_context
from api_service.models import User


class LoginResource(Resource):
    """Handles user login and JWT token generation."""

    def post(self):
        """Login endpoint that returns a JWT token."""
        data = request.get_json()
        if not data or "username" not in data or "password" not in data:
            return {"message": "Username and password are required"}, 400

        user = User.query.filter_by(username=data["username"]).first()
        if not user or not pwd_context.verify(data["password"], user.password):
            return {"message": "Invalid credentials"}, 401

        access_token = create_access_token(identity={"id": user.id, "role": user.role})
        refresh_token = create_refresh_token(identity={"id": user.id, "role": user.role})

        return {"access_token": access_token, "refresh_token": refresh_token}, 200


class RefreshTokenResource(Resource):
    """Handles JWT refresh token."""

    @jwt_required(refresh=True)
    def post(self):
        """Refreshes the access token."""
        identity = get_jwt_identity()
        new_access_token = create_access_token(identity=identity)
        return {"access_token": new_access_token}, 200
