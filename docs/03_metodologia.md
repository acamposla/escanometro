# Metodología

**Este documento se publica en la web antes de tener resultados.** Es la única
defensa real contra la acusación de partidismo: el procedimiento se declara
primero y cualquiera puede repetirlo.

## 1. Corpus

Diario de Sesiones del Congreso de los Diputados, XV Legislatura, del 2023-08-17
al 2026-09-23. Se obtiene con `scripts/obtener_corpus.sh`.

## 2. Grupos incluidos, y por qué solo cuatro

Solo **PP y Vox** (bloque de la derecha) y **PSOE y Sumar** (bloque de la
izquierda).

Junts, PNV, ERC, Bildu y el Grupo Mixto quedan fuera por una razón de diseño, no
ideológica: en el eje izquierda/derecha su posición es discutible (Junts es derecha
económica e independentista; el PNV es centro-derecha nacionalista), y **una
respuesta correcta discutible destruye la credibilidad del juego**. Si el jugador
puede argumentar que la respuesta oficial está mal, el instrumento deja de medir.

Efecto lateral: excluirlos elimina casi por completo el problema de las lenguas
cooficiales, porque los cuatro grupos estatales intervienen en castellano.

## 3. Selección: nadie elige frases

En orden, y cada paso es automático:

1. **Segmentación.** La intervención se parte en frases. El corpus trae discursos
   enteros (máximo medido: 85.037 caracteres), así que la unidad es la frase.
2. **Saneamiento.** Se eliminan las acotaciones del taquígrafo entre paréntesis. Se
   descartan las frases con palabras pegadas por el parseo del PDF, en vez de
   reconstruirlas: una frase reconstruida ya no es la que se dijo.
3. **Filtro de longitud.** Entre 80 y 180 caracteres. Por debajo no hay afirmación;
   por encima no se lee en un gesto.
4. **Filtro de tema.** Expresión regular por tema. La lista de palabras de cada
   tema se publica: es un punto de sesgo y se declara como tal.
5. **Exclusión por autodelación.** Fuera toda frase que revele el emisor sin
   razonamiento: nombres y siglas de grupo, referencias a la propia bancada,
   apelaciones al rival, aparato de la sesión.
6. **Exclusión por cita de terceros.** Fuera todo lo que vaya entre comillas o
   venga precedido de verbo de cita. **Este filtro es el más importante del
   proyecto**: el corpus atribuye la frase a quien la pronuncia, así que sin él un
   diputado citando a su rival produciría una atribución falsa con datos
   correctos.
7. **Exclusión por lengua.** Solo castellano. El idioma delataría el grupo sin
   leer el contenido. No se traduce (ver `05_legal_y_anonimato.md`).
8. **Exclusión por falta de fecha.** Sin fecha no hay fuente citable.
9. **Clasificación con modelo.** Dos preguntas, con el prompt publicado: ¿la frase
   trata realmente del tema? ¿es una afirmación ideológicamente asignable, o es
   trámite y relleno? Medido: sin este paso, el 45% del pool es relleno y hay
   falsos positivos de tema en torno al 40%.
   Modelo: `qwen3-32b` (pesos abiertos, ejecutado en local), prompt
   `clasificador_v2`, elegido contra una revisión humana a ciegas de 50 frases.
   **Límite declarado:** coincide con la revisión humana en el 90% de los casos
   sobre el tema y en el 86% sobre la postura (kappa 0,41), y no descartó ninguna
   frase válida, pero solo detecta 3 de cada 10 frases de relleno. El relleno que
   pase lo elimina el punto 11, no este. En sanidad detecta peor la postura cuando el
   Gobierno defiende su gestión con datos, y descarta más frases del bloque que
   gobierna.
   **Papel institucional.** Todas las frases son de la XV Legislatura, en la que gobierna
   la izquierda: una frase que delata a quien gobierna o a quien está en la oposición se
   puede acertar sin pasar por el eje. No se filtra (ni una persona ni el modelo lo
   distinguen de forma fiable); cada frase del catálogo lleva una etiqueta de rol y el
   resultado se publica separado para las frases con rol y sin él.
10. **Muestreo aleatorio con semilla fija**, equilibrado mitad y mitad entre
    bloques aunque el corpus no lo esté.
11. **Criba por dificultad medida.** Entra la frase donde la gente falla **estando
    segura**. No entra por gusto de nadie. **Regla fijada el 2026-10-04, antes de
    tener respuestas:** una frase sale del catálogo cuando acumula al menos 15
    respuestas y el 85% o más son aciertos. Se aplica por código
    (`scripts/criba.py`) sobre todas las frases a la vez, se publica la lista de
    frases retiradas con sus cifras y el umbral no se cambia a la vista de los
    datos. Las frases retiradas se sustituyen por reservas del mismo tema y bloque,
    en el orden del sorteo.

Ninguna frase se descarta por su contenido político ni por incomodar. Si una
exclusión no cabe en un filtro del código, no se aplica.

## 3 bis. Estado del catálogo v1 (2026-10-05)

- Pool tras filtros: 3.878 frases distintas (3.936 combinaciones frase-tema); 3.362 superan
  el clasificador (`qwen3-32b`, prompt v2).
