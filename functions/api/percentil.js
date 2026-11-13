// GET /api/percentil?puntos=N&total=10[&reto=AAAA-MM-DD]: que parte de las partidas
// completas saco menos puntos que N. Es un agregado: no devuelve nada de nadie (regla
// dura 4). Lee el recuento por puntuacion (migracion 0005): como mucho 41 filas por
// consulta, haya las partidas que haya. Sin reto compara con todas las partidas del
// catalogo; con reto, solo con las de ese dia.
import catalogo from "../../web/catalogo.json";

const POR_RONDA = 10;

export async function onRequestGet({ request, env }) {
  const url = new URL(request.url);
  const puntos = Number(url.searchParams.get("puntos"));
  const total = Number(url.searchParams.get("total"));
  const reto = url.searchParams.get("reto");
  if (reto !== null && !/^\d{4}-\d{2}-\d{2}$/.test(reto)) return Response.json({ error: "datos" }, { status: 400 });
  if (!Number.isInteger(puntos) || total !== POR_RONDA || Math.abs(puntos) > 2 * POR_RONDA) {
    return Response.json({ error: "datos" }, { status: 400 });
  }
  const { results } = await env.DB.prepare("SELECT puntos, n FROM recuento WHERE version_catalogo = ? AND grupo = ?")
    .bind(catalogo.version, reto ?? "*")
    .all();
  let n = 0;
  let menos = 0;
  for (const f of results) {
    n += f.n;
    if (f.puntos < puntos) menos += f.n;
  }
  // Con pocas partidas un percentil engana: se dice que aun no hay base.
  if (n < 20) return Response.json({ partidas: n, percentil: null });
  return Response.json({ partidas: n, percentil: Math.round((100 * menos) / n) });
}
