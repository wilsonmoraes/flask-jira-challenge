# encoding: utf-8

import click
from flask.cli import with_appcontext

from api_service.models import AssetType


@click.group()
def cli():
    """Main entry point"""
    pass


@cli.command("init")
@with_appcontext
def init():
    """Initialize default asset types"""
    from api_service.extensions import db

    click.echo("Checking and seeding default asset types...")

    default_types = ["Laptop", "Monitor", "Software License"]
    for name in default_types:
        if not AssetType.query.filter_by(name=name).first():
            db.session.add(AssetType(name=name))

    db.session.commit()
    click.echo("Default asset types created (if not already present).")


if __name__ == "__main__":
    cli()
