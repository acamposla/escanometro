#!/usr/bin/env python3
"""Clasifica candidatas con un modelo de lenguaje: tema real, postura y, desde v3, rol.

Habla con cualquier endpoint compatible con OpenAI (/v1/chat/completions). Por
defecto, un LiteLLM local, que enruta por nombre a Ollama local o a
OpenRouter: el mismo script compara modelos locales y de pago cambiando solo
--modelo.

El modelo solo ve el tema y el texto. Nunca el grupo ni el orador: el
clasificador decide si la frase sirve, no de que lado es.

Una frase que el modelo no devuelve no es un veredicto, es trabajo sin hacer: se
reintenta sola y, si sigue sin respuesta, se cuenta como incidencia y no se
escribe.

Uso:
  LITELLM_API_KEY=... python scripts/clasificar.py --entrada datos/revision/revision_ciega.csv --modelo qwen3-32b
"""

import argparse
import collections
import csv
import hashlib
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPT_DEFECTO = os.path.join(RAIZ, "prompts", "clasificador_v1.txt")

# Tras tantos lotes seguidos sin conexion, el endpoint esta caido: seguir solo
# convierte el pool entero en incidencias en unos segundos.
MAX_CAIDAS_SEGUIDAS = 3

_PENSAMIENTO = re.compile(r"<think>.*?</think>", re.DOTALL)


def cargar_prompt(ruta):
    with open(ruta, encoding="utf-8") as fh:
        texto = fh.read()
    version = os.path.splitext(os.path.basename(ruta))[0]
    huella = hashlib.sha1(texto.encode("utf-8")).hexdigest()[:8]
    return texto, version, huella


def renderizar(prompt, lote):
    lineas = [f'{i}. [{c["tema"]}] {c["frase"]}' for i, c in enumerate(lote, 1)]
    return prompt.rstrip() + "\n\n" + "\n".join(lineas)


def campos_de(prompt):
    """Preguntas que pide el prompt, en orden. v1 y v2 piden tema y postura; v3
    anade rol (si la frase delata a quien gobierna o a la oposicion). El prompt de
    calidad pide si se entiende sola, si afirma algo y si delata al orador."""
    if '"entiende"' in prompt:
        return ("entiende", "afirma", "delata")
    return ("tema", "postura", "rol") if '"rol"' in prompt else ("tema", "postura")


def parsear(texto, n, campos=("tema", "postura")):
    """Devuelve {posicion: (valor de cada campo)} con las entradas validas.

    Tolera texto alrededor del JSON y bloques de razonamiento. Descarta en
    silencio lo que no sea un booleano: una entrada mal formada cuenta como no
    devuelta y va al reintento.
    """
    texto = _PENSAMIENTO.sub("", texto or "")
    inicio, fin = texto.find("{"), texto.rfind("}")
    if inicio < 0 or fin <= inicio:
        return {}
    try:
        datos = json.loads(texto[inicio : fin + 1])
    except json.JSONDecodeError:
        return {}
    salida = {}
    for r in datos.get("resultados", []) if isinstance(datos, dict) else []:
        if not isinstance(r, dict):
            continue
        pos, valores = r.get("n"), tuple(r.get(c) for c in campos)
        if isinstance(pos, int) and 1 <= pos <= n and all(isinstance(v, bool) for v in valores):
            salida[pos] = valores
    return salida


# Tope de la respuesta. OpenRouter reserva por adelantado el coste maximo de cada
# llamada; sin tope, con poco saldo devuelve 402 aunque la llamada real cueste centimos
# (2026-10-05). Un lote de 15 frases responde en unos 600 tokens. Los modelos locales que
# razonan antes de contestar (qwen3.6-35b: ~5.600 tokens por lote) necesitan ir sin tope
# (--max-tokens 0): con 3.000 se cortaban y cada lote acababa repitiendose frase a frase.
MAX_TOKENS = 3000


def llamar(base_url, clave, modelo, contenido, timeout, max_tokens=MAX_TOKENS):
    peticion_json = {
        "model": modelo,
        "temperature": 0,
        "messages": [{"role": "user", "content": contenido}],
    }
    if max_tokens:
        peticion_json["max_tokens"] = max_tokens
    cuerpo = json.dumps(peticion_json).encode("utf-8")
    peticion = urllib.request.Request(
        base_url.rstrip("/") + "/chat/completions",
        data=cuerpo,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {clave}"},
    )
    with urllib.request.urlopen(peticion, timeout=timeout) as resp:
        datos = json.load(resp)
    return datos["choices"][0]["message"].get("content") or ""


