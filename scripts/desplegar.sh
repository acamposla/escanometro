#!/usr/bin/env bash
# Publica el Escañómetro en Cloudflare Pages (proyecto escanometro) con su base D1.
#
#   bash scripts/desplegar.sh            -> produccion (escanometro.pages.dev)
#   bash scripts/desplegar.sh borrador   -> vista previa (borrador.escanometro.pages.dev)
#
# Se niega a publicar en produccion un catalogo provisional (sin cotejar con el PDF
# oficial: regla dura 2). Antes de publicar pasa los tests y aplica las migraciones
# pendientes a la base D1 remota. Usa la sesion OAuth de wrangler de esta maquina.
set -euo pipefail
cd "$(dirname "$0")/.."

RAMA="${1:-main}"
PROVISIONAL=$(python3 -c "import json;print(json.load(open('web/catalogo.json'))['provisional'])")
VERSION=$(python3 -c "import json;print(json.load(open('web/catalogo.json'))['version'])")

if [[ "$RAMA" == "main" && "$PROVISIONAL" == "True" ]]; then
  echo "NO: el catalogo $VERSION es provisional (sin cotejar). Solo se publica como borrador." >&2
  exit 1
fi

./.venv/bin/python -m pytest tests/ -q
wrangler d1 migrations apply sesgo-respuestas --remote
wrangler pages deploy web --project-name escanometro --branch "$RAMA" --commit-dirty=true

echo "Publicado catalogo $VERSION en la rama $RAMA."
