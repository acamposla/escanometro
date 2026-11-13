# Riesgos fatales

Los cinco primeros se identificaron antes de empezar. Los tres últimos salieron de
medir el corpus el 2026-09-29.

## 1. El catálogo es consumible y la retención es cero por construcción

Es el fallo estructural del género. Un jugador agota 100 frases en una sesión y no
vuelve. Los incumbentes lo tapan con producción continua de contenido, que aquí no
se puede sostener.

**Asumido, no mitigado.** Esto es una campaña con fecha de caducidad: catálogo
finito, ventana de difusión de dos o tres semanas, análisis publicado al final, y
el juego se queda online como archivo. La alternativa sería una obligación de
generar contenido todas las semanas, gratis, para desconocidos.

Ventaja del tema elegido frente a la idea original de imágenes: el corpus **crece
solo** con cada sesión del Congreso, así que reponer catálogo cuesta ejecutar un
script, no generar imágenes de pago.

## 2. El instrumento mide otra cosa de la que dice medir, y el fallo es silencioso

El juego funciona, la gente juega, los números salen, y el titular publicado es
falso. Cuatro vías detectadas:

- **Pista de idioma**: una frase en catalán delata el grupo. Mitigado (solo
  castellano, y solo los cuatro grupos estatales).
- **Autodelación**: la frase nombra al rival o a la propia bancada. Mitigado con
  filtro y probado con test.
- **Desequilibrio de tema**: si un bloque domina el tema, se gana deslizando
  siempre al mismo lado. Mitigado con el umbral de balance y con muestreo a partes
  iguales.
- **Relleno confundido con dificultad**: una frase vacía da el mismo 50% que una
  frase que engaña. Mitigado midiendo confianza, no solo acierto.

Publicar un análisis falso con firma propia es el daño mayor: no cae la pieza, cae
la credibilidad de quien la firma.

## 3. Coste de oportunidad sobre la búsqueda de empleo

Hay una búsqueda activa en curso, un proceso avanzado y un TFM sin cerrar. Este
proyecto no es ninguna de las cinco piezas del portfolio.

**Decisión de Alejandro**: adelante, con objetivo viral. El riesgo queda anotado
para que no se descubra dentro de tres semanas como si fuera una sorpresa.

## 4. Atribución errónea: el riesgo reputacional y legal

Una frase mal atribuida a un político real es un bulo con el nombre de quien lo
publica encima. Y el corpus atribuye la frase a quien la pronuncia, así que un
diputado citando a su rival la produciría sin que nadie lo notase.

Mitigaciones, las tres necesarias:

1. Filtro de citas de terceros (comillas y verbos de cita), con test.
2. Fuente enlazada en cada frase, con sesión y fecha.
3. Buzón de correcciones visible, y retirada sin discusión de lo que se señale.

## 5. El proyecto acaba siendo munición de guerra cultural

Va a ocurrir en alguna medida: los dos bloques lo usarán como prueba de lo que ya
creían. No se evita, se acota:

- Temas templados en el catálogo inicial. Inmigración, memoria histórica y aborto
  quedan fuera (y además no pasan el umbral de balance).
- Metodología publicada **antes** de tener resultados.
- Resultados descritos, no interpretados (`03_metodologia.md`, punto 5).
- Literatura académica citada en la propia web: el sesgo está documentado por
  terceros en otros países, así que no lo inventó quien hizo el juego.

## 6. Nuevo: la ventana temporal del corpus es corta

Solo la XV Legislatura, tres años. Se pierde el contraste más potente, que es lo
que un partido decía en la oposición frente a lo que dice gobernando. Ampliar exige
parsear PDF de legislaturas anteriores y comprobar que el formato aguanta.

Consecuencia si no se amplía: el juego mide el eje en un momento concreto, no su
evolución. Es menos interesante de lo que podría ser, y hay que decirlo al publicar
en vez de esperar a que alguien lo señale.

## 7. Nuevo: el catálogo no se puede proteger

Las frases y sus respuestas viajan al navegador. Un tercero las descarga del JSON
o, si se sirvieran desde un endpoint, jugando cien veces. El repositorio privado
protege el código, no el contenido.

Lo defendible no es el catálogo: es el método, la continuidad (el corpus crece con
cada sesión) y la serie de datos agregados, que solo tiene quien recibe el tráfico.
Un clon empieza con cero respuestas y sin serie histórica.

## 8. Nuevo: el filtro por palabra clave trae ruido de tema

Medido: en torno al 40% de falsos positivos en una muestra ("hospital Al-Shifa"
capturado por sanidad, "okupas de alta magistratura" por vivienda). Sin el paso de
clasificación con modelo, el catálogo mezcla temas y el juego pierde sentido.

Riesgo derivado: ese paso introduce un modelo en la ruta de selección, y un modelo
es opaco. Mitigación: se publica el prompt, se guarda la decisión del modelo por
frase, y la clasificación se revisa a mano sobre una muestra antes de aceptar el
catálogo.
