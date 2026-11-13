# Investigación: corpus, viabilidad y hallazgos

Todo lo de este documento se midió el 2026-09-29 sobre el corpus real. Las cifras
son reproducibles con `scripts/medir_temas.py`.

## El corpus

**Fuente elegida: `escano-abierto`** (MIT, `jorgegarcelan/escano-abierto`), que
procesa los PDF oficiales del Diario de Sesiones y extrae las intervenciones una a
una. Los datos de origen son del Congreso y se reutilizan al amparo de la Ley
37/2007.

Campos por intervención: `orden`, `orador`, `cargo`, `grupo`, `item`, `exp`,
`seccion`, `texto`, `reacciones`. Por sesión: `id`, `serie`, `numero`, `fecha`,
`sesion`, `organo` y `ds` con la URL del PDF oficial. Esos dos últimos son lo que
permite el reveal con fuente citable.

| Medida | Valor |
|---|---|
| Sesiones | 822 (7 sin fecha, descartadas) |
| Rango | 2023-08-17 a 2026-09-23 |
| Intervenciones | 76.306 |
| De la Presidencia (ruido) | 43.458, el 57% |
| Longitud del texto: mediana | 240 caracteres |
| Longitud del texto: máximo | 85.037 caracteres |

Dos consecuencias de esas dos últimas filas: el 57% del corpus es la Presidencia
dando y quitando turnos, y hay intervenciones que son discursos enteros sin
segmentar, así que **hay que trabajar con frases dentro de la intervención**, no
con la intervención.

**Descartada la alternativa `jalonsomerchan/congreso-opendata`** pese a estar más
activa (1.435 commits, actualización cada 30 minutos): sus intervenciones no
garantizan el texto completo porque descubre enlaces del buscador, y no declara
licencia. Sin texto literal no hay juego.

**Portal oficial** (`congreso.es/es/datos-abiertos`): cinco conjuntos en XML, JSON
y CSV (Votaciones, Diputados, Iniciativas, Intervenciones, Órganos). No aclara si
"Intervenciones" incluye el texto de los discursos. **Incógnita abierta**: si lo
incluyera, sería mejor fuente que parsear PDF.

## Limitaciones del corpus

1. **Solo la XV Legislatura.** Tres años. Se pierde el contraste más jugoso, que es
   lo que un partido decía en la oposición frente a lo que dice gobernando. Se
   puede ampliar descargando PDF de legislaturas anteriores, a costa de comprobar
   que el parseo aguanta formatos antiguos.
2. **No hay campo oficial de materia.** El tema se filtra por palabras clave
   definidas por nosotros, y esa lista es un punto de sesgo que se publica.

## Viabilidad por tema

Medido con el filtro completo y solo los cuatro grupos estatales. El **balance**
es (frases del bloque menor / frases del bloque mayor): no es cosmético, porque un
tema desequilibrado se gana deslizando siempre al mismo lado sin leer. Umbral:
balance ≥ 0,75 y al menos 500 frases.

| Tema | Derecha | Izquierda | Total | Balance | Veredicto |
|---|---:|---:|---:|---:|---|
| memoria histórica | 242 | 241 | 483 | 1,00 | fuera (volumen y riesgo) |
| **sanidad** | 628 | 632 | 1.260 | **0,99** | **entra** |
| **pensiones** | 294 | 308 | 602 | **0,95** | **entra** |
| agua y trasvases | 34 | 31 | 65 | 0,91 | fuera (volumen) |
| trabajo y salarios | 325 | 370 | 695 | 0,88 | reserva |
| **vivienda** | 1.299 | 1.110 | 2.409 | **0,85** | **entra** |
| defensa y OTAN | 590 | 500 | 1.090 | 0,85 | reserva |
| energía y nuclear | 687 | 490 | 1.177 | 0,71 | fuera |
| educación | 378 | 531 | 909 | 0,71 | fuera |
| turismo | 132 | 189 | 321 | 0,70 | fuera |
| género y aborto | 180 | 267 | 447 | 0,67 | fuera |
| inmigración | 882 | 502 | 1.384 | 0,57 | fuera |
| campo | 475 | 257 | 732 | 0,54 | fuera |

**Catálogo inicial: sanidad, vivienda y pensiones.** Trabajo y defensa en reserva.

Notas sobre exclusiones que no son obvias:

