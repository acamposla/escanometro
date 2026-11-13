# Decisiones

Orden cronológico. Cada entrada dice qué se decidió y contra qué alternativa.

## 2026-09-29

### Idea original descartada: adivinar si una imagen es real o generada con IA

Verificado que está construida y publicada con la misma mecánica (swipe, sin
cuenta, XP, ranking, categorías) en App Store, Google Play, web de Sightengine,
itch.io y repos abiertos. Categoría con incumbentes y sin hueco.

Lo que se salva de ese análisis y se reutiliza aquí: el criterio de que el par
emparejado convierte un juego en instrumento de medida, y que el entregable real es
el dato agregado, no el juego.

### Giro a frases parlamentarias

Propuesta de Alejandro. Ventaja decisiva sobre la de imágenes: la verdad de terreno
es **documental y verificable** (quién dijo qué, con enlace al Diario de Sesiones) en
lugar de una etiqueta que hay que fabricar. Desaparecen de golpe el coste de
generación, el AI Act, el watermark y el sesgo de compresión.

Y el gesto coincide con el contenido: izquierda y derecha son el eje, no una
metáfora de interfaz.

### Objetivo: producto viral

Elegido por Alejandro sobre pieza de portfolio y ejercicio de despliegue. Se anotó
el coste de oportunidad (búsqueda activa, proceso avanzado, TFM abierto) y se
decidió seguir. Ver `docs/07_riesgos.md`, riesgo 3.

### Tema por dato, no por interés editorial

Se midieron 14 temas con volumen y balance. Entran **sanidad** (balance 0,99),
**vivienda** (0,85) y **pensiones** (0,95). En reserva trabajo (0,88) y defensa
(0,85).

- **Inmigración fuera.** Parecía el mejor con el filtro laxo (0,88) y con el filtro
  completo da 0,57. Sale por dato, además del riesgo.
- **Energía fuera.** Se recomendó con el filtro laxo (0,76) y con el completo da
  0,71. Corrección explícita de una recomendación previa.
- **Campo fuera** (0,54): pasó de 0,79 al excluir nacionalistas.
- **Memoria histórica fuera**: equilibrada (1,00) pero sin volumen (483) y es donde
  un error de atribución cuesta más caro.

### Solo los cuatro grupos estatales

PP y Vox contra PSOE y Sumar. Junts, PNV, ERC, Bildu y Mixto fuera **por diseño, no
por ideología**: su posición en el eje izquierda/derecha es discutible y una
respuesta correcta discutible destruye la credibilidad del instrumento. Efecto
lateral: elimina casi por completo el problema de las lenguas cooficiales.

### No se traduce

Contra la propuesta de traducir las frases en catalán. Una traducción deja de ser
cita, y traducir es elegir palabras, que en política son la marca ideológica: sería
reintroducir criterio propio en el único sitio donde se había quitado. Además, el
art. 33 TRLPI ampara reproducir, no transformar (art. 21). Coste de no traducir:
cero, porque quedan más de 4.000 frases limpias en castellano.

### Percentil en vez de ranking con alias

Hallazgo que decide el diseño: **un responsable de tratamiento no puede ser
anónimo** (art. 13 RGPD), así que recoger alias obligaría a firmar el proyecto. El
percentil es un agregado sin dato personal, no necesita política de privacidad, no
necesita moderación de alias y se comparte mejor.

### Nada se guarda en el dispositivo

El art. 22.2 LSSI cubre `localStorage` igual que una cookie, y que se borre al
cerrar la pestaña no exime (Directrices 2/2023 del CEPD, §37). El estado de la
partida vive en memoria. Coste: se pierde la racha al recargar. Beneficio: no hay
banner y la página de cookies dice la verdad.

### Anonimato máximo dentro de lo legal

Decisión de Alejandro. Sin firma, WHOIS protegido, repo privado, identidad de git
separada, y un buzón de contacto anónimo. Es reversible en un solo sentido: se puede
añadir el nombre después, no quitarlo.

El buzón no es un trámite: es la mitigación principal del riesgo de atribución
errónea, porque da una vía antes de que alguien busque otra.

