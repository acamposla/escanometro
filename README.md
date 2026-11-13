# Escañómetro

Juego web con frases reales del Congreso de los Diputados: sale una frase del Diario de
Sesiones y el jugador apuesta si la dijo la izquierda (PSOE y Sumar) o la derecha (PP y
Vox), con "seguro" o "creo que". Al responder, la ficha enseña quién la dijo, su grupo,
la fecha y el enlace al PDF oficial de la sesión.

En producción en [escanometro.com](https://escanometro.com). La
[metodología](https://escanometro.com/metodologia.html) está publicada en la web.

Mide cuánto falla el eje izquierda-derecha como predictor de lo que se dice, como
**acierto condicionado a la confianza**: cuántas frases se atribuyen al bloque
equivocado estando seguro.

## Por qué se publica el código

Ninguna frase del catálogo se elige ni se descarta a mano. Todas las exclusiones están en
`scripts/filtros.py`, con sus tests en `tests/`. Si una exclusión no cabe en un filtro,
no se aplica. Este repositorio permite comprobarlo.

## Cómo se construye el catálogo

1. **Corpus.** Diario de Sesiones de la XV Legislatura, a partir del parseo abierto de
   [escano-abierto](https://github.com/jorgegarcelan/escano-abierto) (MIT).
   `scripts/obtener_corpus.sh` lo descarga (541 MB, no se versiona).
2. **Filtros** (`scripts/filtros.py`): longitud, tema por lista de palabras, sin
   autodelación (siglas, "nuestro grupo", "señor ministro"), sin citas de terceros, solo
   castellano y solo los cuatro grupos estatales.
3. **Clasificador** (`scripts/clasificar.py`, `prompts/clasificador_v2.txt`):
   `qwen3-32b` en local decide si la frase trata del tema y si afirma algo debatible.
   Nunca ve el partido ni el orador. Validado contra una revisión humana a ciegas de 50
   frases (`scripts/muestra_revision.py`, `scripts/comparar.py`).
4. **Juicio de calidad** (`prompts/calidad_v2.txt`): dos modelos independientes; la
   frase entra solo si aprueban los dos.
5. **Muestreo** con semilla fija y el mismo número de frases por tema y bloque
   (`scripts/catalogo.py`).
6. **Cotejo con el PDF oficial** por dos métodos, texto y orador (`scripts/cotejar.py`).
7. **Criba por dificultad** (`scripts/criba.py`): sale la frase con al menos 15
   respuestas y un 85 % o más de aciertos. La regla se fijó antes de tener respuestas.

Las decisiones de diseño, con fecha y la alternativa descartada, están en `DECISIONES.md`.

## Puesta en marcha

```bash
python3 -m venv .venv && ./.venv/bin/pip install -r requirements.txt
bash scripts/obtener_corpus.sh
./.venv/bin/python -m pytest tests/ -q
./.venv/bin/python scripts/medir_temas.py corpus/data/sesiones
```

La clasificación necesita un endpoint compatible con OpenAI (por ejemplo LiteLLM con
Ollama): `--base-url` y la clave en `LITELLM_API_KEY`.

La web es estática (`web/`) con funciones de Cloudflare Pages (`functions/api/`) y una
base D1 (`migrations/`). `wrangler.toml`, `web/medir.js` y `functions/api/u/send.js` llevan
identificadores de ejemplo: hay que poner los de una base D1 y una instancia de Umami
propias.

## Documentación

| Documento | Contenido |
|---|---|
| `docs/01_objetivos.md` | Qué mide y qué no |
| `docs/02_investigacion.md` | Corpus medido, temas con balance, hallazgos |
| `docs/03_metodologia.md` | Criterio de selección (versión de trabajo de la metodología publicada) |
| `docs/04_arquitectura.md` | Stack, páginas y esquema de datos |
| `docs/05_legal_y_anonimato.md` | Derechos sobre las frases, RGPD y LSSI |
| `docs/07_riesgos.md` | Riesgos del proyecto |
| `docs/08_estado_del_arte.md` | Competencia, precedentes y literatura científica |
| `docs/09_pipeline.md` | Qué hace cada script y cómo se encadenan |
| `DECISIONES.md` | Qué se decidió, cuándo y frente a qué alternativa |

## Licencias

- **Código:** MIT (`LICENSE`). El resto, en `NOTICE`.
- **Frases:** Diario de Sesiones del Congreso de los Diputados. Su reproducción se ampara
  en el art. 33 del TRLPI; los datos del Congreso se reutilizan al amparo de la Ley
  37/2007.
- **Retratos** (`web/fotos/`): fotografías oficiales del Congreso de los Diputados,
  reproducidas sin modificar según sus condiciones de reutilización. No están cubiertos
  por la licencia MIT.
- **Tipografía** IBM Plex: SIL Open Font License (`web/fonts/OFL-ibm-plex.txt`).

Autor: Alejandro Campos Lamas ([alejandrocamposlamas.com](https://alejandrocamposlamas.com)).
