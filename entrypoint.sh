#!/bin/bash

# Run database migrations
flask db upgrade

# Seed default asset types
flask init

# Start Flask application
exec flask run --host=0.0.0.0