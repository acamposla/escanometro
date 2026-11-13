-- Procedencia del jugador, en categorias y sin datos personales (2026-10-06). El canal
-- decide quien juega y la cifra publicada describe a esa poblacion: sin esto no se podria
-- decir a quien describe. Ver DECISIONES.md.
--   origen: tipo de web de la que llega (buscador, red_social, foro, medio, mensajeria,
--           universidad, directo, interno, otro) o la etiqueta de un enlace de campana
--           ("c:meneame"). Lo calcula el navegador al cargar y no se guarda en el dispositivo.
--   pais: 'ES' u 'otro', de Cloudflare. No se guarda la IP.
--   red_nube: 1 si la conexion sale de un centro de datos (probable robot). Se marca, no
--             se descarta: la decision de excluir se toma en el analisis, a la vista.
ALTER TABLE respuestas ADD COLUMN origen TEXT;
ALTER TABLE respuestas ADD COLUMN pais TEXT;
ALTER TABLE respuestas ADD COLUMN red_nube INTEGER;
