from collections import Counter

from sqlalchemy.orm import joinedload

from api_service.exceptions import APIConflict, APIBadRequest, APINotFound
from api_service.extensions import db
from api_service.models import AssetType, AssetField, Asset, AssetData


class AssetService:

    # === Asset Types ===

    @staticmethod
    def create_asset_type(name):
        if AssetType.query.filter_by(name=name).first():
            raise APIConflict(f"AssetType with name '{name}' already exists")
        asset_type = AssetType(name=name)
        db.session.add(asset_type)
        db.session.commit()
        return asset_type

    @staticmethod
    def get_all_asset_types():
        return AssetType.query.all()

    @staticmethod
    def get_asset_type_by_id(type_id):
        return AssetType.query.get(type_id)

    # === Asset Fields ===

    @staticmethod
    def create_asset_field_for_type(asset_type_id, field_name, field_type):
        if not field_name or not field_name.strip():
            raise APIBadRequest("Field name must not be empty")

        if field_type not in ("Text", "Number"):
            raise APIBadRequest(f"Invalid field type '{field_type}'. Allowed types: 'Text', 'Number'")

        asset_type = AssetService.get_asset_type_by_id(asset_type_id)
        if not asset_type:
            raise APIBadRequest(f"AssetType with ID {asset_type_id} not found")

        # Ensures idempotent creation and association of a field to an asset type
        field = AssetField.query.filter_by(name=field_name, field_type=field_type).first()
        if not field:
            field = AssetField(name=field_name, field_type=field_type)
            db.session.add(field)
            db.session.commit()

        if field not in asset_type.fields:
            asset_type.fields.append(field)
            db.session.commit()

        return field

    @staticmethod
    def get_fields_for_type(asset_type_id):
        asset_type = AssetService.get_asset_type_by_id(asset_type_id)
        if not asset_type:
            return None
        return asset_type.fields

    # === Assets ===

    @staticmethod
    def create_asset(asset_type_id, data):

        if not data:
            raise APIBadRequest("Missing 'data' payload")

        asset_type = AssetService.get_asset_type_by_id(asset_type_id)

        if not asset_type:
            raise APIBadRequest(f"AssetType with ID {asset_type_id} not found")

        if not asset_type.fields:
            raise APIBadRequest(f"AssetType {asset_type_id} has no fields defined")

        # Map field_id -> AssetField
        allowed_field_ids = {f.id: f for f in asset_type.fields}

        field_id_list = [item.get("field_id") for item in data]
        duplicates = [fid for fid, count in Counter(field_id_list).items() if count > 1]
        if duplicates:
            raise APIBadRequest(f"Duplicate field_id(s) found in payload: {duplicates}")

        asset = Asset(asset_type_id=asset_type_id)
        db.session.add(asset)
        db.session.flush()  # get ID without a commit

        for item in data:
            field_id = item.get("field_id")
            value = item.get("value")

            if field_id not in allowed_field_ids:
                raise APIBadRequest(f"Field ID '{field_id}' is not valid for AssetType {asset_type_id}")

            field = allowed_field_ids[field_id]

            if field.field_type == "Number":
                try:
                    float(value)
                except (ValueError, TypeError):
                    raise APIBadRequest(f"Invalid value for field '{field.name}', expected a number.")
            elif field.field_type == "Text":
                if not isinstance(value, str):
                    raise APIBadRequest(f"Invalid value for field '{field.name}', expected text.")

            asset_data = AssetData(
                asset_id=asset.id,
                field_id=field_id,
                value=str(value)
            )
            db.session.add(asset_data)

        db.session.commit()
        return asset

    @staticmethod
    def get_all_assets():
        return Asset.query.options(joinedload(Asset.data).joinedload(AssetData.field)).all()

    @staticmethod
    def get_asset_by_id(asset_id):
        return Asset.query.options(joinedload(Asset.data).joinedload(AssetData.field)).filter_by(id=asset_id).first()

    @staticmethod
    def update_asset(asset_id, updated_data):
        asset = Asset.query.options(joinedload(Asset.data).joinedload(AssetData.field)).filter_by(id=asset_id).first()
        if not asset:
            raise APINotFound(f"Asset with ID {asset_id} not found")

        asset_type = asset.asset_type
        if not asset_type or not asset_type.fields:
            raise APIBadRequest(f"AssetType for asset {asset_id} has no fields defined")

        if not updated_data:
            raise APIBadRequest("Missing 'data' payload")

        allowed_field_ids = {f.id: f for f in asset_type.fields}

        field_id_list = [item.get("field_id") for item in updated_data]
        duplicates = [fid for fid, count in Counter(field_id_list).items() if count > 1]
        if duplicates:
            raise APIBadRequest(f"Duplicate field_id(s) found in payload: {duplicates}")

        update_map = {item["field_id"]: item["value"] for item in updated_data}

        for field_id in update_map:
            if field_id not in allowed_field_ids:
                raise APIBadRequest(f"Field ID '{field_id}' is not valid for AssetType {asset_type.id}")

        for data in asset.data:
            field = data.field
            if data.field_id not in update_map:
                continue

            new_value = update_map[data.field_id]

            if field.field_type == "Number":
                try:
                    float(new_value)
                except (ValueError, TypeError):
                    raise APIBadRequest(f"Invalid value for field '{field.name}', expected a number.")
            elif field.field_type == "Text":
                if not isinstance(new_value, str):
                    raise APIBadRequest(f"Invalid value for field '{field.name}', expected text.")

            data.value = str(new_value)

        db.session.commit()
        return asset
