-- Reto diario: fecha (Madrid) del reto al que pertenece la respuesta; NULL en partida libre.
ALTER TABLE respuestas ADD COLUMN reto TEXT;
CREATE INDEX idx_respuestas_reto ON respuestas (reto);
