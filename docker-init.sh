# docker-init.sh
#!/bin/bash
set -e

# Initialize the database
superset db upgrade

# Create an admin user (you can change the credentials here)
superset fab create-admin --username admin --firstname Admin --lastname User --email admin@example.com --password admin || true

# Initialize Superset
superset init
