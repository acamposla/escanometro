// POST /api/respuesta: guarda una frase respondida. Lo unico dinamico del sistema.
// El acierto se calcula aqui, contra el catalogo, no se acepta del navegador.
// No se guarda la IP ni ninguna cabecera de la peticion (docs/05, regla dura 4).
import catalogo from "../../web/catalogo.json";
import { esNube, pais } from "../../lib/red.js";

const POR_ID = new Map(catalogo.frases.map((f) => [f.id, f]));
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$/;
const POR_RONDA = 10;
// Procedencia (migracion 0006): categoria de la web de llegada o etiqueta de campana.
const ORIGEN = /^(directo|interno|buscador|red_social|foro|medio|mensajeria|universidad|otro|c:[a-z0-9-]{1,30})$/;
// Puntuacion (igual que web/app.js): "creo que" +1 / 0, "seguro" +2 / -2.
const PUNTOS_SQL = "SUM(CASE WHEN confianza = 2 THEN (CASE WHEN acierto = 1 THEN 2 ELSE -2 END) ELSE acierto END)";

// Al llegar la decima respuesta, la partida se anota una vez y suma en el recuento por
// puntuacion del que lee /api/percentil (migracion 0005).
async function cerrarPartida(db, sesion) {
  const p = await db
    .prepare(`SELECT COUNT(*) AS n, ${PUNTOS_SQL} AS puntos, MAX(reto) AS reto FROM respuestas WHERE sesion_juego = ?`)
    .bind(sesion)
    .first();
  if (!p || p.n !== POR_RONDA) return;
  const alta = await db
    .prepare("INSERT OR IGNORE INTO partidas (sesion_juego, version_catalogo, reto, puntos) VALUES (?, ?, ?, ?)")
    .bind(sesion, catalogo.version, p.reto, p.puntos)
    .run();
  if (alta.meta?.changes !== 1) return; // ya contada (dos ultimas respuestas a la vez)
  const sumar = db.prepare(
    `INSERT INTO recuento (version_catalogo, grupo, puntos, n) VALUES (?, ?, ?, 1)
     ON CONFLICT (version_catalogo, grupo, puntos) DO UPDATE SET n = n + 1`
  );
  await db.batch([sumar.bind(catalogo.version, "*", p.puntos), sumar.bind(catalogo.version, p.reto ?? "libre", p.puntos)]);
}

export async function onRequestPost({ request, env }) {
  let d;
  try {
    d = await request.json();
  } catch {
    return Response.json({ error: "json" }, { status: 400 });
  }
  const frase = POR_ID.get(d.frase_id);
  const valido =
    frase &&
    typeof d.sesion_juego === "string" && UUID.test(d.sesion_juego) &&
    (d.swipe === "IZQ" || d.swipe === "DER") &&
    [1, 2].includes(d.confianza) && // 1 = "creo que", 2 = "seguro"
    d.version_catalogo === catalogo.version;
  if (!valido) return Response.json({ error: "datos" }, { status: 400 });

  // Reto diario: solo se acepta la fecha de hoy o de ayer (partidas que cruzan la medianoche).
  let reto = null;
  if (typeof d.reto === "string" && /^\d{4}-\d{2}-\d{2}$/.test(d.reto)) {
    const hoy = new Intl.DateTimeFormat("en-CA", { timeZone: "Europe/Madrid" }).format(new Date());
    const ayer = new Intl.DateTimeFormat("en-CA", { timeZone: "Europe/Madrid" }).format(new Date(Date.now() - 864e5));
    if (d.reto === hoy || d.reto === ayer) reto = d.reto;
  }
  const puntosAntes = Number.isInteger(d.puntos_antes) && Math.abs(d.puntos_antes) <= 40 ? d.puntos_antes : null;
  const ms = Number.isInteger(d.ms_reaccion) && d.ms_reaccion >= 0 && d.ms_reaccion < 600000 ? d.ms_reaccion : null;
  const acierto = d.swipe === frase.bloque ? 1 : 0;
  const origen = typeof d.origen === "string" && ORIGEN.test(d.origen) ? d.origen : null;
  const guardada = await env.DB.prepare(
    `INSERT OR IGNORE INTO respuestas
       (sesion_juego, version_catalogo, frase_id, tema, bloque_real, swipe, acierto, confianza, ms_reaccion, reto, puntos_antes,
        origen, pais, red_nube)
     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)`
  )
    .bind(d.sesion_juego, catalogo.version, frase.id, frase.tema, frase.bloque, d.swipe, acierto, d.confianza, ms, reto, puntosAntes,
      origen, pais(request), esNube(request) ? 1 : 0)
    .run();
  if (guardada.meta?.changes === 1) {
    try {
      await cerrarPartida(env.DB, d.sesion_juego);
    } catch {
      // Si falla el recuento, la respuesta ya esta guardada: el percentil se recalcula
      // a partir de respuestas si hiciera falta.
    }
  }
  return Response.json({ acierto });
}
