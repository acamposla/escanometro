-- Avisos de error sobre una frase (mal atribuida, mal transcrita, fuera de contexto).
-- Anonimos: sin correo, sin IP, sin identificador. El texto libre es opcional y corto.
CREATE TABLE avisos (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  frase_id TEXT NOT NULL,
  version_catalogo TEXT NOT NULL,
  motivo TEXT NOT NULL CHECK (motivo IN ('atribucion', 'transcripcion', 'contexto', 'otro')),
  texto TEXT CHECK (texto IS NULL OR length(texto) <= 500),
  creado_en TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_avisos_frase ON avisos (frase_id);