### Repo privado y sin licencia

Contra publicarlo como MIT. Alejandro no quiere que se clone y se despliegue. Se
resuelve la tensión con la neutralidad separando las dos cosas: **se publica el
método** (corpus, palabras clave, filtros, prompt, criba), que es lo que permite
reproducir el resultado, y no el código, que nadie necesita para auditar
imparcialidad.

Aviso asociado: el catálogo no se puede proteger de todos modos, porque viaja al
navegador. Lo defendible es el método, la continuidad del corpus y la serie de
datos agregados.

### Stack: Cloudflare Pages + Supabase

Contra Next.js en Vercel. Criterio: menos partes móviles, porque quien mantiene
esto no revisa código. Se acepta que el catálogo sea legible desde el cliente.

### La métrica es el acierto condicionado a la confianza

Hallazgo de inspeccionar muestras: una frase vacía y una frase que engaña dan la
misma tasa de acierto (50%) y son lo contrario. Sin medir confianza, el catálogo se
llena de relleno y el juego frustra.

### El clasificador con modelo es obligatorio

Medido: el 45% del pool aleatorio es relleno (agradecimientos, trámite) y cerca del
40% son falsos positivos de tema ("hospital Al-Shifa" capturado por sanidad,
"okupas de alta magistratura" por vivienda). El filtro por palabra clave no basta.

### La web incluye una página con la literatura científica

Propuesta de Alejandro. Tres funciones a la vez: autoridad, contenido enlazable por
prensa, y defensa contra la acusación de partidismo, porque el sesgo que se mide
está documentado por terceros en otros países (Novoa et al. en PNAS, Swire et al.,
Zell et al., y el Perception Gap de More in Common).

## 2026-09-30

### Corrección de un dato de la documentación

El corpus ocupa **541 MB en disco**, no los 322 MB que decían el README, las notas internas
y el propio script. Los 322 MB eran solo la carpeta `data/`; el resto es el historial
de git del repositorio de origen.

## 2026-10-01

### BOE: posible módulo de la Fase 7, no de este proyecto

Idea de Alejandro: atribuir normas del BOE a gobiernos del PSOE o del PP. La verdad
de terreno también es documental (fecha y firma), pero mide otra hipótesis (si la
gestión delata la ideología, no el discurso) y la mayor parte del BOE es texto
técnico sin carga ideológica: necesitaría un filtro más difícil que el clasificador
de la Fase 2. Sin medir el volumen que sobreviviría. Queda anotado en la Fase 7.

### Se salta la prueba de señal (Fase 3)

Decisión de Alejandro: construir el producto directamente, sin la prueba de diez
frases. Coste asumido: la pregunta que podía tumbar el proyecto (si la gente acierta
por encima del 80%, el eje sí predice) se contesta con el juego ya construido, no
antes. Lo que no se salta: el clasificador de la Fase 2. El muestreo equilibrado
reparte las frases a partes iguales entre bloques, pero no impide que la mitad sean
relleno sin marca ideológica, y ese relleno empuja el acierto hacia el 50% por azar.

### Clasificador: `qwen3-32b` con el prompt `v2`, y la puerta de la Fase 2 se pasa con riesgo aceptado

Revisión humana a ciegas de 50 frases (semilla 1) contra tres modelos por LiteLLM.

**Con `v1` el acuerdo en postura fue de azar (42-50%)**, y los tres modelos fallaban
en el mismo sentido. Causa: el criterio. Alejandro marcaba 0 a frases genéricas
("cualquiera podría decirlo") y a datos ("solo es un dato"). Lo primero es la
pregunta del juego, no la del clasificador; lo segundo lo resolvió él mismo: elegir
qué dato se dice ya es tomar posición. `v2` añade la prueba del debate (¿podría
alguien usar la frase para defender o atacar algo?) y los dos casos. Repitió la
revisión de postura con 6 dudas marcadas. Su revisión `v1` se guarda en
`datos/revision/revision_ciega_postura_v1.csv`.

