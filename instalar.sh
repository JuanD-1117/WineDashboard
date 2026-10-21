#!/usr/bin/env bash
# Levanta WineDashboard en Docker y la abre en el navegador.
#
#   ./instalar.sh                  # construye y levanta (idempotente)
#   WINE_PORT=8600 ./instalar.sh   # otro puerto
#
# Si el puerto pedido está ocupado por otro programa, usa el siguiente libre.
set -euo pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

error() { printf '\nERROR: %s\n' "$*" >&2; exit 1; }
paso()  { printf '\n==> %s\n' "$*"; }

asegurar_docker() {
    # Docker Desktop recién instalado en macOS puede no haber enlazado aún la CLI en el PATH.
    local cli_mac=/Applications/Docker.app/Contents/Resources/bin
    if ! command -v docker >/dev/null 2>&1 && [[ -x "$cli_mac/docker" ]]; then
        export PATH="$cli_mac:$PATH"
    fi
    command -v docker >/dev/null 2>&1 \
        || error "Docker no está instalado: https://docs.docker.com/get-docker/"

    if ! docker info >/dev/null 2>&1; then
        if [[ "$(uname)" == "Darwin" ]] && open -a Docker >/dev/null 2>&1; then
            paso "Docker Desktop estaba cerrado. Iniciándolo (puede tardar hasta 3 minutos)..."
            for _ in $(seq 1 90); do
                docker info >/dev/null 2>&1 && break
                sleep 2
            done
        fi
        docker info >/dev/null 2>&1 \
            || error "El daemon de Docker no responde. Abra Docker Desktop y repita el comando."
    fi
    docker compose version >/dev/null 2>&1 || error "Falta el plugin 'docker compose' (v2)."
}

puerto_en_uso() {
    local puerto="$1"
    # Un puerto publicado por el propio contenedor del proyecto no es un conflicto.
    if docker ps --filter "name=^winedashboard-app$" --format '{{.Ports}}' \
        | grep -q ":${puerto}->"; then
        return 1
    fi
    # Conectar por TCP detecta cualquier proceso escuchando, sea de quien sea.
    (exec 3<>"/dev/tcp/127.0.0.1/$puerto") 2>/dev/null
}

primer_puerto_libre() {
    local puerto="$1"
    while puerto_en_uso "$puerto"; do
        puerto=$((puerto + 1))
    done
    echo "$puerto"
}

asegurar_docker

pedido="${WINE_PORT:-8501}"
WINE_PORT="$(primer_puerto_libre "$pedido")"
[[ "$WINE_PORT" == "$pedido" ]] || paso "El puerto $pedido está ocupado; se usará $WINE_PORT."
export WINE_PORT

paso "Construyendo la imagen y levantando WineDashboard..."
docker compose up -d --build

paso "Esperando a que la app responda en http://localhost:$WINE_PORT ..."
for _ in $(seq 1 60); do
    if curl -fsS "http://localhost:$WINE_PORT/_stcore/health" >/dev/null 2>&1; then
        break
    fi
    sleep 2
done
curl -fsS "http://localhost:$WINE_PORT/_stcore/health" >/dev/null 2>&1 \
    || error "La app no respondió. Revise: docker compose logs app"

docker compose ps
cat <<FIN

  WineDashboard : http://localhost:$WINE_PORT

  Detener      : docker compose down
  Borrar todo  : ./limpiar.sh
FIN

if command -v open >/dev/null 2>&1; then
    open "http://localhost:$WINE_PORT" >/dev/null 2>&1 || true
elif command -v xdg-open >/dev/null 2>&1; then
    xdg-open "http://localhost:$WINE_PORT" >/dev/null 2>&1 || true
fi
