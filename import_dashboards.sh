#!/bin/bash

# Wait for Superset to be ready
until curl -sSf http://localhost:8088/api/v1/ping; do
  echo "Waiting for Superset to be ready..."
  sleep 10
done

# Import the dashboard
curl -X POST \
  -F 'file=@/app/superset_exports/dashboard.zip' \
  "http://localhost:8088/api/v1/dashboard/import/"
