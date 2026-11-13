#!/usr/bin/env python3
"""Exporta el catalogo a web/catalogo.json, que leen el juego y la funcion de respuestas.

La version del catalogo es una huella del contenido: si cambia una sola frase,
cambia la version y las respuestas antiguas quedan separadas en el analisis.

Uso:  python scripts/exportar_catalogo.py datos/catalogo/catalogo_v1.csv
      python scripts/exportar_catalogo.py datos/catalogo/candidatos.csv --provisional
"""

import argparse
import csv
import hashlib
import json
import re

# La etiqueta de rol no viaja al navegador: solo se usa en el analisis.
CAMPOS = ["id", "tema", "frase", "bloque", "grupo", "orador", "fecha", "ds", "pdf", "foto"]


_CIFRA_LARGA = re.compile(r"(?<![\d.,])(\d{5,})(?![\d])")


def agrupar_cifras(texto):
    """Cifras de cinco o mas digitos en grupos de tres con espacio fijo ("346 000"), como
    las imprime el Diario de Sesiones y como manda la RAE. El parseo del corpus les quito
    el espacio y en pantalla "1196000" no se lee. Solo cambia la presentacion: el cotejo
    con el PDF se hace antes, sobre el texto del corpus."""
    def agrupar(m):
        d = m.group(1)
        grupos = []
        while d:
            grupos.insert(0, d[-3:])
            d = d[:-3]
        return "\u00a0".join(grupos)
    return _CIFRA_LARGA.sub(agrupar, texto)


def construir(filas, provisional=False, por_celda=25, fotos=None):
    fotos = fotos or {}
    filas = [dict(f, foto=fotos.get(f.get("orador", ""), ""), frase=agrupar_cifras(f.get("frase", ""))) for f in filas]
    if provisional:
        filas = [f for f in filas if int(f["orden"]) <= por_celda]
    frases = [{c: f.get(c, "") for c in CAMPOS} for f in filas]
    frases.sort(key=lambda f: f["id"])
    huella = hashlib.sha1(json.dumps(frases, ensure_ascii=False).encode("utf-8")).hexdigest()[:8]
    version = ("provisional-" if provisional else "v-") + huella
    return {"version": version, "provisional": provisional, "frases": frases}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("catalogo")
    ap.add_argument("--provisional", action="store_true", help="candidatos sin confirmar ni cotejar")
    ap.add_argument("--salida", default="web/catalogo.json")
    ap.add_argument("--fotos", default="datos/catalogo/fotos.csv", help="salida de scripts/fotos.py")
    args = ap.parse_args()
    fotos = {}
    try:
        with open(args.fotos, encoding="utf-8") as fh:
            fotos = {f["orador"]: f["foto"] for f in csv.DictReader(fh) if f["estado"] == "ok"}
    except FileNotFoundError:
        pass
    with open(args.catalogo, encoding="utf-8") as fh:
        datos = construir(list(csv.DictReader(fh)), args.provisional, fotos=fotos)
    with open(args.salida, "w", encoding="utf-8") as fh:
        json.dump(datos, fh, ensure_ascii=False, indent=1)
    print(f"{len(datos['frases'])} frases, version {datos['version']} -> {args.salida}")


if __name__ == "__main__":
    main()
