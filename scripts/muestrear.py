#!/usr/bin/env python3
"""Extrae una muestra aleatoria equilibrada de candidatas, con su fuente.

Aleatoria y con semilla fija a proposito: el muestreo tiene que ser repetible por
un tercero y nadie, tampoco yo, elige una frase por su contenido. Lo unico que
decide la entrada al catalogo es el filtro formal (filtros.py) y, despues, la
dificultad medida con jugadores reales.

Uso:  python scripts/muestrear.py corpus/data/sesiones --n 20 --semilla 1
"""

import argparse
import csv
import glob
import json
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import filtros  # noqa: E402

CAMPOS = ["id", "tema", "bloque", "grupo", "orador", "fecha", "ds", "pdf", "frase"]


def construir_pool(ruta_sesiones):
    pool = {"DER": [], "IZQ": []}
    for fichero in sorted(glob.glob(os.path.join(ruta_sesiones, "*.json"))):
        sesion = json.load(open(fichero, encoding="utf-8"))
        for candidata in filtros.candidatas_de_sesion(sesion):
            pool[candidata["bloque"]].append(candidata)
    if not pool["DER"] or not pool["IZQ"]:
        raise SystemExit(f"Pool vacio en {ruta_sesiones}. Revisa la ruta del corpus.")
    return pool


def muestrear(pool, n, semilla):
    """Mitad y mitad: el catalogo se equilibra por muestreo aunque el corpus no
    lo este, porque un catalogo desbalanceado es explotable."""
    por_bloque = n // 2
    for bloque in ("DER", "IZQ"):
        if len(pool[bloque]) < por_bloque:
            raise SystemExit(
                f"El bloque {bloque} solo tiene {len(pool[bloque])} candidatas, "
                f"se piden {por_bloque}."
            )
    rng = random.Random(semilla)
    seleccion = rng.sample(pool["DER"], por_bloque) + rng.sample(pool["IZQ"], por_bloque)
    rng.shuffle(seleccion)
    return seleccion


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sesiones", nargs="?", default="corpus/data/sesiones")
    ap.add_argument("--n", type=int, default=20, help="tamano de la muestra (par)")
    ap.add_argument("--semilla", type=int, default=1)
    ap.add_argument("--salida", default="datos/muestras/candidatas.csv")
    args = ap.parse_args()

    if args.n % 2:
        raise SystemExit("--n debe ser par para que la muestra quede equilibrada.")

    pool = construir_pool(args.sesiones)
    print(f"pool limpio: DER {len(pool['DER'])} | IZQ {len(pool['IZQ'])}")
    seleccion = muestrear(pool, args.n, args.semilla)

    for i, c in enumerate(seleccion, 1):
        print(f"\n{i:2d}. [{c['tema']}] {c['frase']}")
        print(f"     -> {c['grupo']} | {c['orador']} | {c['fecha']} | {c['ds']}")

    os.makedirs(os.path.dirname(args.salida), exist_ok=True)
    with open(args.salida, "w", newline="", encoding="utf-8") as fh:
        escritor = csv.DictWriter(fh, fieldnames=CAMPOS)
        escritor.writeheader()
        escritor.writerows(seleccion)
    print(f"\nGuardado en {args.salida} (semilla {args.semilla}, repetible).")


if __name__ == "__main__":
    main()