- **Inmigración** parecía el mejor tema en una medición previa con filtro laxo
  (0,88) y con el filtro completo cae a 0,57: la derecha habla del tema 1,76 veces
  más. Sale por dato, no solo por riesgo reputacional.
- **Energía** se recomendó por error con el filtro laxo (0,76) y con el completo da
  0,71. Queda fuera.
- **Memoria histórica** sale equilibrada (1,00) al mirar solo los cuatro grupos
  estatales, pero no llega a 500 frases y es donde un error de atribución cuesta
  más caro. Fuera por las dos razones.
- **Campo** pasó de 0,79 a 0,54 al excluir a los nacionalistas, que es coherente:
  buena parte del debate agrario lo llevan ERC, Junts y PNV por sus territorios.

## El material existe: frases que engañan

Las dos mejores encontradas en muestreo aleatorio, sin selección editorial. Las
dos son del PP y cualquiera las colocaría a la izquierda:

> "En España tenemos únicamente el 2,5% de vivienda pública frente al 9,3 de media
> en la Unión Europea, 7 puntos por debajo."
> **PP**, Mesquida Mayans, 2024-06-18, DSCD-15-CO-127

> "El acceso a la vivienda se ha convertido en un drama y el informe lo dice sin
> tapujos: no hay política estructural de vivienda."
> **PP**, Pascual Rocamora, 2025-06-17, DSCD-15-CO-366

Y de Vox, en el mismo registro que se atribuiría a la izquierda:

> "Esto es un escándalo y un insulto a los españoles que no llegan a fin de mes ni
> pueden adquirir una vivienda."
> **VOX**, Chamorro Delmo, 2026-04-28, DSCD-15-CO-550

## Defectos del corpus detectados y resueltos

Los tres salieron de inspeccionar muestras aleatorias, no de suponer. Están
cubiertos en `scripts/filtros.py` y con un test cada uno.

1. **Acotaciones del taquígrafo** dentro del texto: *"aquí lo tiene (muestra otro
   documento), por separado"*. Se eliminan.
2. **Palabras pegadas** por el parseo del PDF: *"fondos comoAlquiler Seguro"*. La
   frase se descarta en vez de adivinar dónde iba el espacio: una frase
   reconstruida ya no es la que se dijo.
3. **Siete sesiones sin fecha.** Se descartan: sin fecha no hay fuente citable.

## Dos hallazgos que obligan a un paso de clasificación con modelo

El filtro por expresión regular no basta, y las dos razones se midieron:

**a) El 45% del pool aleatorio es relleno.** En una muestra de 20, nueve eran
agradecimientos al personal sanitario, preguntas de trámite o frases sin contenido
asignable. No engañan: simplemente no dicen nada.

**b) Hay falsos positivos de tema.** En una muestra de 10, cuatro: *"el hospital
Al-Shifa, donde se encontraron túneles"* (Gaza, capturado por "hospital"), *"el
dopaje deja de concebirse como infracción deportiva"* (capturado por "sanitario"),
*"okupas de alta magistratura"* (poder judicial, capturado por "okupa").

Por tanto el paso de clasificación tiene **dos funciones**: confirmar que la frase
trata realmente del tema, y evaluar si es ideológicamente asignable. Sin él, el
catálogo mezcla relleno y ruido, y el juego aburre.

## Tamaño disponible

Tras el filtro completo, con los tres temas del catálogo, el pool supera las 4.000
frases limpias repartidas entre los dos bloques. El catálogo objetivo es de 60 a
100. Sobra material por un factor de cuarenta, así que todas las exclusiones
conservadoras de este documento salen gratis.

## Estabilidad de la medición (2026-09-30)

El corpus crece: al día siguiente de la primera medición traía **824 sesiones y
76.421 intervenciones**, frente a 822 y 76.306. El rango de fechas no se movió
(seguía terminando el 2026-09-23), así que lo añadido son comisiones publicadas con
retraso, no sesiones nuevas.

Los balances no se movieron: sanidad 0,99, pensiones 0,95, trabajo 0,87 frente a
0,88. **La elección de temas es estable ante una actualización del corpus**, medida
en dos máquinas distintas (Python 3.14 y 3.9.6).

Consecuencia práctica: las cifras de este documento son de una fecha, no constantes.
Cualquier cifra que se publique lleva la fecha de la ejecución que la produjo, y se
regenera con `scripts/medir_temas.py` antes de publicarla.