| Modelo (`v2`) | Tema | Postura | kappa postura | Relleno que deja pasar | Válidas que descarta |
|---|---|---|---|---|---|
| `qwen3-32b` | 90% | 86% | 0,41 | 7 de 10 | 0 de 40 |
| `gpt-oss-20b` | 86% | 82% | 0,24 | 8 de 10 | 1 de 40 |
| `or-deepseek-v3.2` | 84% | 80% | 0,32 | 6 de 10 | 4 de 40 |

Gana `qwen3-32b`: mejor en las dos preguntas, local, gratis y de pesos abiertos. El
modelo de pago no gana en nada. Las diferencias en relleno (2 o 3 frases sobre 10)
son ruido.

**La puerta no se cumple del todo**: el clasificador no detecta el relleno de forma
fiable. Decisión de Alejandro: seguir. Con el criterio aclarado el relleno es el 20%
de la muestra, no el 45%, y el que pase lo elimina el criterio 11 de la metodología
(una frase vacía no la coloca nadie con confianza). Riesgo aceptado: eso no se puede
comprobar hasta que haya jugadores. Límite declarado en `docs/03_metodologia.md`.

## 2026-10-04

### Diferencias entre bloques tras el clasificador: explicadas, no son sesgo constante

Pool completo con `qwen3-32b` y `v2`: sobreviven 3.650 de 4.281 combinaciones frase y
tema (85%). Dos diferencias entre bloques que no son azar (p < 0,01), en sentidos
opuestos:

- **Pensiones, la derecha pierde más (19% frente a 11%).** Toda la diferencia está en
  "no habla del tema" (36 frente a 13): la red de palabras clave pesca "cotización" en
  frases de fiscalidad ("impuestos y cotizaciones que lastran a las empresas"), y el
  modelo las saca con razón. Lectura de 6 al azar; sin contar las 36.
