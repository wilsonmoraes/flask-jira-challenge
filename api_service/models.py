# encoding: utf-8
from sqlalchemy.ext.hybrid import hybrid_property

from api_service.extensions import db, pwd_context


class User(db.Model):
    """Basic user model"""

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(80), unique=True, nullable=False)
    _password = db.Column("password", db.String(255), nullable=False)
    active = db.Column(db.Boolean, default=True)
    role = db.Column(db.String(20), nullable=False)

    @hybrid_property
    def password(self):
        return self._password

    @password.setter
    def password(self, value):
        self._password = pwd_context.hash(value)

    def __repr__(self):
        return "<User %s>" % self.username


class AssetType(db.Model):
    __tablename__ = 'asset_types'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True, nullable=False)
    fields = db.relationship(
        'AssetField',
        secondary='asset_type_fields',
        backref='asset_types'
    )


class AssetField(db.Model):
    __tablename__ = 'asset_fields'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    field_type = db.Column(
        db.Enum('Text', 'Number', name='field_type', validate_strings=True),
        nullable=False
    )


asset_type_fields = db.Table(
    'asset_type_fields',
    db.Column('type_id', db.Integer, db.ForeignKey('asset_types.id'), primary_key=True),
    db.Column('field_id', db.Integer, db.ForeignKey('asset_fields.id'), primary_key=True)
)


class Asset(db.Model):
    __tablename__ = 'assets'
    id = db.Column(db.Integer, primary_key=True)
    asset_type_id = db.Column(db.Integer, db.ForeignKey('asset_types.id'), nullable=False)

    asset_type = db.relationship('AssetType', backref='assets')
    data = db.relationship('AssetData', backref='asset', cascade='all, delete-orphan')


class AssetData(db.Model):
    __tablename__ = 'asset_data'
    id = db.Column(db.Integer, primary_key=True)
    asset_id = db.Column(db.Integer, db.ForeignKey('assets.id'), nullable=False)
    field_id = db.Column(db.Integer, db.ForeignKey('asset_fields.id'), nullable=False)
    value = db.Column(db.String, nullable=False)

    field = db.relationship('AssetField')
