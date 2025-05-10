import logging

from flask_jwt_extended import (
    JWTManager, create_access_token, create_refresh_token,
    jwt_required, get_jwt_identity, get_jwt
)

from api_service.extensions import pwd_context
from api_service.models import User

logger = logging.getLogger(__name__)

jwt = JWTManager()


class AuthService:
    """Handles authentication using Flask-HTTPAuth."""

    @staticmethod
    def authenticate(username, password):
        """Authenticates a user and returns a JWT token."""
        user = User.query.filter_by(username=username).first()
        if user and pwd_context.verify(password, user.password):
            access_token = create_access_token(
                identity=str(user.id),
                additional_claims={"role": user.role}
            )
            refresh_token = create_refresh_token(
                identity=str(user.id),
                additional_claims={"role": user.role},
            )
            return {"access_token": access_token, "refresh_token": refresh_token}, 200
        return {"message": "Invalid credentials"}, 401

    @staticmethod
    @jwt_required()
    def get_authenticated_user():
        """Returns the currently authenticated user."""
        user = get_jwt_identity()
        return User.query.get(user['id'])

    @staticmethod
    @jwt_required()
    def require_admin():
        """Ensures the authenticated user is an admin."""
        claims = get_jwt()
        if claims.get("role") != "ADMIN":
            return {"message": "Forbidden: You do not have permission to access this resource"}, 403
        return {"message": "Authorized"}, 200

    @staticmethod
    @jwt_required(refresh=True)
    def refresh_access_token():
        """Refreshes the access token using a refresh token."""
        user_id = get_jwt_identity()
        claims = get_jwt()
        new_access_token = create_access_token(
            identity=user_id,
            additional_claims={"role": claims.get("role")}
        )
        return {"access_token": new_access_token}, 200


def jwt_admin_required(f):
    """Decorator to restrict access to admins only."""

    @jwt_required()
    def decorated_function(*args, **kwargs):
        claims = get_jwt()
        if claims.get('sub', {}).get("role") != "ADMIN":
            return {"message": "Forbidden: You do not have permission to access this resource"}, 403
        return f(*args, **kwargs)

    return decorated_function
