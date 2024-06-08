#!/bin/bash

# Esperar a que Superset esté listo
until curl -sSf http://superset:8088/api/v1/ping; do
  echo "Esperando a que Superset esté listo..."
  sleep 10
done

# Importar el dashboard
curl -X POST \
  -F 'file=@/app/superset_exports/dashboard.zip' \
  "http://superset:8088/api/v1/dashboard/import/"
