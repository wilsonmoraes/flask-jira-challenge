# encoding: utf-8

from flask import Flask
from flask_jwt_extended import JWTManager

from api_service import api
from api_service.extensions import db, cache
from api_service.extensions import migrate
from api_service.manage import cli


def create_app(testing=False):
    app = Flask("api_service")
    app.config.from_object("api_service.config")

    JWTManager(app)
    cache.init_app(app)

    if testing is True:
        app.config["TESTING"] = True

    configure_extensions(app)
    register_blueprints(app)

    return app


def configure_extensions(app):
    db.init_app(app)
    migrate.init_app(app, db)
    app.cli.add_command(cli)


def register_blueprints(app):
    app.register_blueprint(api.views.api_bp)
    app.register_blueprint(api.views.auth_bp)


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000)