- **Sanidad, la izquierda pierde más (24% frente a 18%).** Toda en "sin postura" (110
  frente a 74). Patrón en una lectura de 10 al azar: el gobierno describe e informa, y al
  modelo le cuesta ver postura en el gobierno que defiende su gestión con datos ("la
  plantilla sanitaria ha crecido un 22%"). Límite declarado en la metodología.

### El papel institucional se mide, no se filtra

Observación de Alejandro: todo el corpus es de la XV legislatura, así que izquierda y
gobierno coinciden, y una frase que presume de gestión se acierta por el papel sin pasar
por el eje. La opción de fondo (sumar una legislatura con gobierno del PP) queda como
mejora: `escano-abierto` solo cubre desde 2023-08-17 y habría que parsear PDF antiguos.

Se probó filtrarlo con una tercera pregunta (`prompts/clasificador_v3.txt`, rol). Contra
la revisión de Alejandro: rol 72% (kappa 0,23), y la pregunta nueva empeora postura (80%
frente a 86%). En la decisión final coinciden en 30 de 50. No sirve como filtro. Decisión:
el catálogo se filtra con `v2`, y `v3` se usa solo para **etiquetar** el rol de cada frase
del catálogo; con jugadores se compara el acierto con rol y sin rol, y se publica la
diferencia. Pendiente un doble ciego con un segundo revisor para saber si la pregunta del rol es fiable entre
personas.

### El veredicto depende de las vecinas de lote

Mismo modelo y mismo prompt `v2` sobre las mismas 50 frases: postura 86% en lotes de la
revisión y 90% en los lotes del pool completo. Para el catálogo se reclasifica frase a
frase (lote 1), que es lo reproducible.

### Cloudflare D1 en vez de Supabase

Diagnóstico técnico: el plan gratuito de Supabase permite dos
proyectos activos por persona; y un proyecto gratuito se pausa tras una semana sin
actividad, con lo que el juego dejaría de guardar respuestas sin avisar. Decisión de
Alejandro: D1 (SQLite) en la misma cuenta de Cloudflare que Pages. Un proveedor en vez
de dos, sin pausa, sin claves en el navegador y sin la trampa del IPv6. Coste: se deja
Postgres; para dos tablas y un `GROUP BY` no cambia nada. Riesgo: proveedor único;
se mitiga exportando las respuestas a una máquina propia. Base creada: `sesgo-respuestas`,
región WEUR, con la sesión OAuth de `wrangler` que ya había (permiso `d1 (write)`):
ninguna credencial nueva.

### Confianza como apuesta, en un solo gesto, y tarjeta que se da la vuelta

Primera prueba de Alejandro en local: 13 de 20 (65%), y las 20 respuestas con
"Seguro". La pregunta de confianza en un paso aparte frenaba el juego y se respondía
por inercia. Decisión: cuatro opciones en un solo gesto ("seguro" o "creo que", a cada
lado; deslizar poco o hasta el borde) con puntuación de apuesta: "creo que" +1 / 0,
"seguro" +2 / -2. Marcar "seguro" sin estarlo cuesta puntos, así que la confianza
registrada es más honesta que con la pregunta suelta. El percentil se calcula sobre
puntos. La pantalla final dice cuántas veces se falló estando seguro. Propuesta de
Alejandro: la tarjeta gira al responder y el reverso muestra veredicto, autor, grupo,
fecha y enlace al Diario de Sesiones.

### Nombre: Escañómetro

`izquierda-o-derecha` descartado por Alejandro: quería un neologismo que dijera
política y elegir. Elegido "Escañómetro" (escaño + medir) frente a "¿Te mojas?",
"Barrer para casa" y "Polarímetro"; este último se descartó porque promete medir
polarización y el juego no la mide (`08_estado_del_arte.md`, punto 5.3). Proyecto de
Pages `escanometro` creado; `izquierda-o-derecha`, vacío, borrado.

### Sin total en directo, terminar cuando se quiera, y la proporción de "seguro"

Sin total acumulado durante la partida: con la apuesta, quien va perdiendo tendería a
marcar "seguro" para remontar, y la confianza registrada mediría estrategia y no
seguridad. El reverso de cada tarjeta sí enseña los puntos de esa frase. Botón
"Terminar y ver mi puntuación" en cualquier momento; las respuestas dadas quedan
guardadas. La pantalla final dice cuántas veces se dijo "seguro" y en cuántas se
falló (propuesta tras ver que Alejandro sentía acertar siempre con un 63% real y 14
fallos en 40 "seguro"). El percentil solo se da en partidas completas.

### Criterio 11 fijado antes de los datos: fuera la frase con 15 respuestas y 85% de acierto

Alejandro, jugando, encuentra frases demasiado evidentes y pide depurar. A mano no se
puede (regla dura 1): la depuración la hacen los datos. Regla fijada hoy, antes de
tener ninguna respuesta, publicada en la metodología y en la web: una frase sale cuando
acumula al menos 15 respuestas y el 85% o más son aciertos; se aplica por código sobre
todas, se publica la lista de retiradas y el umbral no se toca a la vista de los datos.
Las retiradas se sustituyen por reservas del mismo tema y bloque. Para que haya
reservas, el catálogo pasa de 96 a 150 frases (25 por tema y bloque). Siguiente paso:
un piloto cerrado con 5 a 10 personas lo más variadas posible; riesgo declarado: si el
piloto se parece a Alejandro, la criba quita lo obvio para ese grupo.

Mientras, los patrones que Alejandro señala y caben en código van a los filtros
(personas políticas, siglas regionales, términos catalanes). Descartado un filtro de
"referencias temporales al Gobierno" ("estos ocho terribles años"): atrapaba 74 frases,
muchas neutras, y más de un bloque que de otro.

## 2026-10-05

### Buzón de correo sustituido por un aviso anónimo en la web; página de datos sin nombre

Alejandro pregunta si hace falta política de privacidad y aviso legal con su nombre. No
(docs/05): sin datos personales no hay responsable que identificar, y sin actividad
económica no aplica el art. 10 LSSI. Se publica una página "Datos y condiciones" en
lenguaje llano (qué se guarda, qué no, de dónde salen frases y fotos, cómo avisar de un
error), sin identificar al autor. El buzón de correo se descarta:
recibir correos es tratar la dirección de quien escribe. En su lugar, un aviso anónimo
en el reverso de cada ficha (`/api/aviso`, tabla `avisos`): motivo y texto opcional, sin
correo, IP ni cabeceras. Pendiente de confirmación por un abogado si el proyecto crece.

### Retratos oficiales en el reverso

Propuesta de Alejandro. Aviso legal de congreso.es: reutilización permitida sin alterar
el contenido, citando fuente y fecha; no menciona las fotos expresamente. Se usan sin
modificar, alojados en la web, solo con coincidencia única orador-código (97 de 107).

### Cotejo con el PDF: doble método, sin revisión manual

Alejandro delega la revisión. Dos métodos independientes (texto plano y maquetación
real con `pdftotext -layout`): 211 de 222 confirmadas por ambos, 10 por uno sin que el
otro señale a otro orador, 1 sin confirmar (fuera, `datos/catalogo/no_cotejadas.csv`).
Ninguna frase atribuida a otra persona. Corrección registrada: dije que el Diario de
Sesiones va a dos columnas sin abrir la página; va a una. Las discrepancias del primer
método venían del orden de bloques del texto plano.

### Incidente: borrado de respuestas reales en producción (2026-10-05)

Al limpiar mis pruebas tras desplegar el reto diario ejecuté `DELETE FROM respuestas;
DELETE FROM avisos;` sobre la base real, en el mismo comando que mostraba 17 respuestas
que no eran mías (alguien ya estaba jugando con el enlace). Restauración con D1 Time
Travel: el primer punto disponible era anterior a la migración 0003, que hubo que volver a
aplicar (unos minutos en los que el endpoint de respuestas fallaba). Recuperadas 14 de
17; 3 perdidas sin remedio (el historial ya no conservaba el instante previo al borrado).

**Regla desde hoy:** en producción no se borra nunca una tabla entera. Las pruebas se
hacen con un `sesion_juego` conocido y se borran por ese identificador. Antes de
cualquier borrado, consulta separada, lectura del resultado y borrado filtrado.

### Marcador en directo, con los puntos previos guardados

Revierte la decisión del 2026-10-04 de ocultar el total durante la partida: Alejandro
quiere el marcador visible (tensión de juego). Para no perder la medida, cada respuesta
guarda `puntos_antes` (migración 0004): el análisis puede comprobar si quien va perdiendo
marca "seguro" más a menudo y separar ese efecto. Arreglado de paso: el barrido de
celebración podía terminar sobre la ficha siguiente.

### Compartir "tu sorpresa": una frase, elegida por el fallo del jugador

Segunda imagen para compartir con una sola frase: el fallo estando seguro más rápido o, si
no hay, el fallo más rápido. Tres condiciones: la elige el resultado del jugador y nunca
el proyecto (regla 1 aplicada a lo que se difunde); el texto habla del error de quien
juega ("Lo tenía claro: esto lo dijo la izquierda"), no del político, y sin marca de
género; la fuente (autor, grupo, fecha, referencia del DS) va siempre en la imagen. No se
ofrece en el reto del día para no desvelar respuestas. Riesgo aceptado: alguien la usará
para ridiculizar al partido que dijo la frase; la defensa es que es literal, verificable y
la eligió su propio fallo.

### El percentil va también en lo que se comparte

Cuando existe (20 partidas completas o más), el percentil sale en la imagen del resultado y
en el texto para compartir. Redacción cambiada a "partidas" en vez de "quienes han jugado":
una persona puede jugar varias rondas y no hay forma de saberlo. Las imágenes se dibujan al
llegar al resultado y "Compartir" las usa ya hechas, porque Safari en iOS rechaza el menú
nativo si entre el toque y la llamada hay demasiado trabajo. Las partidas libres se comparan
con todas las partidas completas del catálogo; el reto, solo con las de ese reto.

### Se abre a buscadores y se numeran las versiones (2026-10-05)

Fuera el `noindex` y el `Disallow: /`: `robots.txt` abierto (salvo `/api/`) con
`sitemap.xml`, `llms.txt`, `canonical` por página y datos estructurados `WebApplication`
sin autor (regla 6). Google solo indexa el texto fijo de las páginas; las frases se cargan
al jugar, así que abrirse ahora no expone el catálogo 1 antes de la versión 2. Versión
visible en el pie: el número mayor sube con cada edición del catálogo (2.0 = catálogo con
filtro de calidad) y el menor con cada cambio publicado de la aplicación. Hoy, 1.1.

Riesgo detectado para el lanzamiento: el plan gratuito de Workers/D1 corta a 100.000
llamadas a funciones al día (compartidas con otros proyectos de la cuenta), 100.000 filas
escritas y 5 millones de filas leídas, y el percentil recorre todas las respuestas en cada
consulta. Antes de la difusión: plan de pago (5 $/mes) y percentil sobre una tabla de
partidas en vez de sobre las respuestas.

### Percentil sobre un recuento por puntuación (2026-10-05)

Migración 0005: tablas `partidas` (una fila al llegar la décima respuesta) y `recuento`
(partidas por catálogo, grupo y puntuación; grupo `*`, `libre` o la fecha del reto). El
percentil lee como mucho 41 filas en vez de recorrer todas las respuestas, así que deja de
ser el primer tope del plan gratuito de D1. Verificado en local con 16 partidas simuladas y
una a medias: mismo resultado que el cálculo completo (percentiles 5, 9, 18 y 68 con 22
partidas) y la incompleta no cuenta. La migración rellena las partidas ya terminadas.

### Imagotipo, iconos y firma (2026-10-05)

`branding/logo/logo.html` dibuja el hemiciclo con interrogante con la misma geometría que
la web: avatar cuadrado oscuro de 1024 px (perfiles de redes; centrado para recorte
circular), iconos de 192, 512 y 180 px (`manifest.webmanifest` y `apple-touch-icon`: la
web se puede añadir a la pantalla de inicio como app, sin tiendas) y firma de correo
horizontal servida en `escanometro.com/firma.png` (`branding/logo/firma.html`).

### Versión 2.0: catálogo con juicio de calidad, 240 frases (2026-10-05)

Alejandro aceptó que un 43% de frases defectuosas era demasiado para difundir. Catálogo 2:
reglas nuevas en `filtros.py`, dos jueces de calidad (Sonnet 4.6 y DeepSeek V3.2 con
`prompts/calidad_v2.txt`; entra si aprueban los dos), confirmación una a una con
`qwen3-32b`, cotejo con el PDF por dos métodos con retirada si cualquiera sitúa la frase en
otro turno, y 240 frases (40 por tema y bloque, a petición de "cuantas más mejor").
Defectuosas entre las aprobadas: 10% en una muestra nueva de 60 leída a ciegas. Cifras y
desglose por bloque en `docs/03_metodologia.md` §3 ter y en la metodología publicada.
Coste en OpenRouter de toda la pasada: unos 5 $; la cuenta queda con unos 2,7 $. El
percentil empieza de cero con el catálogo nuevo (va por versión) y el reto del día cambia
de frases.

### Separar personas de robots en Umami (2026-10-05)

En las primeras 24 horas, 10 de 16 visitantes venían de Estados Unidos: rastreadores
(Google y Bing recién invitados) y escáneres con un Chrome normal que Umami no reconoce
como robots. Dos filtros sin guardar nada en el dispositivo: (1) el reenvío
`/api/u/send` descarta las visitas desde redes de centros de datos (`request.cf.asn`:
Google, Amazon, Microsoft, Hetzner, OVH y similares; no Cloudflare, Akamai ni Fastly, por
las que sale gente real con WARP o el Relay privado de iCloud); (2) evento `interaccion`
la primera vez que alguien toca, pulsa una tecla o hace scroll. Lectura: los visitantes
con `interaccion` y los eventos de partida son personas; las páginas vistas sueltas,
no necesariamente. Las respuestas del juego en D1 no se filtran por red: la criba ya
descarta tiempos de reacción por debajo de 400 ms.

## 2026-10-06

### España en lo que se comparte y nombre del sitio para Google

Petición de Alejandro: que quien no sea de España (Latinoamérica) entienda de qué
Congreso se habla. La descripción para buscadores ya decía "Congreso de los Diputados",
pero lo que se ve al compartir no nombraba el país. Cambios: `og:description` de las
cuatro páginas y rótulo de `og.png` ("Congreso de los Diputados · España", antes "Diario
de Sesiones · XV Legislatura"); meta description de la portada con el país al principio,
porque Google la corta según el ancho; dato estructurado `WebSite` en la portada (`name`
Escañómetro, `alternateName` Escanometro), que es lo que Google usa para el nombre del
sitio. No se toca `lang`: Google no lo usa para el idioma ni el país. Versión 2.2.

Contexto anotado el mismo día: elecciones generales convocadas el 2026-10-05 para el
29 de noviembre (campaña del 13 al 27, reflexión el 28). La LOREG (art. 69.7) prohíbe
publicar sondeos electorales los cinco días anteriores a la votación; sin verificar si
una cifra de acierto por bloque contaría como tal, no se publican cifras del 24 al 29.

### Jueces de calidad locales frente a los de pago (2026-10-06)

`qwen3.6-35b` y `gpt-oss-20b` en un servidor local, mismo prompt (`calidad_v2`) y mismas 3.227
candidatas, sin coste (5,2 h y 2,3 h; con `--max-tokens 0`, porque `qwen3.6-35b` razona
unos 5.600 tokens por lote y el tope de 3.000 lo cortaba). Contra la lectura de referencia
de las 150 frases del catálogo 1 (reglas + jueces; defectuosas entre las aprobadas):

| Jueces | Aprobadas | Defectuosas | Buenas perdidas | Kappa |
|---|---|---|---|---|
| Sonnet 4.6 + DeepSeek V3.2 (usada en la 2.0) | 61 | 10% | 31 de 86 | 0,52 |
| qwen3.6-35b + gpt-oss-20b (local) | 75 | 24% | 29 de 86 | 0,37 |
| qwen3.6-35b + Sonnet 4.6 | 57 | 5% | 32 de 86 | 0,55 |

En el pool completo la pareja local aprueba más (1.944 frente a 1.478) y está menos
equilibrada: 63% de las frases de izquierda frente a 58% de las de derecha (la de pago,
46% y 45%). `gpt-oss-20b` aprueba el 83% de todo y casi no filtra. Conclusión: el catálogo
2.0 se queda como está; la pareja local no sustituye a la de pago. Para próximas ediciones,
Sonnet + `qwen3.6-35b` (DeepSeek fuera: era el más lento y el local hace su papel gratis),
con la salvedad de que el 5% sale de una muestra pequeña y afinada sobre esas mismas frases.

### Origen, país y robots en cada respuesta; arreglos para Google (2026-10-06)

Versión 2.3. **Datos nuevos por respuesta** (migración 0006, sin datos personales): `origen`
(tipo de web de llegada, calculado por el navegador a partir de `document.referrer`, o
etiqueta de campaña), `pais` (`ES` u `otro`, de Cloudflare) y `red_nube` (1 si la conexión
sale de un centro de datos; los robots se marcan, no se descartan, y la exclusión se
decide en el análisis). Motivo: el canal decide quién juega y la cifra publicada tiene que
poder decir a quién describe. Clasificación probada con 13 casos (buscador, foro,
universidad, mensajería, red social, medio, interno, directo, otro, campaña y etiqueta
inválida).

**Enlaces de campaña:** `https://escanometro.com/?o=<etiqueta>`, con la etiqueta en minúsculas,
cifras y guiones (hasta 30): `?o=meneame`, `?o=reddit-spain`, `?o=uni-uc3m`. Uno distinto
por sitio y por persona a la que se envía. La etiqueta se quita de la barra al cargar
(quien reciba el enlace reenviado no hereda la campaña) y llega a Umami como
`utm_campaign`. En la base queda como `origen = 'c:<etiqueta>'`.

**Google:** `/favicon.ico` devolvía la portada en HTML y Google mostraba un globo genérico;
ahora hay `favicon.ico` (16, 32, 48) y `favicon-96.png` con una versión simplificada del
imagotipo (`branding/logo/logo.html?pieza=favicon`). Cualquier dirección inexistente
devolvía la portada con 200 (contenido duplicado para Google); ahora `404.html` da un 404
real. La descripción de la portada empieza por "Escañómetro". `escañómetro.com` (con ñ)
está libre, pero Cloudflare no registra dominios con ñ: si se compra, en otro registrador
y solo como redirección.

### Modo equipo: `?o=equipo` (2026-10-06)

Para separar las pruebas propias de los datos reales: entrar siempre por
`https://escanometro.com/?o=equipo`. Las respuestas quedan con `origen = 'c:equipo'` y se
excluyen del análisis. A diferencia de las demás etiquetas, `equipo` se queda en la barra
(sobrevive a recargas) y `web/medir.js` la añade a los enlaces internos (sobrevive a la
navegación); no se guarda nada en el dispositivo. Esa dirección no se comparte. Las
partidas del piloto anteriores a esta etiqueta (26 partidas del 5 y 6 de octubre, casi
todas de Alejandro por horario) se apartan con una fecha de corte que se fija antes de
difundir.

## 2026-10-23

### Esperar antes de diagnosticar el abandono (no lanzar aún la consulta a D1)

Revisión de la puerta de decisión del 14-oct: a esta
fecha, 41 partidas empezadas y 6 terminadas (~15%), muy por debajo de los umbrales fijados
el 2026-10-07 (150-200 partidas y >50% terminadas). Casi todo ese tráfico es anterior a
cualquier publicación en foros (Menéame sigue bloqueada por el requisito de 8 meneos).

Alternativa descartada: lanzar ya el diagnóstico (histograma en D1 de en qué pregunta
abandona cada partida no terminada, cruzado por `origen` y dispositivo) para probar la
hipótesis de que el juego es "poco adictivo". Se descarta porque con n=41 no hay potencia
para separar esa hipótesis de ruido de muestra, fricción de entrada o composición del
canal: el repunte del 21-oct (22 páginas vistas) viene de un amigo que compartió el
enlace en un chat, no de alguien que buscó el juego, y no es comparable al tráfico que
traerá un foro.

Decisión: esperar a tener más volumen de tráfico real (tras publicar en foros) antes de
diagnosticar. Es una decisión de secuencia, no de abandono del proyecto ni de la puerta
del 14-oct en sí.

## 2026-11-13

### El autor pasa a ser público

Alejandro decide que el Escañómetro deja de ser anónimo: va como pieza en su portfolio
(alejandrocamposlamas.com) y lo anuncia en LinkedIn con su nombre ("vamos a hacerlo
public. No pasa nada"). Alternativa que se abandona: el anonimato del autor (regla 6),
mantenido desde el inicio.

Consecuencias:
- Queda superado el canal del 2026-10-01 en lo que tenía de anonimato ("sin las redes de
  Alejandro") y la firma "Equipo del Escañómetro" ante periodistas.
- La aceptación del riesgo del art. 14 RGPD (2026-10-05) se hizo con el autor oculto. Con
  autor público el contacto puede firmarse con nombre, lo que reduce ese riesgo.
- **Sin aviso legal con identificación del responsable** en la web (decisión de
  Alejandro). No se ha verificado si la LSSI (art. 10) lo exige sin actividad económica.
- La identidad de git separada de este repositorio se conserva: no estorba.

### Ventana de publicación (campaña del 29-N)

Para el post y la pieza: nada de cifras del juego del 24 al 29 de noviembre (LOREG art.
69.7; que una cifra de acierto cuente como sondeo sigue sin verificar). Por prudencia,
nada el 28 (jornada de reflexión) ni el 29. Contar el proyecto y el método sin cifras no
es un sondeo.

### El código se publica: copia limpia con licencia MIT

Revierte "Repo privado y sin licencia" (2026-09-29). Con el autor público, Alejandro decide
abrir el código, con licencia MIT (la misma del corpus de partida). Así la regla 1
(ninguna frase se elige a mano) deja de ser una promesa y se puede comprobar en los
filtros y sus tests. Se publica una copia sin el historial de trabajo y sin las notas
internas de operación (cuentas, máquinas, difusión); la configuración de despliegue y de
medición lleva valores de ejemplo.
