// Clasificacion de la conexion para separar robots de personas (2026-10-05/06). Se usa en el
// reenvio a Umami (descarta) y en /api/respuesta (marca, no descarta). Solo se mira la red
// de origen que da Cloudflare (`request.cf.asn`); no se guarda la IP ni la red.
//
// Redes de centros de datos: de ahi salen rastreadores y escaneres que se presentan como un
// Chrome normal. NO estan Cloudflare (13335), Akamai (36183) ni Fastly (54113): por ellas
// sale gente real con WARP o con el Relay privado de iCloud.
export const NUBES = new Set([
  15169, 396982, // Google y Google Cloud
  16509, 14618, // Amazon
  8075, // Microsoft
  14061, // DigitalOcean
  16276, // OVH
  24940, // Hetzner
  63949, // Linode
  31898, // Oracle
  45102, 132203, // Alibaba, Tencent
  12876, 20473, 51167, 60781, // Scaleway, Vultr, Contabo, Leaseweb
]);

export function esNube(request) {
  return NUBES.has(request.cf?.asn);
}

// Pais en dos valores: el resultado se publica para España y basta con separar lo demas.
export function pais(request) {
  const c = request.cf?.country;
  if (!c) return null;
  return c === "ES" ? "ES" : "otro";
}
