-- Partidas completas y recuento por puntuacion (2026-10-05). El percentil recorria todas
-- las respuestas en cada consulta: con el plan gratuito de D1 (5 millones de filas
-- leidas al dia) unas 700 partidas en un dia lo agotaban. Con el recuento, cada consulta
-- lee como mucho 41 filas (puntuaciones de -20 a +20).
CREATE TABLE partidas (
  sesion_juego TEXT PRIMARY KEY,
  version_catalogo TEXT NOT NULL,
  reto TEXT,
  puntos INTEGER NOT NULL,
  creado_en TEXT NOT NULL DEFAULT (datetime('now'))
);
-- grupo: '*' todas las partidas del catalogo, 'libre', o la fecha del reto.
CREATE TABLE recuento (
  version_catalogo TEXT NOT NULL,
  grupo TEXT NOT NULL,
  puntos INTEGER NOT NULL,
  n INTEGER NOT NULL,
  PRIMARY KEY (version_catalogo, grupo, puntos)
);
-- Partidas ya terminadas antes de esta migracion.
INSERT INTO partidas (sesion_juego, version_catalogo, reto, puntos)
SELECT sesion_juego, MIN(version_catalogo), MAX(reto),
       SUM(CASE WHEN confianza = 2 THEN (CASE WHEN acierto = 1 THEN 2 ELSE -2 END) ELSE acierto END)
FROM respuestas GROUP BY sesion_juego HAVING COUNT(*) = 10;
INSERT INTO recuento (version_catalogo, grupo, puntos, n)
SELECT version_catalogo, '*', puntos, COUNT(*) FROM partidas GROUP BY version_catalogo, puntos;
INSERT INTO recuento (version_catalogo, grupo, puntos, n)
SELECT version_catalogo, COALESCE(reto, 'libre'), puntos, COUNT(*)
FROM partidas GROUP BY version_catalogo, COALESCE(reto, 'libre'), puntos;
