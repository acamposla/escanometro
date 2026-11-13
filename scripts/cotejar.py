#!/usr/bin/env python3
"""Coteja cada frase del catalogo con el PDF oficial del Diario de Sesiones.

Dos comprobaciones por frase:
1. La frase aparece en el PDF, palabra por palabra en el mismo orden (sin
   distinguir mayusculas, signos, saltos de linea ni cortes de palabra con guion).
2. El turno de palabra en que aparece es del orador que atribuye el corpus: se
   busca la ultima cabecera "El senor/La senora APELLIDOS:" antes de la frase,
   saltando las de la presidencia.

Lo que no pase cualquiera de las dos lo revisa una persona contra el PDF. Lo que
pase, tambien en una muestra. Necesita `pdftotext` (poppler).

Uso:  python scripts/cotejar.py datos/catalogo/catalogo_v1.csv
"""

import argparse
import csv
import os
import re
import subprocess
import unicodedata
import urllib.request

_CABECERA = re.compile(
    # Mayusculas espanolas y catalanas (SARRIÀ, PUIGNERÒ, LLAÇA): sin la À el script
    # se saltaba la cabecera y atribuia la frase al orador anterior.
    r"(?:El|La) se(?:ñ|n)ora? ([A-ZÀ-ÝÑÜÇ][A-ZÀ-ÝÑÜÇ·' \-]+?)(?: \([^)]*\))?:"
)


def sin_tildes(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn")


def texto_pdf(url, cache):
    os.makedirs(cache, exist_ok=True)
    nombre = os.path.join(cache, os.path.basename(url))
    if not os.path.exists(nombre):
        peticion = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(peticion, timeout=120) as resp, open(nombre, "wb") as fh:
            fh.write(resp.read())
    txt = nombre[:-4] + ".txt"
    if not os.path.exists(txt):
        subprocess.run(["pdftotext", nombre, txt], check=True)
    with open(txt, encoding="utf-8", errors="replace") as fh:
        return fh.read()


_PRESIDENCIA = re.compile(r"^(VICE)?PRESIDENT[AE]", re.I)


def patron_frase(frase):
    """Regex que encuentra la frase en el texto original del PDF: palabras separadas
    por cualquier signo o salto, y un posible corte con guion dentro de cada palabra."""
    palabras = re.findall(r"\w+", frase)
    trozos = []
    for p in palabras:
        partes = [re.escape(p[0])]
        for a, b in zip(p, p[1:]):
            # Entre cifras, el PDF pone un espacio de millares ("28 394") que el corpus quita.
            partes.append("[\\s\u00a0\u202f]?" if a.isdigit() and b.isdigit() else "(?:-\\s*)?")
            partes.append(re.escape(b))
        trozos.append("".join(partes))
    # Entre palabras, cualquier signo o salto, y las acotaciones del taquigrafo
    # ("(aplausos)"), que el corpus elimina y el PDF conserva.
    return re.compile(r"(?:\W|\([^)]{0,60}\))+".join(trozos), re.I)


def orador_antes(texto, posicion):
    """Apellidos de la ultima cabecera de turno anterior a la posicion, saltando las
    de la presidencia, que interviene a mitad de turno sin quitar la palabra."""
    for c in reversed(list(_CABECERA.finditer(texto[:posicion]))):
        nombre = c.group(1).strip()
        if not _PRESIDENCIA.match(nombre):
            return nombre
    return ""


def coincide_orador(orador_corpus, orador_pdf):
    """El corpus da "Apellido1 Apellido2"; el PDF, "APELLIDO1 APELLIDO2"."""
    a = sin_tildes(orador_corpus or "").lower().split()
    b = sin_tildes(orador_pdf or "").lower().split()
    return bool(a) and set(a) <= set(b)


def cotejar(fila, texto):
    m = patron_frase(fila["frase"]).search(texto)
    if not m:
        return {"encontrada": 0, "orador_pdf": "", "orador_ok": 0}
    orador_pdf = orador_antes(texto, m.start())
    return {"encontrada": 1, "orador_pdf": orador_pdf, "orador_ok": int(coincide_orador(fila["orador"], orador_pdf))}


def texto_maquetado(pdf, cache):
    """Segundo metodo, independiente del primero: el texto con la maquetacion de la
    pagina (pdftotext -layout). El texto plano a veces altera el orden de los bloques
    y deja la cabecera de un turno antes de una frase de otro; aqui se lee en el orden
    en que esta impreso. Lo que los dos metodos confirman se da por cotejado."""
    destino = os.path.join(cache, os.path.basename(pdf)[:-4] + ".layout.txt")
    if not os.path.exists(destino):
        subprocess.run(["pdftotext", "-layout", pdf, destino], check=True)
    with open(destino, encoding="utf-8", errors="replace") as fh:
        return fh.read()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("catalogo")
    ap.add_argument("--cache", default="datos/pdf")
    ap.add_argument("--salida", default=None)
    ap.add_argument("--maquetado", action="store_true", help="segundo metodo: texto con la maquetacion de la pagina")
    args = ap.parse_args()

    with open(args.catalogo, encoding="utf-8") as fh:
        filas = list(csv.DictReader(fh))
    salida = args.salida or args.catalogo.replace(".csv", "_cotejo.csv")
    resultado = []
    for f in filas:
        try:
            texto = texto_pdf(f["pdf"], args.cache)
            if args.maquetado:
                texto = texto_maquetado(os.path.join(args.cache, os.path.basename(f["pdf"])), args.cache)
            r = cotejar(f, texto)
        except (OSError, subprocess.CalledProcessError) as e:  # PDF caido o ilegible: lo revisa una persona
            r = {"encontrada": "", "orador_pdf": f"ERROR: {e}", "orador_ok": ""}
        resultado.append(dict(f, **r))
    with open(salida, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(resultado[0].keys()))
        w.writeheader()
        w.writerows(resultado)
    ok = sum(1 for r in resultado if r["encontrada"] == 1 and r["orador_ok"] == 1)
    print(f"{ok}/{len(resultado)} encontradas y con el orador correcto -> {salida}")
    for r in resultado:
        if not (r["encontrada"] == 1 and r["orador_ok"] == 1):
            print(f"  REVISAR {r['id']} | encontrada={r['encontrada']} | corpus={r['orador']} | pdf={r['orador_pdf']}")


if __name__ == "__main__":
    main()