- Filtros ampliados con regla y test: Ministerio, nombres de líderes nacionales y
  autonómicos, siglas de otros grupos, términos institucionales catalanes, gallego y
  valenciano, palabras pegadas por el parseo y anáfora inicial ("Eso es...", "Fueron esas
  políticas..."). Los sujetos implícitos que remiten a un tercero ("No son un grupo más...")
  no caben en una regla de texto: quedan para el aviso "fuera de contexto" y la criba.
- Catálogo: 150 frases, 25 por tema y bloque, en el orden de un sorteo estable por frase
  (semilla 1). Confirmadas una a una con el mismo modelo, en local y vía OpenRouter (95%
  de coincidencia en las 43 hechas por ambas vías).
- Cotejo con el PDF: dos métodos (texto plano y maquetación). 211 de 222 candidatas
  confirmadas por ambos, 10 por uno sin contradicción, 1 retirada. Ninguna atribuida a
  otra persona.

## 3 ter. Catálogo v2 (2026-10-05): juicio de calidad

- Lectura a ciegas del catálogo v1 (Claude Opus, sin partido ni orador): 43% de frases
  defectuosas (40 dependían del contexto o eran trozos, 20 relleno o dato sin postura,
  2 texto roto, 2 delataban o citaban a otros). Defectos repartidos igual entre bloques
  (33 izquierda, 31 derecha).
- Reglas nuevas en `filtros.py`, con test y frases de control: continuación de lo
  anterior, texto roto (punto pegado, puntos suspensivos finales), citas oídas ("dicen
  que") y "nosotras". Pool: 3.724 frases distintas (3.779 combinaciones); 3.227 superan
  el clasificador.
- Juicio de calidad (`prompts/calidad_v2.txt`): Claude Sonnet 4.6 y DeepSeek V3.2 vía
  OpenRouter responden si la frase se entiende sola, si afirma algo y si delata al
  orador; entra si los dos la aprueban. Aprueban 1.478 de 3.227 (46%; izquierda 46%,
  derecha 45%; pensiones 53/42, sanidad 36/42, vivienda 49/48, izquierda/derecha).
- Medida: defectuosas entre las aprobadas, 10% sobre las 150 del v1 (con las que se afinó
  el prompt) y 10% (6 de 60) en una muestra nueva del catálogo v2 leída a ciegas después
  (intervalo aproximado 5-20%).
- Catálogo: 240 frases, 40 por tema y bloque (semilla 1); 56 repetidas del v1. Confirmadas
  una a una con `qwen3-32b` (las nuevas, vía OpenRouter).
- Cotejo: de 330 candidatas, 307 confirmadas por los dos métodos, 3 por uno, 9 por
  ninguno y 11 situadas por un método en el turno de otra persona (retiradas aunque el
  otro las confirmara). En el catálogo: 238 por ambos, 2 por uno.
- Presentación: las cifras de cinco o más dígitos se agrupan con espacio fijo
  ("346 000"), como en el Diario de Sesiones; el cotejo se hace antes, sobre el texto del
  corpus.

## 4. La métrica

No es la tasa de acierto. Es **el acierto condicionado a la confianza**.

Razón: una frase que nadie sabe colocar y una frase que todos colocan mal dan la
misma tasa (50%) y son lo contrario. La primera es relleno; la segunda es el
hallazgo. Sin medir confianza, el catálogo se llena de frases vacías y el juego
frustra.

Se registra por respuesta: frase, dirección del swipe, acierto, confianza y tiempo
de reacción. Nada que identifique al jugador.

Cada ronda es una partida con su propio identificador aleatorio. Una misma persona
puede jugar varias rondas, y no hay forma de saberlo (ni se quiere): los resultados
se publican por respuesta y por partida, declarando que las partidas no son
personas.

## 5. Publicación de resultados: describir, no interpretar

La neutralidad se pierde en la última frase, no en la recogida de datos.

- **Dato**: "en sanidad, el 43% de las frases se atribuye al bloque equivocado, y
  el 61% de esos errores se comete con confianza alta".
- **Conclusión política, prohibida**: "la izquierda y la derecha dicen lo mismo".

Se publican los resultados completos, incluidos los que no favorecen ninguna
lectura, y el desglose por tema y por grupo. Los resultados se enmarcan en la
literatura existente (ver `08_estado_del_arte.md`), que documenta el mismo sesgo
en otros países: eso desactiva la lectura de que el sesgo lo inventó quien hizo el
juego.

## 6. Integridad de los datos

Sin cuentas, cualquiera puede enviar respuestas automatizadas. No se defiende con
arquitectura sino en el análisis, que es más barato y más honesto:

- Se descartan las sesiones con tiempos de reacción imposibles (por debajo de unos
  400 ms es reflejo, no juicio).
- Se descartan las sesiones con acierto perfecto en tiradas largas.
- Se publica cuántas sesiones se descartaron y por qué.

## 7. Corrección de errores

Cada frase lleva su fuente enlazada. Hay un buzón de contacto y **una frase
señalada como mal atribuida se corrige o se retira**, sin discutir. El registro de
correcciones se publica.
