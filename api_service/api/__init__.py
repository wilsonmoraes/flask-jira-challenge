from flask_restx import Api

from api_service.api.asset_types import api as asset_type_ns
from api_service.api.assets import api as asset_ns

api = Api(
    title="Asset Management API",
    version="1.0",
    description="API for managing dynamic assets",
    doc="/docs"
)

api.add_namespace(asset_type_ns, path="/api/v1/asset-types")
api.add_namespace(asset_ns, path="/api/v1/assets")
