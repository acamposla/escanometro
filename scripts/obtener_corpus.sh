#!/usr/bin/env bash
# Descarga el corpus del Diario de Sesiones. No se versiona aqui: son 541 MB en disco (322 MB solo la
# carpeta data/, el resto es historial de git) de un tercero, y se reclonan en un comando.
#
# Fuente: escano-abierto (MIT), que procesa los PDF oficiales del Congreso y
# extrae las intervenciones una a una con orador, grupo, fecha y texto literal.
# Los datos originales son del Congreso de los Diputados, reutilizables al
# amparo de la Ley 37/2007.
set -euo pipefail

DESTINO="${1:-corpus}"

if [ -d "$DESTINO/.git" ]; then
  echo "El corpus ya esta en $DESTINO. Actualizando."
  git -C "$DESTINO" pull --ff-only
else
  git clone --depth 1 https://github.com/jorgegarcelan/escano-abierto.git "$DESTINO"
fi

SESIONES="$DESTINO/data/sesiones"
echo
echo "Sesiones disponibles: $(find "$SESIONES" -name '*.json' | wc -l)"
echo "Ruta para los scripts: $SESIONES"
