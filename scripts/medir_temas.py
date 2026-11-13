#!/usr/bin/env python3
"""Mide volumen y balance por tema sobre el corpus.

El balance (frases del bloque menor / frases del bloque mayor) no es cosmetico:
si un bloque domina un tema, el jugador acierta deslizando siempre al mismo lado
sin leer, y el juego queda roto en silencio. Umbral de trabajo: 0,75.

Uso:  python scripts/medir_temas.py corpus/data/sesiones
"""

import collections
import glob
import json
import os
import re
import statistics
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import filtros  # noqa: E402

UMBRAL_BALANCE = 0.75

# Temas explorados el 2026-09-29 para elegir los del catalogo. Los tres de
# filtros.TEMAS son los que pasaron el corte; el resto se conserva para poder
# repetir la medicion y para documentar por que quedaron fuera.
TEMAS_EXPLORADOS = dict(
    filtros.TEMAS,
    energia=r"nuclear|renovable|el.ctric|apag.n|energ.tic",
    campo=r"agricultor|ganader|regad|sequ.a|agrari",
    inmigracion=r"inmigra|migrant|menas|frontera|extranjer|acogida|refugiad",
    educacion=r"educaci|universidad|profesorado|concertada|curr.cul",
    defensa=r"OTAN|Ucrania|gasto militar|defensa|rearm",
    trabajo=r"salario m.nimo|SMI|jornada laboral|convenio|despido|sindicat",
    memoria=r"memoria democr|franquis|dictadura|exhumaci|amnist",
    genero=r"violencia de g.nero|machis|feminis|igualdad de g.nero|aborto",
    turismo=r"turis|masificaci|crucer",
    agua=r"trasvase|desalad|hidrol.gic|caudal",
)


def cargar(ruta_sesiones):
    ficheros = sorted(glob.glob(os.path.join(ruta_sesiones, "*.json")))
    if not ficheros:
        raise SystemExit(
            f"No hay sesiones en {ruta_sesiones}. Ejecuta scripts/obtener_corpus.sh"
        )
    return [json.load(open(f, encoding="utf-8")) for f in ficheros]


def describir_corpus(sesiones):
    fechas = [s["fecha"] for s in sesiones if s.get("fecha")]
    sin_fecha = len(sesiones) - len(fechas)
    total_iv = sum(len(s.get("intervenciones", [])) for s in sesiones)
    grupos = collections.Counter(
        iv.get("grupo") or "SIN_GRUPO"
        for s in sesiones
        for iv in s.get("intervenciones", [])
    )
    largos = [
        len(iv.get("texto") or "")
        for s in sesiones
        for iv in s.get("intervenciones", [])
    ]
    print(f"sesiones: {len(sesiones)} (sin fecha, descartadas: {sin_fecha})")
    print(f"rango: {min(fechas)} -> {max(fechas)}")
    print(f"intervenciones: {total_iv}")
    print(
        f"longitud del texto: mediana {int(statistics.median(largos))} | "
        f"maximo {max(largos)}"
    )
    ruido = grupos.get("MESA", 0)
    print(f"de la Presidencia (ruido, se descarta): {ruido} ({100*ruido/total_iv:.0f}%)")
    print()


def medir(sesiones, temas):
    filas = []
    for tema, patron in temas.items():
        cuenta = collections.Counter()
        for s in sesiones:
            for c in filtros.candidatas_de_sesion(s, {tema: patron}):
                cuenta[c["bloque"]] += 1
        der, izq = cuenta["DER"], cuenta["IZQ"]
        balance = min(der, izq) / max(der, izq, 1)
        filas.append((tema, der, izq, der + izq, balance))
    return sorted(filas, key=lambda f: -f[4])


def main():
    ruta = sys.argv[1] if len(sys.argv) > 1 else "corpus/data/sesiones"
    sesiones = cargar(ruta)
    describir_corpus(sesiones)
    print(f"{'tema':13s} {'DER':>6s} {'IZQ':>6s} {'total':>7s} {'balance':>8s}  veredicto")
    for tema, der, izq, total, balance in medir(sesiones, TEMAS_EXPLORADOS):
        veredicto = "entra" if balance >= UMBRAL_BALANCE and total >= 500 else "fuera"
        marca = " *" if tema in filtros.TEMAS else "  "
        print(
            f"{tema:13s} {der:6d} {izq:6d} {total:7d} {balance:8.2f}  "
            f"{veredicto}{marca}"
        )
    print()
    print("* tema del catalogo inicial (definido en filtros.TEMAS)")
    print(f"umbral aplicado: balance >= {UMBRAL_BALANCE} y al menos 500 frases")


if __name__ == "__main__":
    main()
