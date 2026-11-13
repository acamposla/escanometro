# Escañómetro: guía de marca

Estado: **borrador v0 (2026-10-04)**. Capas 0 y 1 decididas con Alejandro; capa 2
aplicada en la web (variante A + C), con tokens provisionales pendientes de su visto bueno. Lo marcado
`provisional` lo propuso el asistente y nadie lo ha aprobado todavía.

Procedencia de la capa 0: `docs/01_objetivos.md`, `docs/03_metodologia.md` y
`docs/08_estado_del_arte.md`, confirmada por Alejandro el 2026-10-04.

## Capa 0. Estrategia

| | |
|---|---|
| **Para quién** | Público general curioso de política, en el móvil. En segundo plano, periodistas de datos y académicos, que leen la metodología. |
| **Contra qué compite** | Los quizzes de "¿quién lo dijo?" de partidos y medios, que eligen frases a mano para burlarse del rival. Y contra la sensación de "ya sé cómo habla cada partido". |
| **La promesa** | Crees que sabes quién dijo qué. Compruébalo con frases reales. |
| **El foso** | Frases literales con su fuente oficial enlazada, seleccionadas por un procedimiento publicado antes de tener resultados. |
| **Territorio prohibido** | Colores de partido asociados a un lado; burla a cualquier político o partido; interpretar resultados; tono de sermón o de lección. |

### Valores operativos (cada uno rechaza algo concreto)

| Valor | Rechaza |
|---|---|
| **Neutralidad por construcción** | Rojo a la izquierda y azul a la derecha, o cualquier par de colores que un votante asocie a un partido. Iconos de puño, gaviota, rosa o bandera. Que un bando "gane" visualmente (más grande, más brillante). |
| **Rigor que se puede comprobar** | Una frase sin enlace a su fuente. Una cifra en pantalla sin decir de cuántas partidas sale. Un percentil con menos de 20 partidas. |
| **Juego, no lección** | Textos largos antes de jugar. Explicar el sesgo antes de que el jugador lo sienta. Moralejas en la pantalla final. |

## Capa 1. Verbal

**Arquetipo: el laboratorio con un cómplice dentro** (decidido 2026-10-04). Preciso y
sobrio en lo que se afirma; con un guiño seco en cómo se dice. El guiño es al jugador,
nunca a costa de un político.

Descartados: el concurso de televisión (celebra y pincha, choca con el rigor) y el
cómplice irónico puro (sin el laboratorio, pierde autoridad ante un periodista).

| Rasgo | Es | No es |
|---|---|---|
| Preciso | Cifras exactas, fuente siempre a un toque | Frío ni técnico para iniciados |
| Seco | Una frase corta que deja el dato a la vista: "Has dicho 'seguro' 6 veces. Has fallado 3." | Sarcástico ni condescendiente con el jugador |
| Cómplice | Hablar de tú, reconocer que a todos nos pasa | Chistes sobre partidos o políticos |

**Léxico canónico:** frase, fuente, Diario de Sesiones, bloque (izquierda / derecha),
"creo que" / "seguro", acierto, fallo estando seguro, partida.

**Léxico prohibido:** "sesgo" dirigido al jugador ("eres sesgado"); "facha", "rojo",
"progre" o cualquier etiqueta de bando; "demuestra", "prueba que" sobre resultados;
"los partidos dicen lo mismo" (regla dura 8).

**Reglas de escritura:** frases de menos de 20 palabras en el juego; la cifra antes que
el adjetivo; sin exclamaciones salvo en el reverso de la tarjeta; sin guion largo; tú.

## Capa 2. Visual

**Territorio: instrumento de medida + archivo** (decidido 2026-10-04, variante A + C).
Regla de roles: **lo que se toca es instrumento** (IBM Plex Mono, latón, escala,
teclas que se hunden); **lo que se lee es documento** (IBM Plex Serif, papel, ficha del
Diario de Sesiones). El medidor usa el hemiciclo como escala: los escaños se encienden
en latón al paso de la aguja. Una aguja no tiene partido.

Tokens en `escanometro-design-tokens.json`. Contrastes calculados con la fórmula WCAG.

**Color:** papel y tinta; un solo acento, latón (`#86600F`, 4,9:1). Izquierda y derecha
comparten color y forma; solo cambia la posición. Acierto en verde petróleo y fallo en
siena: ninguno es rojo, azul, morado, verde lima ni magenta. Tema oscuro equivalente.

**Tipografía:** autoalojada (cargarla de Google enviaría la IP del visitante a Google;
regla dura 4).

**Movimiento:** aguja 420 ms con sobreoscilación amortiguada; giro de ficha 560 ms; sello
260 ms tras el giro. Aguja en reposo con una oscilación mínima (el instrumento está
vivo). Con `prefers-reduced-motion`, sin giro, sin oscilación y sin sobreoscilación.

**Compartir:** fila de símbolos sin spoiler (🎯 seguro acertado, 💥 seguro fallado,
✅ creo que acertado, ⬜ creo que fallado) copiada al portapapeles, sin SDK de redes.

### Sonido (decidido 2026-10-04)

Sonidos de instrumento, no de casino: clic al elegir, timbre al acertar, caída al fallar
un "seguro". Silenciable y discreto por defecto. La preferencia no se guarda (regla
dura 4): se pierde al recargar.

### Excepciones deliberadas al detector `impeccable` (2026-10-05)

De 37 antipatrones se corrigieron 31 (texto de menos de 11 px, barras laterales, borde
fino con sombra ancha, mayúsculas en textos largos, rebote en sellos, imagen sin `src`,
transición de ancho). Quedan 6 por decisión de marca, no por descuido:
- **Sobreoscilación de la aguja**: es la física de un instrumento real (`motion.aguja`).
- **Pautado de la ficha** (`repeating-linear-gradient`): papel de ficha de archivo.
- **`overflow-x: hidden` en `body`**: evita el scroll horizontal al arrastrar la ficha;
  el diálogo de aviso va en la capa superior y no se recorta.

### Estética empujada (2026-10-05, a petición de Alejandro: "menos plano")

Sin colores nuevos (un segundo tono acabaría pareciendo de algún partido). Se empujan
las dos metáforas: el medidor es la **esfera de un instrumento** (placa oscura, bisel de
latón, escala grabada con los umbrales de la apuesta, placa "Escañómetro · Mod. XV"), y
la ficha lleva **pestaña de archivador** con el tema y número de registro de la sesión.
Al acertar, los escaños del lado elegido se encienden en barrido de dentro afuera: la
celebración es el propio instrumento. Tokens nuevos: `--placa`, `--placa-escano`,
`--placa-rotulo`, `--laton-vivo` (provisionales).
