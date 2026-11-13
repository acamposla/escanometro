#!/usr/bin/env python3
"""Construye el catalogo del juego a partir del pool clasificado, en dos pasos.

1. `candidatos`: entre las combinaciones que sobreviven al clasificador (tema y
   postura), baraja cada celda tema x bloque con semilla fija y toma las N primeras
   mas unas reservas. Una frase que esta en dos temas solo entra una vez.
2. `final`: los candidatos se reclasifican frase a frase (lote 1, reproducible) con
   `clasificar.py`. En cada celda entran, en el orden barajado, las N primeras que
   vuelven a pasar. La etiqueta de rol (v3) se anade como dato, no como filtro.

Nadie elige una frase: el orden lo fija la semilla y la entrada la fija el modelo.

Uso:
  python scripts/catalogo.py candidatos --clasificacion datos/clasificacion/qwen3-32b__clasificador_v2__pool.jsonl
  python scripts/clasificar.py --entrada datos/catalogo/candidatos.csv --modelo qwen3-32b \\
      --prompt prompts/clasificador_v2.txt --lote 1 --dir datos/catalogo/lote1
  (igual con clasificador_v3.txt)
  python scripts/catalogo.py final
"""

import argparse
import csv
import hashlib
import json
import os

TEMAS = ("pensiones", "sanidad", "vivienda")
BLOQUES = ("DER", "IZQ")


def leer_csv(ruta):
    with open(ruta, encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def leer_jsonl(ruta):
    with open(ruta, encoding="utf-8") as fh:
        return {(r["id"], r["tema"]): r for r in map(json.loads, filter(str.strip, fh))}


def sobrevive(r):
    return bool(r and r["tema_ok"] and r["postura"])


def clave_sorteo(semilla, fila):
    """Posicion de una frase en el sorteo, que depende solo de la semilla y de la
    propia frase. Asi, quitar frases del pool (un filtro nuevo) no reordena las demas
    ni tira el trabajo ya hecho con ellas. Antes se barajaba la lista entera."""
    return hashlib.sha256(f"{semilla}|{fila['id']}|{fila['tema']}".encode("utf-8")).hexdigest()


def apta(jueces, clave):
    """Calidad (catalogo 2, prompts/calidad_v2.txt): la frase entra solo si TODOS los
    jueces la han juzgado y todos dicen que se entiende sola, que afirma algo y que no
    delata al orador. Sin veredicto de algun juez, no entra."""
    for juez in jueces:
        r = juez.get(clave)
        if not r or not r["entiende"] or not r["afirma"] or r["delata"]:
            return False
    return True


def candidatos(pool, clasificacion, por_celda, reservas, semilla, jueces=()):
    """Lista ordenada de candidatos por celda, con su posicion en el sorteo."""
    usados = set()
    salida = []
    for tema in TEMAS:
        for bloque in BLOQUES:
            celda = [
                f for f in pool
                if f["tema"] == tema and f["bloque"] == bloque
                and sobrevive(clasificacion.get((f["id"], f["tema"])))
                and apta(jueces, (f["id"], f["tema"]))
            ]
            celda.sort(key=lambda f: clave_sorteo(semilla, f))
            tomados = 0
            for f in celda:
                if f["id"] in usados:
                    continue
                usados.add(f["id"])
                tomados += 1
                salida.append(dict(f, orden=tomados))
                if tomados == por_celda + reservas:
                    break
            if tomados < por_celda:
                raise ValueError(f"{tema}/{bloque}: solo {tomados} candidatos, se piden {por_celda}")
    return salida


def final(cands, confirmacion, rol, por_celda, excluir=frozenset()):
    """En cada celda, las N primeras (por orden del sorteo) que se confirman con lote 1
    y no han sido retiradas por el criterio 11 (`excluir`, ids de frase)."""
    salida = []
    for tema in TEMAS:
        for bloque in BLOQUES:
            celda = sorted(
                (c for c in cands if c["tema"] == tema and c["bloque"] == bloque),
                key=lambda c: int(c["orden"]),
            )
            elegidas = [
                c for c in celda
                if c["id"] not in excluir and sobrevive(confirmacion.get((c["id"], c["tema"])))
            ][:por_celda]
            if len(elegidas) < por_celda:
                raise ValueError(f"{tema}/{bloque}: solo {len(elegidas)} confirmadas, faltan reservas")
            for c in elegidas:
                etiqueta = rol.get((c["id"], c["tema"]))
                salida.append(dict(c, rol="" if etiqueta is None else int(etiqueta["rol"])))
    return salida


def escribir(ruta, filas):
    os.makedirs(os.path.dirname(ruta), exist_ok=True)
    with open(ruta, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="paso", required=True)
    c = sub.add_parser("candidatos")
    c.add_argument("--pool", default="datos/pool.csv")
    c.add_argument("--clasificacion", required=True)
    c.add_argument("--por-celda", type=int, default=25)
    c.add_argument("--reservas", type=int, default=12)
    c.add_argument("--semilla", type=int, default=1)
    c.add_argument("--salida", default="datos/catalogo/candidatos.csv")
    c.add_argument("--calidad", action="append", default=[],
                   help="JSONL de un juez de calidad (repetible): la frase entra si todos la aprueban")
    f = sub.add_parser("final")
    f.add_argument("--candidatos", default="datos/catalogo/candidatos.csv")
    f.add_argument("--confirmacion", default="datos/catalogo/lote1/qwen3-32b__clasificador_v2.jsonl")
    f.add_argument("--rol", default="datos/catalogo/lote1/qwen3-32b__clasificador_v3.jsonl")
    f.add_argument("--por-celda", type=int, default=25)
    f.add_argument("--excluir", action="append", default=[],
                   help="CSV con columna frase_id de frases que no entran: criba del criterio 11 o "
                        "datos/catalogo/no_cotejadas.csv (repetible)")
    f.add_argument("--salida", default="datos/catalogo/catalogo_v1.csv")
    args = ap.parse_args()

    if args.paso == "candidatos":
        filas = candidatos(leer_csv(args.pool), leer_jsonl(args.clasificacion),
                           args.por_celda, args.reservas, args.semilla,
                           [leer_jsonl(r) for r in args.calidad])
        escribir(args.salida, filas)
        print(f"{len(filas)} candidatos -> {args.salida} (semilla {args.semilla})")
    else:
        rol = leer_jsonl(args.rol) if os.path.exists(args.rol) else {}
        excluir = frozenset(f["frase_id"] for ruta in args.excluir for f in leer_csv(ruta))
        filas = final(leer_csv(args.candidatos), leer_jsonl(args.confirmacion), rol, args.por_celda, excluir)
        escribir(args.salida, filas)
        print(f"{len(filas)} frases -> {args.salida}")
        if not rol:
            print("Aviso: sin etiqueta de rol (falta la pasada con v3).")


if __name__ == "__main__":
    main()
