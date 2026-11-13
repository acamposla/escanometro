#!/usr/bin/env python3
"""Saca la muestra de revision humana del clasificador, a ciegas.

La revision de Alejandro es el patron contra el que se mide cada modelo. Para que
su criterio no entre por la puerta de atras, la hoja de revision solo lleva el
texto y el tema: ni grupo, ni orador, ni lo que haya dicho ningun modelo. La
fuente completa va a un fichero aparte que no se abre hasta terminar.

Uso:  python scripts/muestra_revision.py --n 50 --semilla 1
"""

import argparse
import csv
import os
import random

CIEGA = ["id", "tema", "frase", "tema_ok", "postura"]


def leer_pool(ruta):
    with open(ruta, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def muestra_equilibrada(filas, n, semilla):
    """Mitad de cada bloque, al azar con semilla fija, como el catalogo."""
    if n % 2:
        raise ValueError("n debe ser par para que la muestra quede equilibrada")
    por_bloque = {"DER": [], "IZQ": []}
    for f in filas:
        por_bloque[f["bloque"]].append(f)
    rng = random.Random(semilla)
    seleccion = []
    for bloque in ("DER", "IZQ"):
        if len(por_bloque[bloque]) < n // 2:
            raise ValueError(f"el bloque {bloque} no tiene {n // 2} candidatas")
        seleccion += rng.sample(por_bloque[bloque], n // 2)
    rng.shuffle(seleccion)
    return seleccion


def hoja_ciega(seleccion):
    return [
        {"id": f["id"], "tema": f["tema"], "frase": f["frase"], "tema_ok": "", "postura": ""}
        for f in seleccion
    ]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default="datos/pool.csv")
    ap.add_argument("--n", type=int, default=50)
    ap.add_argument("--semilla", type=int, default=1)
    ap.add_argument("--dir", default="datos/revision")
    args = ap.parse_args()

    seleccion = muestra_equilibrada(leer_pool(args.pool), args.n, args.semilla)
    os.makedirs(args.dir, exist_ok=True)

    ruta_ciega = os.path.join(args.dir, "revision_ciega.csv")
    if os.path.exists(ruta_ciega):
        raise SystemExit(f"{ruta_ciega} ya existe: no se sobrescribe una revision empezada.")
    with open(ruta_ciega, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=CIEGA)
        w.writeheader()
        w.writerows(hoja_ciega(seleccion))

    ruta_fuente = os.path.join(args.dir, "revision_fuente_NO_ABRIR.csv")
    with open(ruta_fuente, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(seleccion[0].keys()))
        w.writeheader()
        w.writerows(seleccion)

    print(f"Hoja de revision: {ruta_ciega} ({len(seleccion)} frases, semilla {args.semilla})")
    print("Rellena tema_ok y postura con 1 (si) o 0 (no).")
    print(f"Fuente completa aparte: {ruta_fuente}")


if __name__ == "__main__":
    main()
