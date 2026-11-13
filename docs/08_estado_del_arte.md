# Estado del arte

Verificado el 2026-09-29. Tres capas: los productos que ya existen, el precedente
de instrumento público que se viralizó, y el fundamento académico del fenómeno.

## 1. Productos existentes

### El formato original descartado (imagen real o generada con IA)

Está construido y publicado, con la mecánica idéntica a la que se había pensado
(swipe, sin cuenta, XP, ranking, categorías):

- AI or Not Game, App Store, actualizado en julio de 2026
- AI or Not, Google Play
- AI or Not, versión web de Sightengine
- AI or Real: Guess the Truth, App Store
- Clones abiertos: `followyes/ai-or-human` en GitHub, `adminbat` en itch.io

Conclusión: categoría con incumbentes y sin hueco. Se abandonó como producto.

### El formato "¿quién lo dijo?" político en España

También existe, pero en una forma distinta y más débil:

- **Juego de Sumar** (agosto de 2026): frases de Feijóo, Abascal y Ayuso con tres
  autores posibles. Es una pieza de partido para burlarse del rival.
- **Frases de políticos españoles**, app en Google Play.
- **Tests de medios**: asivaespana, okdiario y similares.
- **Precedente argentino** (2019): "¿Quién lo dijo?" en minutouno, para elecciones.

Todos comparten tres límites: las frases se eligen a mano con criterio editorial,
el objetivo es el quiz de memoria ("¿te acuerdas de quién dijo esta barbaridad?")
y no hay corpus, procedimiento ni fuente citable. Ninguno mide nada.

## 2. El precedente que sí es comparable

**The Perception Gap** (More in Common, informe de Yudkin, Hawkins y Dixon, junio
de 2019, `perceptiongap.us`) es un test público sobre percepción de polarización
que se difundió ampliamente y generó cobertura. Su hallazgo central: demócratas y
republicanos creen que cerca del doble de sus oponentes sostiene posiciones
extremas de los que realmente las sostienen (perciben un 55% frente a un ~30%
real), y la distorsión es mayor en los más activos políticamente.

Es el modelo a seguir en forma (test público, dato agregado, cobertura de prensa)
y la diferencia está en el instrumento: **ellos preguntan por percepciones
declaradas; aquí se presenta evidencia documental**. Una frase real con enlace al
Diario de Sesiones es mucho más difícil de discutir que una estimación de
opinión, y por eso el resultado es más resistente al "esto lo dice quien lo
pregunta".

## 3. Fundamento académico

El mecanismo que el juego explota y mide está descrito y publicado:

- **[Generically partisan: Polarization in political communication](https://consensus.app/papers/details/13df1a7936fe5c08978df931097b182a/?utm_source=claude_code)**
  (Novoa et al., 2023, PNAS) es el más pertinente. Sostiene que la polarización
  percibida excede con mucho la real y que una causa es la tendencia a formar
  generalizaciones de grupo a partir de evidencia inconsistente. En su estudio 1
  (n = 417) los participantes respaldaban afirmaciones genéricas del tipo "los
  demócratas favorecen X" siempre que fueran más ciertas del partido objetivo que
  del contrario, **incluso creyendo que eran verdad para bastante menos de la
  mitad de ese partido**. En el estudio 2 (n = 928), la gente recordaba las
  declaraciones de las élites políticas como genéricas aunque no lo fueran.
- **[Processing political misinformation: comprehending the Trump phenomenon](https://consensus.app/papers/details/4428b76d35c55903ace48218a51d6ffd/?utm_source=claude_code)**
  (Swire et al., 2017, Royal Society Open Science, 369 citas) muestra que la
  atribución a una figura política altera por sí sola la credibilidad asignada a
  la misma frase. Justifica el diseño: la frase se presenta sin etiqueta y el
  autor se revela después.
- **[It's their fault: Partisan attribution bias and its association with voting intentions](https://consensus.app/papers/details/a96d620fc7d058d588d5a32e93fd632a/?utm_source=claude_code)**
  (Zell et al., 2021, Group Processes & Intergroup Relations) documenta el sesgo
  de atribución partidista y que se agrava con la intensidad ideológica.

## 4. El hueco

Los juegos usan frases elegidas a mano y no miden. Los estudios miden pero usan
**frases genéricas construidas por los investigadores** ("los demócratas favorecen
la discriminación positiva"), no citas textuales verificables.

Nadie ha hecho lo que este proyecto hace: **atribución de citas verbatim de un
corpus parlamentario oficial, con fuente enlazada por frase, selección
reproducible y medición de acierto condicionado a la confianza, en España**.

Eso es el hueco, y es defendible por una razón concreta: no depende de ser el
primero en tener la idea, sino de haber construido el corpus y el procedimiento.
Copiar el concepto cuesta una tarde; copiar el instrumento exige repetir el
método, y si alguien lo repite, confirma el resultado en vez de competir con él.

## 5. Lo que este estado del arte obliga a hacer

1. **No presentarlo como novedad de formato.** Lo nuevo es el instrumento, no el
   swipe. Si el proyecto se anuncia como "un juego nuevo", pierde contra las apps
   que ya están en las tiendas.
2. **Citar a Novoa et al. al publicar los resultados.** Enmarca el hallazgo en
   literatura existente y desactiva la lectura partidista: el sesgo que se mide
   está documentado en dos países y no lo inventó el autor del juego.
3. **No reclamar hallazgos que el diseño no sostiene.** El juego mide atribución
   de frases, no polarización afectiva ni opiniones. Ver `03_metodologia.md`,
   punto 5.
