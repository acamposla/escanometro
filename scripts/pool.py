#!/usr/bin/env python3
"""Exporta el pool completo de candidatas a un CSV, con su identificador.

Es la entrada comun del clasificador y de la muestra de revision: los dos leen
el mismo fichero para que sus resultados se puedan cruzar por `id`.

Uso:  python scripts/pool.py corpus/data/sesiones
"""

import argparse
import csv
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from muestrear import CAMPOS, construir_pool


def deduplicar(candidatas):
    """Una frase repetida por el mismo orador en la misma sesion es una sola
    candidata: comparte id y contarla dos veces la sobrerrepresenta."""
    vistas = set()
    salida = []
    for c in candidatas:
        clave = (c["id"], c["tema"])
        if clave in vistas:
            continue
        vistas.add(clave)
        salida.append(c)
    return salida


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sesiones", nargs="?", default="corpus/data/sesiones")
    ap.add_argument("--salida", default="datos/pool.csv")
    args = ap.parse_args()

    pool = construir_pool(args.sesiones)
    filas = deduplicar(pool["DER"] + pool["IZQ"])
    filas.sort(key=lambda c: (c["tema"], c["id"]))

    os.makedirs(os.path.dirname(args.salida), exist_ok=True)
    with open(args.salida, "w", newline="", encoding="utf-8") as fh:
        escritor = csv.DictWriter(fh, fieldnames=CAMPOS)
        escritor.writeheader()
        escritor.writerows(filas)

    por_tema = {}
    for c in filas:
        por_tema[c["tema"]] = por_tema.get(c["tema"], 0) + 1
    print(f"{len(filas)} candidatas -> {args.salida}")
    for tema, n in sorted(por_tema.items()):
        print(f"  {tema:10s} {n}")


if __name__ == "__main__":
    main()
