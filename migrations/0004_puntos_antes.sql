-- Puntos que llevaba el jugador al responder. El marcador se ve en directo: con esto el
-- analisis puede comprobar si quien va perdiendo apuesta "seguro" por estrategia.
ALTER TABLE respuestas ADD COLUMN puntos_antes INTEGER;
