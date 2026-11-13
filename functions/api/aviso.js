// POST /api/aviso: alguien senala un error en una frase. Anonimo: no se guarda IP,
// cabeceras ni correo. Sustituye a un buzon de correo, que obligaria a tratar la
// direccion de quien escribe (docs/05_legal_y_anonimato.md).
import catalogo from "../../web/catalogo.json";

const IDS = new Set(catalogo.frases.map((f) => f.id));
const MOTIVOS = new Set(["atribucion", "transcripcion", "contexto", "otro"]);

export async function onRequestPost({ request, env }) {
  let d;
  try {
    d = await request.json();
  } catch {
    return Response.json({ error: "json" }, { status: 400 });
  }
  const texto = typeof d.texto === "string" ? d.texto.trim().slice(0, 500) : "";
  if (!IDS.has(d.frase_id) || !MOTIVOS.has(d.motivo)) {
    return Response.json({ error: "datos" }, { status: 400 });
  }
  await env.DB.prepare(
    "INSERT INTO avisos (frase_id, version_catalogo, motivo, texto) VALUES (?, ?, ?, ?)"
  )
    .bind(d.frase_id, catalogo.version, d.motivo, texto || null)
    .run();
  return Response.json({ ok: true });
}
