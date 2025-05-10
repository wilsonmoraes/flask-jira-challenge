from flask_restx import Namespace, Resource, fields

from api_service.repositories.asset_repository import AssetRepository

api = Namespace("assets", description="Asset operations")

asset_data_field = fields.Raw(required=True, description="Field-value pairs based on asset type")

asset_input_model = api.model("AssetInput", {
    "asset_type_id": fields.Integer(required=True),
    "data": asset_data_field
})

asset_response_model = api.model("AssetResponse", {
    "id": fields.Integer(),
    "asset_type_id": fields.Integer(),
    "data": fields.Raw()
})


@api.route("")
class AssetList(Resource):
    @api.marshal_list_with(asset_response_model)
    def get(self):
        """List all asset instances"""
        assets = AssetRepository.get_all_assets()
        return [
            {
                "id": asset.id,
                "asset_type_id": asset.asset_type_id,
                "data": {d.field.name: d.value for d in asset.data}
            } for asset in assets
        ]

    @api.expect(asset_input_model)
    @api.marshal_with(asset_response_model, code=201)
    def post(self):
        """Create a new asset instance"""
        data = api.payload
        try:
            asset = AssetRepository.create_asset(data["asset_type_id"], data["data"])
        except ValueError as e:
            api.abort(400, str(e))
        if not asset:
            api.abort(404, "Asset type not found")
        return {
            "id": asset.id,
            "asset_type_id": asset.asset_type_id,
            "data": {d.field.name: d.value for d in asset.data}
        }, 201


@api.route("/<int:asset_id>")
class AssetDetail(Resource):
    @api.marshal_with(asset_response_model)
    def get(self, asset_id):
        """Get an asset instance by ID"""
        asset = AssetRepository.get_asset_by_id(asset_id)
        if not asset:
            api.abort(404, "Asset not found")
        return {
            "id": asset.id,
            "asset_type_id": asset.asset_type_id,
            "data": {d.field.name: d.value for d in asset.data}
        }

    @api.expect(asset_input_model)
    @api.marshal_with(asset_response_model)
    def put(self, asset_id):
        """Update an asset instance"""
        data = api.payload
        asset = AssetRepository.update_asset(asset_id, data["data"])
        if not asset:
            api.abort(404, "Asset not found")
        return {
            "id": asset.id,
            "asset_type_id": asset.asset_type_id,
            "data": {d.field.name: d.value for d in asset.data}
        }
