from flask import request
from flask_restx import Namespace, Resource, fields

from api_service.extensions import cache
from api_service.services.asset_service import AssetService
from api_service.services.auth_service import require_api_key

ASSET_TYPE_ALL_CACHE_KEY = "asset_types:all"
ASSET_TYPE_CACHE_KEY = lambda type_id: f"asset_types:{type_id}"
ASSET_TYPE_FIELDS_CACHE_KEY = lambda type_id: f"asset_types:{type_id}:fields"

api = Namespace("asset-types", description="Asset Type operations")

asset_type_model = api.model("AssetType", {
    "id": fields.Integer(readonly=True),
    "name": fields.String(required=True, description="Name of the asset type"),
})

field_model = api.model("AssetField", {
    "id": fields.Integer(readonly=True),
    "name": fields.String(required=True),
    "field_type": fields.String(required=True, enum=["Text", "Number"]),
})

field_input = api.model("AssetFieldInput", {
    "name": fields.String(required=True),
    "field_type": fields.String(required=True, enum=["Text", "Number"]),
})


@api.route("")
class AssetTypes(Resource):
    method_decorators = [require_api_key]

    @api.expect(asset_type_model)
    @api.marshal_with(asset_type_model, code=201)
    def post(self):
        """Create a new asset type"""
        data = api.payload

        cache.delete(ASSET_TYPE_ALL_CACHE_KEY)

        return AssetService.create_asset_type(data["name"]), 201

    @cache.cached(timeout=60, key_prefix=ASSET_TYPE_ALL_CACHE_KEY)
    @api.marshal_list_with(asset_type_model)
    def get(self):
        """List all asset types"""
        return AssetService.get_all_asset_types()


@api.route("/<int:type_id>")
class AssetType(Resource):
    method_decorators = [require_api_key]

    @cache.cached(timeout=60, key_prefix=lambda: ASSET_TYPE_CACHE_KEY(request.view_args["type_id"]))
    @api.marshal_with(asset_type_model)
    def get(self, type_id):
        """Get asset type by ID"""
        asset_type = AssetService.get_asset_type_by_id(type_id)
        if not asset_type:
            api.abort(404, "Asset type not found")
        return asset_type


@api.route("/<int:type_id>/fields")
class AssetFieldList(Resource):
    method_decorators = [require_api_key]

    @cache.cached(timeout=60, key_prefix=lambda: ASSET_TYPE_FIELDS_CACHE_KEY(request.view_args["type_id"]))
    @api.marshal_list_with(field_model)
    def get(self, type_id):
        """List all fields for a given asset type"""
        fields = AssetService.get_fields_for_type(type_id)
        if fields is None:
            api.abort(404, "Asset type not found")
        return fields

    @api.expect(field_input)
    @api.marshal_with(field_model, code=201)
    def post(self, type_id):
        """Create a new field for an asset type"""
        data = api.payload
        field = AssetService.create_asset_field_for_type(
            asset_type_id=type_id,
            field_name=data["name"],
            field_type=data["field_type"]
        )
        if field is None:
            api.abort(404, "Asset type not found")

        cache.delete(ASSET_TYPE_FIELDS_CACHE_KEY(type_id))
        cache.delete(ASSET_TYPE_ALL_CACHE_KEY)

        return field, 201
