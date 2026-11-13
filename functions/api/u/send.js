// POST /api/u/send: cuenta visitas sin cookies. Reenvia el ping de web/medir.js al Umami
// propio (autoalojado). El navegador solo habla con escanometro.com: el destino no aparece en la
// pagina y los bloqueadores no tumban la ruta. Umami no guarda la IP: la usa para el pais
// y para un identificador que cambia cada dia, y la descarta (lo dice datos.html).
import { esNube } from "../../../lib/red.js";
const UMAMI = "https://umami.example.com/api/send"; // tu instancia de Umami
const SITIO = "00000000-0000-0000-0000-000000000000"; // id del sitio en Umami

export async function onRequestPost({ request }) {
  let d;
  try {
    d = await request.json();
  } catch {
    return new Response(null, { status: 204 });
  }
  if (esNube(request)) return new Response(null, { status: 204 }); // robots: lib/red.js
  // Solo pings de este sitio y de este dominio: el reenvio no es un proxy abierto.
  if (d?.payload?.website !== SITIO || d?.payload?.hostname !== "escanometro.com") {
    return new Response(null, { status: 204 });
  }
  const cabeceras = new Headers({
    "content-type": "application/json",
    "user-agent": request.headers.get("user-agent") ?? "",
    "x-vz-ip": request.headers.get("cf-connecting-ip") ?? "",
  });
  try {
    await fetch(UMAMI, { method: "POST", headers: cabeceras, body: JSON.stringify(d) });
  } catch {
    // Si Umami no responde, se pierde la medida, no la pagina.
  }
  return new Response(null, { status: 204 });
}
