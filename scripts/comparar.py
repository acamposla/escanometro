#!/usr/bin/env python3
"""Compara cada modelo con la revision humana a ciegas.

Por cada modelo y cada pregunta (tema_ok, postura): acuerdo simple, kappa de
Cohen (acuerdo descontando el azar) y los dos tipos de error por separado,
porque no cuestan lo mismo. Dejar pasar relleno abarata el juego; descartar una
frase valida solo reduce el pool.

Uso:  python scripts/comparar.py
"""

import argparse
import csv
import glob
import json
import os

PREGUNTAS = ("tema_ok", "postura", "rol")


def leer_revision(ruta):
    """{id: {pregunta: bool}} con las filas ya rellenadas, y las dudas aparte.

    Un "1?" o "0?" es una respuesta con duda: cuenta con su valor, y ademas se
    devuelve en `dudas` para poder medir sin ella. Un desacuerdo en una frase
    dudosa no es el mismo error que en una clara.
    """
    salida, dudas, temas = {}, set(), {}
    with open(ruta, encoding="utf-8-sig") as fh:
        for f in csv.DictReader(fh):
            valores = {p: f[p].strip() for p in PREGUNTAS if p in f}
            if all(v.rstrip("?") in ("0", "1") for v in valores.values()):
                temas[f["id"]] = f["tema"]
                salida[f["id"]] = {p: v.rstrip("?") == "1" for p, v in valores.items()}
                if any(v.endswith("?") for v in valores.values()):
                    dudas.add(f["id"])
    return salida, dudas, temas


def leer_modelo(ruta, temas):
    """{id: registro}, eligiendo el registro del tema con el que la frase entro en
    la revision. Los ficheros anteriores al 2026-10-04 no guardan el tema."""
    salida = {}
    with open(ruta, encoding="utf-8") as fh:
        for r in map(json.loads, filter(str.strip, fh)):
            if "tema" in r and temas.get(r["id"]) != r["tema"]:
                continue
            salida[r["id"]] = r
    return salida


def metricas(pares):
    """pares: lista de (humano, modelo) booleanos."""
    n = len(pares)
    if not n:
        return None
    acuerdo = sum(h == m for h, m in pares) / n
    p_h = sum(h for h, _ in pares) / n
    p_m = sum(m for _, m in pares) / n
    azar = p_h * p_m + (1 - p_h) * (1 - p_m)
    kappa = (acuerdo - azar) / (1 - azar) if azar < 1 else 1.0
    return {
        "n": n,
        "acuerdo": acuerdo,
        "kappa": kappa,
        "deja_pasar": sum((not h) and m for h, m in pares),
        "descarta": sum(h and (not m) for h, m in pares),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--revision", default="datos/revision/revision_ciega.csv")
    ap.add_argument("--dir", default="datos/clasificacion")
    args = ap.parse_args()

    humano, dudas, temas = leer_revision(args.revision)
    if not humano:
        raise SystemExit("La revision no tiene filas rellenadas con 1 o 0.")
    print(f"Revision humana: {len(humano)} frases, {len(dudas)} con duda\n")
    print(f"{'modelo':38s} {'pregunta':9s} {'frases':8s} {'n':>3s} {'acuerdo':>8s} {'kappa':>6s} {'deja_pasar':>10s} {'descarta':>8s}")
    for ruta in sorted(glob.glob(os.path.join(args.dir, "*.jsonl"))):
        modelo = leer_modelo(ruta, temas)
        nombre = os.path.basename(ruta)[: -len(".jsonl")]
        for p in [q for q in PREGUNTAS if any(q in h for h in humano.values())]:
            for rotulo, excluir in (("todas", set()), ("sin duda", dudas)):
                if rotulo == "sin duda" and not dudas:
                    continue
                pares = [
                    (h[p], modelo[i][p])
                    for i, h in humano.items()
                    if i in modelo and p in modelo[i] and i not in excluir
                ]
                m = metricas(pares)
                if m:
                    print(
                        f"{nombre:38s} {p:9s} {rotulo:8s} {m['n']:3d} {m['acuerdo']:8.0%} {m['kappa']:6.2f} "
                        f"{m['deja_pasar']:10d} {m['descarta']:8d}"
                    )
        faltan = len(set(humano) - set(modelo))
        if faltan:
            print(f"{'':38s} (sin respuesta del modelo en {faltan} frases)")


if __name__ == "__main__":
    main()
