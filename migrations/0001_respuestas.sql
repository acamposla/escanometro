-- Una fila por frase respondida. Sin IP, sin user-agent, sin identificador estable:
-- sesion_juego es aleatorio y vive solo en la memoria de la pestana (docs/04).
-- confianza: 1 = "creo que", 2 = "seguro" (desde el 2026-10-04).
CREATE TABLE respuestas (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  sesion_juego TEXT NOT NULL,
  version_catalogo TEXT NOT NULL,
  frase_id TEXT NOT NULL,
  tema TEXT NOT NULL,
  bloque_real TEXT NOT NULL CHECK (bloque_real IN ('IZQ', 'DER')),
  swipe TEXT NOT NULL CHECK (swipe IN ('IZQ', 'DER')),
  acierto INTEGER NOT NULL CHECK (acierto IN (0, 1)),
  confianza INTEGER NOT NULL CHECK (confianza BETWEEN 1 AND 3),
  ms_reaccion INTEGER,
  creado_en TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_respuestas_sesion ON respuestas (sesion_juego);
CREATE UNIQUE INDEX idx_respuestas_unica ON respuestas (sesion_juego, frase_id);
