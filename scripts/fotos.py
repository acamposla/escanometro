#!/usr/bin/env python3
"""Descarga el retrato oficial de cada orador del catalogo, sin modificarlo.

Fuente: congreso.es (docu/imgweb/diputados/<codigo>_15.jpg). El aviso legal del
Congreso permite reutilizar su informacion sin alterarla, citando la fuente y la
fecha: por eso la imagen se guarda tal cual y la web muestra "Foto: Congreso de los
Diputados" con la fecha de descarga. Se alojan en la propia web (web/fotos/) para que
el navegador del jugador no haga peticiones a un tercero.

El orador del corpus ("Apellido1 Apellido2") se cruza con el hemiciclo del corpus
("Apellidos, Nombre" -> codigo). Si no hay coincidencia unica (baja durante la
legislatura, apellidos repetidos), no hay foto: una foto equivocada es una
atribucion falsa.

Uso:  python scripts/fotos.py datos/catalogo/candidatos.csv
"""

import argparse
import csv
import datetime
import json
import os
import time
import unicodedata
import urllib.request

URL = "https://www.congreso.es/docu/imgweb/diputados/{codigo}_15.jpg"


def clave(texto):
    t = unicodedata.normalize("NFD", texto or "")
    return " ".join("".join(c for c in t if unicodedata.category(c) != "Mn").lower().split())


def indice_hemiciclo(ruta):
    """{apellidos normalizados: [codigos]} a partir de "Apellidos, Nombre"."""
    with open(ruta, encoding="utf-8") as fh:
        escanos = json.load(fh)["escanos"]
    indice = {}
    for nombre, datos in escanos.items():
        apellidos = nombre.split(",")[0]
        indice.setdefault(clave(apellidos), []).append(datos["codigo"])
    return indice


def codigo_de(orador, indice):
    """Codigo si la coincidencia es unica; None si no hay o es ambigua."""
    codigos = indice.get(clave(orador), [])
    return codigos[0] if len(codigos) == 1 else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("catalogo")
    ap.add_argument("--hemiciclo", default="corpus/data/hemiciclo.json")
    ap.add_argument("--destino", default="web/fotos")
    ap.add_argument("--salida", default="datos/catalogo/fotos.csv")
    args = ap.parse_args()

    indice = indice_hemiciclo(args.hemiciclo)
    with open(args.catalogo, encoding="utf-8") as fh:
        oradores = sorted({f["orador"] for f in csv.DictReader(fh)})
    os.makedirs(args.destino, exist_ok=True)
    hoy = datetime.datetime.now(datetime.timezone.utc).date().isoformat()
    filas = []
    for orador in oradores:
        codigo = codigo_de(orador, indice)
        estado, foto = "sin_codigo", ""
        if codigo is not None:
            ruta = os.path.join(args.destino, f"{codigo}.jpg")
            if not os.path.exists(ruta):
                peticion = urllib.request.Request(URL.format(codigo=codigo), headers={"User-Agent": "Mozilla/5.0"})
                try:
                    with urllib.request.urlopen(peticion, timeout=30) as r:
                        datos = r.read()
                        tipo = r.headers.get("Content-Type", "")
                except OSError:
                    datos, tipo = b"", ""
                if tipo.startswith("image/jpeg") and datos[:2] == b"\xff\xd8":
                    with open(ruta, "wb") as fh:
                        fh.write(datos)
                time.sleep(0.3)  # sin rafagas contra el servidor del Congreso
            if os.path.exists(ruta):
                estado, foto = "ok", f"fotos/{codigo}.jpg"
            else:
                estado = "sin_imagen"
        filas.append({"orador": orador, "codigo": codigo or "", "foto": foto, "estado": estado, "descarga": hoy})
    with open(args.salida, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(filas[0].keys()))
        w.writeheader()
        w.writerows(filas)
    resumen = {}
    for f in filas:
        resumen[f["estado"]] = resumen.get(f["estado"], 0) + 1
    print(f"{len(filas)} oradores -> {args.salida}: {resumen}")


if __name__ == "__main__":
    main()
