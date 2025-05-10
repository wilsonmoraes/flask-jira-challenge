# encoding: utf-8

import click
from flask.cli import with_appcontext


@click.group()
def cli():
    """Main entry point"""
    pass


@cli.command("init")
@with_appcontext
def init():
    """Create a new admin user"""
    from api_service.extensions import db
    from api_service.models import User

    click.echo("Checking if users exist...")

    if not User.query.filter_by(username="admin").first():
        user1 = User(username="admin", email="admin@mail.com", password="admin", active=True, role='ADMIN')
        db.session.add(user1)
        db.session.commit()
        click.echo("Admin user created.")

    if not User.query.filter_by(username="johndoe").first():
        user2 = User(username="johndoe", email="johndoe@mail.com", password="john", active=True, role='USER')
        db.session.add(user2)
        db.session.commit()
        click.echo("John Doe user created.")

    click.echo("User creation completed.")


if __name__ == "__main__":
    cli()
