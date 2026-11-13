# Arquitectura

Criterio de selección: **menos partes móviles gana a más elegancia**, porque quien
mantiene esto no revisa código (ver `01_objetivos.md`, restricción de partida).

## Decisiones

| Capa | Decisión | Por qué |
|---|---|---|
| Sitio | Estático en **Cloudflare Pages** | Un solo proveedor. Imposible tumbarlo con tráfico porque es CDN. Vista previa por rama con `wrangler pages deploy --branch`. Coste 0 |
| Catálogo | JSON generado en build por el pipeline de Python | Reproducible, versionado, sin base de datos en la ruta de lectura |
| Datos | **Cloudflare D1** `sesgo-respuestas` (región WEUR) | SQLite en la misma cuenta que Pages. No se pausa por inactividad. La métrica final es `GROUP BY` |
| Endpoint | Uno solo: `POST /api/respuesta`, como Pages Function | Lo único dinámico del sistema. Sin claves en el navegador: la función habla con D1 por binding |
| Identidad | Ninguna | Ver `05_legal_y_anonimato.md` |

**Supabase descartado el 2026-10-04** (ver `DECISIONES.md`): el plan gratuito pausa
el proyecto tras una semana sin actividad (la web seguiría en pie y dejaría de guardar
respuestas sin avisar), limita a dos proyectos activos por persona y añade un segundo
proveedor con claves que custodiar. D1 vive en la misma cuenta que Pages.

**Riesgo de D1:** un solo proveedor. Si Cloudflare suspende la cuenta caen a la vez la
web y los datos. Mitigación: exportación periódica de la tabla de respuestas a una
máquina propia (`wrangler d1 export`).

## Alternativa descartada

Next.js en Vercel con validación de respuestas en servidor. Evitaría que se pueda
hacer trampa leyendo el JSON del catálogo, a cambio de React, SSR, más superficie y
funciones de servidor, que es donde aparecen las facturas con un pico de tráfico.

La trampa no importa: no hay premio y no hay ranking de personas. Lo que hay que
proteger es la limpieza del dato agregado, y eso se defiende en el análisis
(`03_metodologia.md`, punto 6).

## Trampas de infraestructura ya conocidas

Verificadas en proyectos anteriores:

- **"Proxy naranja, externo gris".** Si el dominio está en Cloudflare DNS y el
  hosting fuera, marcarlo como Proxied rompe certificados y vistas previas. Con
  Cloudflare Pages el problema no existe: es un argumento más para Pages.
- **Bot Fight Mode y Turnstile activan la cookie `__cf_bm`.** Están en el plan
  gratuito y son un interruptor. Si se encienden, la página que dice "no usamos
  cookies" pasa a ser falsa sin tocar el código. Quedan apagados a conciencia.

## El servidor local

- **No sirve el juego.** Un pico de tráfico sobre una IP residencial no se hace.
- **Sí aloja el pipeline** de construcción del catálogo: Python sobre CPU, sin GPU,
  reproducible.

## Páginas de la web

1. **El juego.** Frase, swipe, confianza, reveal con autor, grupo, fecha y enlace a
   la fuente. El enlace tiene que llevar al fragmento con número de sesión, no al
   PDF de 400 páginas: un enlace que no se puede comprobar en diez segundos es
   decoración, no fuente.
2. **Resultado.** Percentil, no puesto en una tabla ("has acertado más que el 78%
   de quienes han jugado"). Es un agregado sin dato personal y se comparte mejor.
3. **Por qué falla tu intuición.** La literatura del fenómeno, explicada y citada:
   el trabajo de Novoa et al. en PNAS sobre generalizaciones de grupo, el de Swire
   et al. sobre el efecto de la etiqueta de partido, el de Zell et al. sobre sesgo
   de atribución, y el precedente del Perception Gap de More in Common. Detalle en
   `08_estado_del_arte.md`.
   Esta página hace tres cosas a la vez: da autoridad, es lo que la prensa enlaza,
   y es la mejor defensa contra la acusación de partidismo, porque el sesgo que se
   mide está documentado por terceros en otros países.
4. **Metodología.** `03_metodologia.md` publicado tal cual, antes de tener
   resultados.
5. **Resultados.** Agregados por tema y por grupo, con los descartes declarados.
   Se publica cuando haya volumen suficiente.

## Esquema de datos (borrador)

`respuestas`: id, frase_id, bloque_mostrado, swipe, acierto, confianza,
ms_reaccion, sesion_juego (aleatorio, efímero, no persistido en el dispositivo),
creado_en.

`frases` (del catálogo, también en el JSON): id, tema, grupo, bloque, orador,
fecha, ds, url_pdf, texto, modelo_clasificador, version_catalogo.

Sin IP, sin user-agent, sin identificador estable. Lo que no se guarda no hay que
declararlo, protegerlo ni explicarlo.
