#!/bin/bash
set -e

# Initialize the database
superset db upgrade

# Create an admin user (you can change the credentials here)
superset fab create-admin --username admin --firstname Admin --lastname User --email admin@example.com --password admin || true

# Initialize Superset
superset init

# Import the dashboard
superset import_dashboards -p /superset-exports/dashboard.zip

# Start the Superset server
superset run -h 0.0.0.0 -p 8088 --with-threads --reload --debugger
