#!/usr/bin/env bash
# Elimina el contenedor, la red y la imagen de WineDashboard. No toca otros recursos de Docker.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

docker compose down --remove-orphans
docker image rm winedashboard-app:latest 2>/dev/null || true
echo "Recursos de WineDashboard eliminados."
