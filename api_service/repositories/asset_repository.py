from sqlalchemy.orm import joinedload

from api_service.extensions import db
from api_service.models import AssetType, AssetField, Asset, AssetData


class AssetRepository:

    # === Asset Types ===

    @staticmethod
    def create_asset_type(name):
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
        asset_type = AssetRepository.get_asset_type_by_id(asset_type_id)

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
        asset_type = AssetRepository.get_asset_type_by_id(asset_type_id)
        if not asset_type:
            return None
        return asset_type.fields

    # === Assets ===

    @staticmethod
    def create_asset(asset_type_id, data_dict):
        asset_type_fields = AssetRepository.get_fields_for_type(asset_type_id)
        if asset_type_fields is None:
            return None

        asset = Asset(asset_type_id=asset_type_id)
        db.session.add(asset)
        db.session.flush()  # pega o ID sem dar commit ainda

        for field in asset_type_fields:
            if field.name not in data_dict:
                raise ValueError(f"Missing field: {field.name}")

            raw_value = data_dict[field.name]

            if field.field_type == 'Number':
                try:
                    float(raw_value)
                except ValueError:
                    raise ValueError(f"Invalid value for field '{field.name}', expected a number.")

            asset_data = AssetData(
                asset_id=asset.id,
                field_id=field.id,
                value=str(raw_value)
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
        asset = Asset.query.options(joinedload(Asset.data)).filter_by(id=asset_id).first()
        if not asset:
            return None

        for data in asset.data:
            field_name = data.field.name
            if field_name in updated_data:
                data.value = str(updated_data[field_name])

        db.session.commit()
        return asset
