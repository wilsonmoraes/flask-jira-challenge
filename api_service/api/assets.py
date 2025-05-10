from flask import request
from flask_restx import Namespace, Resource, fields
from api_service.extensions import cache

from api_service.services.asset_service import AssetService
from api_service.services.auth_service import require_api_key

ASSET_CACHE_KEY = lambda asset_id: f"asset:{asset_id}"
ASSET_ALL_CACHE_KEY = "assets:all"

api = Namespace("assets", description="Asset operations")

asset_data_item = api.model("AssetDataInput", {
    "field_id": fields.Integer(required=True),
    "value": fields.Raw(required=True)
})

asset_input_model = api.model("AssetInput", {
    "asset_type_id": fields.Integer(required=True),
    "data": fields.List(fields.Nested(asset_data_item), required=True)
})

asset_update_model = api.model("AssetUpdate", {
    "data": fields.List(fields.Nested(asset_data_item), required=True)
})

asset_data_output_item = api.model("AssetDataOutput", {
    "field_id": fields.Integer(),
    "value": fields.Raw()
})

asset_response_model = api.model("AssetResponse", {
    "id": fields.Integer(),
    "asset_type_id": fields.Integer(),
    "data": fields.List(fields.Nested(asset_data_output_item))
})


@api.route("")
class AssetList(Resource):
    method_decorators = [require_api_key]

    @cache.cached(timeout=60, key_prefix=ASSET_ALL_CACHE_KEY)
    @api.marshal_list_with(asset_response_model)
    def get(self):
        """List all asset instances"""
        assets = AssetService.get_all_assets()
        return [
            {
                "id": asset.id,
                "asset_type_id": asset.asset_type_id,
                "data": [
                    {"field_id": d.field_id, "value": d.value}
                    for d in asset.data
                ]
            } for asset in assets
        ]

    @api.expect(asset_input_model)
    @api.marshal_with(asset_response_model, code=201)
    def post(self):
        """Create a new asset instance"""
        data = api.payload
        asset = None
        try:
            asset = AssetService.create_asset(data["asset_type_id"], data["data"])
        except ValueError as e:
            api.abort(400, str(e))
        if not asset:
            api.abort(404, "Asset type not found")
        cache.delete(ASSET_ALL_CACHE_KEY)
        return {
            "id": asset.id,
            "asset_type_id": asset.asset_type_id,
            "data": [
                {"field_id": d.field_id, "value": d.value}
                for d in asset.data
            ]
        }, 201


@api.route("/<int:asset_id>")
class AssetDetail(Resource):
    method_decorators = [require_api_key]

    @cache.cached(timeout=60, key_prefix=lambda: ASSET_CACHE_KEY(request.view_args['asset_id']))
    @api.marshal_with(asset_response_model)
    def get(self, asset_id):
        """Get an asset instance by ID"""
        asset = AssetService.get_asset_by_id(asset_id)
        if not asset:
            api.abort(404, "Asset not found")
        return {
            "id": asset.id,
            "asset_type_id": asset.asset_type_id,
            "data": [
                {"field_id": d.field_id, "value": d.value}
                for d in asset.data
            ]
        }

    @api.expect(asset_update_model)
    @api.marshal_with(asset_response_model)
    def put(self, asset_id):
        """Update an asset instance"""
        asset = AssetService.update_asset(asset_id, api.payload['data'])
        if not asset:
            api.abort(404, "Asset not found")

        cache.delete(ASSET_ALL_CACHE_KEY)
        cache.delete(ASSET_CACHE_KEY(asset_id))

        return {
            "id": asset.id,
            "asset_type_id": asset.asset_type_id,
            "data": [
                {"field_id": d.field_id, "value": d.value}
                for d in asset.data
            ]
        }
