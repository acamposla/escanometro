#!/usr/bin/env python3
"""Criterio 11: retira del catalogo las frases que casi todo el mundo acierta.

Regla fijada el 2026-10-04, antes de tener respuestas (docs/03_metodologia.md):
una frase sale cuando acumula al menos 15 respuestas y el 85% o mas son aciertos.
Se aplica a todas las frases a la vez y el umbral no se cambia a la vista de los datos.

Antes de contar se descartan las partidas con tiempos de reaccion imposibles
(mediana por debajo de 400 ms: reflejo, no juicio), segun la seccion 6 de la
metodologia. Se informa de cuantas.

Uso:
  python scripts/criba.py --version v-xxxxxxxx            # lee la base D1 remota
  python scripts/criba.py --version v-xxxxxxxx --csv respuestas.csv
La salida es datos/catalogo/criba_<version>.csv, que acepta `catalogo.py final --excluir`.
"""

import argparse
import csv
import json
import os
import statistics
import subprocess
from collections import defaultdict

MIN_RESPUESTAS = 15
UMBRAL_ACIERTO = 0.85
MS_MINIMO = 400


def partidas_validas(filas):
    """Ids de partida cuya mediana de tiempo de reaccion es plausible."""
    tiempos = defaultdict(list)
    for f in filas:
        if f.get("ms_reaccion") not in (None, ""):
            tiempos[f["sesion_juego"]].append(int(f["ms_reaccion"]))
    validas = {s for s in {f["sesion_juego"] for f in filas}}
    for s, ms in tiempos.items():
        if statistics.median(ms) < MS_MINIMO:
            validas.discard(s)
    return validas


def criba(filas, min_respuestas=MIN_RESPUESTAS, umbral=UMBRAL_ACIERTO):
    """Devuelve (retiradas, descartadas): las frases que salen, con sus cifras, y el
    numero de partidas descartadas por tiempos imposibles."""
    validas = partidas_validas(filas)
    descartadas = len({f["sesion_juego"] for f in filas}) - len(validas)
    por_frase = defaultdict(lambda: {"n": 0, "aciertos": 0, "seguras": 0})
    for f in filas:
        if f["sesion_juego"] not in validas:
            continue
        c = por_frase[f["frase_id"]]
        c["n"] += 1
        c["aciertos"] += int(f["acierto"])
        c["seguras"] += int(f["confianza"]) == 2
    retiradas = []
    for frase_id, c in sorted(por_frase.items()):
        if c["n"] >= min_respuestas and c["aciertos"] / c["n"] >= umbral:
            retiradas.append({"frase_id": frase_id, **c, "tasa": round(c["aciertos"] / c["n"], 3)})
    return retiradas, descartadas


def leer_d1(version):
    consulta = (
        "SELECT sesion_juego, frase_id, acierto, confianza, ms_reaccion FROM respuestas "
        f"WHERE version_catalogo = '{version}'"
    )
    salida = subprocess.run(
        ["wrangler", "d1", "execute", "sesgo-respuestas", "--remote", "--json", "--command", consulta],
        check=True, capture_output=True, text=True,
    ).stdout
    return json.loads(salida)[0]["results"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", required=True, help="version del catalogo (web/catalogo.json)")
    ap.add_argument("--csv", help="respuestas exportadas, en vez de leer D1")
    args = ap.parse_args()

    if not args.version.replace("-", "").isalnum():
        raise SystemExit("Version de catalogo no valida.")
    if args.csv:
        with open(args.csv, encoding="utf-8") as fh:
            filas = list(csv.DictReader(fh))
    else:
        filas = leer_d1(args.version)

    retiradas, descartadas = criba(filas)
    salida = f"datos/catalogo/criba_{args.version}.csv"
    os.makedirs(os.path.dirname(salida), exist_ok=True)
    with open(salida, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=["frase_id", "n", "aciertos", "seguras", "tasa"])
        w.writeheader()
        w.writerows(retiradas)
    frases = len({f["frase_id"] for f in filas})
    print(f"{len(filas)} respuestas, {frases} frases, {descartadas} partidas descartadas por tiempos imposibles.")
    print(f"Retiradas ({len(retiradas)}): >= {MIN_RESPUESTAS} respuestas y >= {UMBRAL_ACIERTO:.0%} de acierto -> {salida}")


if __name__ == "__main__":
    main()
