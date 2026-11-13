# Pipeline: del corpus a la elección del clasificador

Qué hace cada fichero del pipeline y cómo se pasan los datos. Cubre las Fases 1 y 2.
La app web (Fase 5) no existe todavía.

Diagrama interactivo:
`.archify/dataflow-pipeline-clasificacion-20261001-162200/pipeline.html` (abrir en el
navegador).

## El flujo en una línea

corpus → filtros → `datos/pool.csv` → modelo de lenguaje → `datos/clasificacion/` →
comparación con la revisión humana → elección del modelo.

Todo se cruza por `id`: un hash de sesión, orador y frase (`filtros.id_frase`). No
depende del orden de lectura, así que sobrevive a que el corpus crezca.

## Ficheros, en orden de uso

| Paso | Fichero | Entra | Sale | Qué hace |
|---|---|---|---|---|
| 0 | `scripts/obtener_corpus.sh` | repo `escano-abierto` | `corpus/data/sesiones/*.json` | Descarga el corpus (541 MB, no versionado). |
| 1 | `scripts/filtros.py` | una sesión | candidatas | Módulo, no se ejecuta solo. Reglas formales: longitud, tema por palabra clave, autodelación, citas de terceros, otras lenguas, saneamiento del parseo. Asigna el `id`. |
| 1 | `scripts/medir_temas.py` | corpus | tabla en pantalla | Diagnóstico: volumen y balance por tema. Con él se eligieron sanidad, vivienda y pensiones. |
| 2 | `scripts/pool.py` | corpus | `datos/pool.csv` | Aplica los filtros a todo el corpus (a través de `muestrear.construir_pool`), deduplica y exporta las 4.281 candidatas con su fuente. |
| 3 | `prompts/clasificador_v1.txt` | | | El prompt. Dos preguntas: ¿trata del tema? ¿afirma algo discutible? Se publica en la metodología. Cambiarlo es crear `v2`, no editar `v1`. |
| 3 | `scripts/muestra_revision.py` | `datos/pool.csv` | `datos/revision/revision_ciega.csv` y `revision_fuente_NO_ABRIR.csv` | 50 frases al azar (semilla 1), mitad de cada bloque. La hoja ciega solo lleva id, tema y frase. No sobrescribe una revisión empezada. |
| 3 | `scripts/clasificar.py` | cualquier CSV con id, tema y frase | `datos/clasificacion/<modelo>__<prompt>.jsonl` | Envía lotes de 20 al modelo por LiteLLM. Lo que el modelo no devuelve se reintenta frase a frase; si sigue sin respuesta se cuenta como incidencia y no se escribe. Reanudable. |
| 4 | `scripts/comparar.py` | revisión rellenada y los `.jsonl` | tabla en pantalla | Por modelo y pregunta: acuerdo, kappa de Cohen, relleno que deja pasar y frases válidas que descarta. |
| | `scripts/muestrear.py` | corpus | `datos/muestras/candidatas.csv` | Muestra equilibrada para el catálogo final (Fase 4). `pool.py` reutiliza su `construir_pool`. |

## Tres garantías y dónde viven

1. **El modelo no ve el partido.** `clasificar.renderizar` solo envía tema y texto.
   Test: `test_el_modelo_no_ve_grupo_ni_orador`.
2. **Una respuesta que falta no es un descarte.** `clasificar.clasificar_lote`
   reintenta y cuenta incidencias por tipo (`parcial`, `recuperada`,
   `sin_respuesta`, `transporte`). Tests: `test_lo_que_falta_se_reintenta...` y
   `test_sin_respuesta_no_se_escribe`.
3. **La revisión humana es ciega.** `muestra_revision.hoja_ciega` deja fuera grupo,
   orador y fuente. Test: `test_hoja_ciega_no_lleva_fuente`.

## El modelo: LiteLLM en un servidor local

`clasificar.py` habla con un LiteLLM (`--base-url`, por defecto `http://localhost:4000/v1`),
un endpoint compatible con OpenAI que enruta por nombre: los modelos sin prefijo van a
Ollama en local (gratis, el dato no sale de casa) y los `or-*` a OpenRouter (de
pago). La clave se pasa en `LITELLM_API_KEY`.

Criterio de elección (ver `DECISIONES.md`, 2026-10-01): gana el modelo más barato
que coincida suficientemente con la revisión humana, con preferencia por pesos
abiertos para que la selección sea reproducible.

## Cómo se ejecuta

```bash
./.venv/bin/python scripts/pool.py corpus/data/sesiones
./.venv/bin/python scripts/muestra_revision.py --n 50 --semilla 1
# la persona que revisa rellena tema_ok y postura (1/0) en datos/revision/revision_ciega.csv
LITELLM_API_KEY=... ./.venv/bin/python scripts/clasificar.py \
    --entrada datos/revision/revision_ciega.csv --modelo qwen3-32b
./.venv/bin/python scripts/comparar.py
```

`datos/` no se versiona: todo se regenera con los scripts y la semilla.
