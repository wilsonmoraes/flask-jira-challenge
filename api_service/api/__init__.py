from flask_restx import Api, Resource

from api_service.api.asset_types import api as asset_type_ns
from api_service.api.assets import api as asset_ns
from api_service.exceptions import APIConflict, APINotFound, APIBadRequest

authorizations = {
    "APIKeyHeader": {
        "type": "apiKey",
        "in": "header",
        "name": "X-API-KEY"
    }
}

api = Api(
    title="Asset Management API",
    version="1.0",
    description="API for managing dynamic assets",
    doc="/docs",
    authorizations=authorizations,
    security="APIKeyHeader"
)

api.add_namespace(asset_type_ns, path="/api/v1/asset-types")
api.add_namespace(asset_ns, path="/api/v1/assets")


@api.route("/health")
class Health(Resource):
    def get(self):
        return {"status": "ok"}, 200


@api.errorhandler(APIConflict)
def handle_conflict(error):
    return {"message": str(error)}, 409


@api.errorhandler(APINotFound)
def handle_not_found(error):
    return {"message": str(error)}, 404


@api.errorhandler(APIBadRequest)
def handle_bad_request(error):
    return {"message": str(error)}, 400