def clasificar_lote(lote, prompt, llamada, incidencias):
    """Clasifica un lote; lo que falte se reintenta frase a frase una vez."""
    campos = campos_de(prompt)
    resultados = {}
    try:
        crudo = parsear(llamada(renderizar(prompt, lote)), len(lote), campos)
    except (OSError, KeyError, ValueError) as e:
        incidencias["transporte"] += 1
        print(f"  error de transporte en lote: {e}", file=sys.stderr)
        crudo = {}
    for pos, valor in crudo.items():
        resultados[clave(lote[pos - 1])] = valor
    faltan = [c for c in lote if clave(c) not in resultados]
    if faltan and crudo:
        incidencias["parcial"] += 1
    for c in faltan:
        try:
            uno = parsear(llamada(renderizar(prompt, [c])), 1, campos)
        except (OSError, KeyError, ValueError):
            uno = {}
        if 1 in uno:
            resultados[clave(c)] = uno[1]
            incidencias["recuperada"] += 1
        else:
            incidencias["sin_respuesta"] += 1
    return resultados


def clave(fila):
    """Una frase puede estar en varios temas y su veredicto cambia con el tema:
    el resultado se identifica por (id, tema), nunca solo por id."""
    return (fila["id"], fila["tema"])


def ya_hechas(ruta):
    if not os.path.exists(ruta):
        return set()
    with open(ruta, encoding="utf-8") as fh:
        return {(r["id"], r["tema"]) for r in map(json.loads, filter(str.strip, fh))}


def slug(modelo):
    return re.sub(r"[^A-Za-z0-9._-]+", "_", modelo)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--entrada", default="datos/pool.csv", help="CSV con id, tema y frase")
    ap.add_argument("--modelo", required=True)
    ap.add_argument("--base-url", default="http://localhost:4000/v1")
    ap.add_argument("--clave-env", default="LITELLM_API_KEY")
    ap.add_argument("--prompt", default=PROMPT_DEFECTO)
    ap.add_argument("--lote", type=int, default=20)
    ap.add_argument("--timeout", type=int, default=600)
    ap.add_argument("--dir", default="datos/clasificacion")
    ap.add_argument("--max-tokens", type=int, default=MAX_TOKENS,
                    help="tope de la respuesta; 0 = sin tope (modelos locales que razonan)")
    args = ap.parse_args()

    clave_api = os.environ.get(args.clave_env)
    if not clave_api:
        raise SystemExit(f"Falta la clave en la variable {args.clave_env}.")

    prompt, version, huella = cargar_prompt(args.prompt)
    with open(args.entrada, encoding="utf-8") as fh:
        filas = list(csv.DictReader(fh))

    os.makedirs(args.dir, exist_ok=True)
    salida = os.path.join(args.dir, f"{slug(args.modelo)}__{version}.jsonl")
    hechas = ya_hechas(salida)
    pendientes = [f for f in filas if clave(f) not in hechas]
    print(f"{args.modelo} | prompt {version} ({huella}) | {len(pendientes)} pendientes de {len(filas)}")

    def llamada(contenido):
        return llamar(args.base_url, clave_api, args.modelo, contenido, args.timeout, args.max_tokens)

    incidencias = collections.Counter()
    inicio = time.time()
    caidas_seguidas = 0
    with open(salida, "a", encoding="utf-8") as fh:
        for i in range(0, len(pendientes), args.lote):
            lote = pendientes[i : i + args.lote]
            antes = incidencias["transporte"]
            resultados = clasificar_lote(lote, prompt, llamada, incidencias)
            caidas_seguidas = caidas_seguidas + 1 if not resultados and incidencias["transporte"] > antes else 0
            if caidas_seguidas >= MAX_CAIDAS_SEGUIDAS:
                raise SystemExit(
                    f"{MAX_CAIDAS_SEGUIDAS} lotes seguidos sin conexion con {args.base_url}: se para "
                    "en vez de recorrer el pool en vacio. Lo ya escrito se conserva; relanzar reanuda."
                )
            for (id_, tema), valores in resultados.items():
                registro = {"id": id_, "tema": tema}
                for campo, valor in zip(campos_de(prompt), valores):
                    registro["tema_ok" if campo == "tema" else campo] = valor
                registro |= {
                    "modelo": args.modelo,
                    "prompt": version,
                    "prompt_sha": huella,
                }
                fh.write(json.dumps(registro, ensure_ascii=False) + "\n")
            fh.flush()
            print(f"  {min(i + args.lote, len(pendientes))}/{len(pendientes)}")

    total = len(ya_hechas(salida) & {clave(f) for f in filas})
    print(f"Hecho en {time.time() - inicio:.0f} s. Clasificadas {total}/{len(filas)} -> {salida}")
    print("Incidencias: " + (", ".join(f"{k} {v}" for k, v in sorted(incidencias.items())) or "ninguna"))


if __name__ == "__main__":
    main()
