# Objetivos

## Qué es

Un juego web para móvil. Se muestra una frase pronunciada en el Congreso de los
Diputados y el jugador desliza a la izquierda o a la derecha según el bloque al
que crea que pertenece quien la dijo. Al soltar, se revela el autor, el grupo, la
fecha y el enlace a la fuente oficial.

El gesto coincide con el contenido: izquierda y derecha no son una metáfora de
interfaz, son el eje que se mide.

## Qué mide

No mide memoria. Mide **cuánto falla el eje izquierda/derecha como predictor de
lo que se dice**, por tema. La métrica que interesa no es la tasa de acierto sino
**el acierto condicionado a la confianza**: cuánta gente se equivoca estando
segura.

Esa distinción es el proyecto. Una frase que nadie sabe colocar y una frase que
todos colocan mal producen la misma tasa de acierto (50%) y son cosas opuestas:
la primera es relleno, la segunda es el producto.

## Objetivo declarado

**Producto viral**, decidido por Alejandro el 2026-09-29 sobre las alternativas
de pieza de portfolio o ejercicio de despliegue. El criterio de éxito es tráfico
y compartición, no empleabilidad.

Consecuencias asumidas de esa elección, documentadas porque se discutieron:

- El proyecto compite por tiempo con la búsqueda activa de empleo y con el TFM.
- No es ninguna de las cinco piezas del portfolio, así que no descuenta de ahí:
  se suma.
- La retención es cero por construcción (ver `07_riesgos.md`, riesgo 1). Esto es
  una campaña con fecha de caducidad, no un producto con vida propia.

## Objetivo secundario, que llega gratis

El juego es un aparato de captura, así que produce un dato agregado publicable:
*"en sanidad, el N% de las frases se atribuye al bloque equivocado, y el M% de
esos errores se comete con confianza alta"*. Ese dato es lo que un periodista
cita, y es la vía realista a la viralidad: no el juego, sino el resultado.

También cierra un hueco técnico declarado (nunca se ha desplegado nada), sin que
sea la razón del proyecto.

## Restricción de partida

Alejandro no revisa código. Su feedback es funcional y visual. Dos consecuencias
que valen como requisitos:

1. **Cada cambio se entrega como URL de vista previa**, no como diff.
2. **Menos partes móviles gana a más elegancia.** Cada servicio añadido es un
   servicio que nadie podrá depurar.

## Lo que este proyecto no es

- No es una herramienta de fact-checking. No juzga si la frase es verdad.
- No pregunta la opinión del jugador, solo su atribución. Preguntar opinión
  convertiría las respuestas en datos del art. 9 del RGPD.
- No interpreta el resultado. Describe. Ver `03_metodologia.md`, punto 5.

## Origen

La idea inicial (2026-09-29) era otra: adivinar si una imagen es real o generada
con IA, deslizando. Se descartó como producto tras verificar que está construida
y publicada, con la misma mecánica, sin cuenta, con XP y ranking, en App Store,
Google Play, web y clones abiertos. El giro a frases parlamentarias lo propuso
Alejandro en la misma sesión. El historial completo está en `DECISIONES.md`.
