// Escañómetro. Rondas de 10 frases, mitad de cada bloque, al azar.
// Cada respuesta es una apuesta en un solo gesto: "creo que" (+1 / 0) o "seguro" (+2 / -2).
// La aguja del medidor lee el gesto en directo; la escala es el hemiciclo.
// El estado vive solo en memoria: nada de cookies ni localStorage (regla dura 4).
"use strict";

const POR_RONDA = 10;
const UMBRAL_CREO = 90; // px de arrastre para "creo que" (70 era demasiado sensible en movil)
const UMBRAL_SEGURO = 0.42; // fraccion del ancho de la ficha para "seguro"
const ANGULO = { neutro: 12, seguro: 50, max: 80, creo: 31, seguroFijo: 68 };
const NOMBRE_BLOQUE = { IZQ: "Izquierda (PSOE · Sumar)", DER: "Derecha (PP · Vox)" };
// Version visible (DECISIONES.md, 2026-10-05): el numero mayor cambia con cada edicion del
// catalogo de frases (2.0 = catalogo con el filtro de calidad); el menor, con cada cambio
// de la aplicacion que se publica.
const VERSION = "2.5";
// ---------- Procedencia del jugador (2026-10-06, migracion 0006) ----------
// Tipo de web de la que llega, o la etiqueta de un enlace de campana (escanometro.com/?o=meneame).
// Vive en memoria mientras dura la pestana: no se guarda nada en el dispositivo (regla 4).
const DOMINIOS_ORIGEN = {
  red_social: ["t.co", "x.com", "twitter.com", "facebook.com", "fb.com", "instagram.com", "tiktok.com",
    "linkedin.com", "lnkd.in", "youtube.com", "threads.net", "bsky.app", "mastodon.social"],
  foro: ["reddit.com", "meneame.net", "forocoches.com", "burbuja.info", "mediavida.com"],
  mensajeria: ["whatsapp.com", "wa.me", "t.me", "telegram.org"],
  universidad: ["ucm.es", "uam.es", "uc3m.es", "ub.edu", "upf.edu", "uab.cat", "uv.es", "ugr.es", "us.es",
    "usal.es", "unizar.es", "ehu.eus", "uned.es", "uniovi.es", "um.es", "ua.es", "uji.es", "udc.es", "usc.gal",
    "uvigo.es", "uma.es", "uca.es", "uco.es", "upo.es", "urjc.es", "uah.es", "uclm.es", "uva.es", "unican.es",
    "unavarra.es", "udl.cat", "urv.cat", "uib.es", "ull.es", "upv.es", "umh.es", "upm.es", "unir.net", "deusto.es"],
  medio: ["elpais.com", "elmundo.es", "eldiario.es", "abc.es", "larazon.es", "lavanguardia.com",
    "elconfidencial.com", "20minutos.es", "publico.es", "rtve.es", "antena3.com", "lasexta.com", "cadenaser.com",
    "cope.es", "ondacero.es", "elespanol.com", "okdiario.com", "infolibre.es", "newtral.es", "maldita.es",
    "elperiodico.com", "expansion.com", "eleconomista.es", "huffingtonpost.es", "vozpopuli.com",
    "theobjective.com", "elplural.com", "ctxt.es", "eldebate.com", "libertaddigital.com", "europapress.es",
    "efe.com", "agendapublica.es"],
};

function origenDeLlegada() {
  const params = new URLSearchParams(location.search);
  const etiqueta = (params.get("o") || "").toLowerCase();
  if (/^[a-z0-9-]{1,30}$/.test(etiqueta)) {
    // "equipo" (pruebas propias) se queda en la barra para que sobreviva a recargas;
    // web/medir.js la propaga a los enlaces internos. Esa direccion no se comparte.
    if (etiqueta === "equipo") return "c:equipo";
    // Fuera de la barra: si el jugador comparte la direccion, quien llegue despues no hereda la campana.
    params.delete("o");
    const resto = params.toString();
    history.replaceState(null, "", location.pathname + (resto ? "?" + resto : "") + location.hash);
    return "c:" + etiqueta;
  }
  if (!document.referrer) return "directo";
  let h;
  try {
    h = new URL(document.referrer).hostname.toLowerCase();
  } catch {
    return "otro";
  }
  if (h === location.hostname) return "interno";
  if (/(^|\.)(google|bing|duckduckgo|yahoo|ecosia|qwant|startpage|yandex)\./.test(h) || h === "search.brave.com") return "buscador";
  for (const [tipo, dominios] of Object.entries(DOMINIOS_ORIGEN)) {
    if (dominios.some((d) => h === d || h.endsWith("." + d))) return tipo;
  }
  if (h.endsWith(".edu")) return "universidad";
  return "otro";
}

const ORIGEN_JUGADOR = origenDeLlegada();
window.ESCANOMETRO_ORIGEN = ORIGEN_JUGADOR; // lo lee web/medir.js para la campana en Umami

const NOMBRE_LADO = { IZQ: "izquierda", DER: "derecha" };
const SVG = "http://www.w3.org/2000/svg";

const $ = (id) => document.getElementById(id);
let catalogo, ronda, indice, aciertos, puntos, seguras, fallosSeguros, respondidas, historial;
let sesion, respondida, mostradaEn, zonaActual;
let demoHecha = false; // la demostracion del gesto se ve una vez por visita (no se guarda nada)
const T_GIRO = 560; // ms, igual que --t-giro: el resultado se conoce al acabar el giro
const T_AVANCE = 600; // ms: tocar la ficha no avanza hasta que el giro ha terminado
// Frases vistas en esta visita, por bloque. Solo en memoria (regla dura 4): al recargar se
// reinicia. Repetir una frase mide memoria, no atribucion.
const vistas = { IZQ: new Set(), DER: new Set() };
let avisoRepeticionDado = false;

// ---------- Puntuacion (debe coincidir con functions/api/percentil.js) ----------
function puntuar(acierto, confianza) {
  if (confianza === 2) return acierto ? 2 : -2;
  return acierto ? 1 : 0;
}

// ---------- Sonido: sintetizado, sin ficheros. Instrumento, no casino. ----------
const sonido = {
  activo: true,
  ctx: null,
  asegurar() {
    if (!this.ctx) {
      const C = window.AudioContext || window.webkitAudioContext;
      if (C) this.ctx = new C();
    }
    if (this.ctx && this.ctx.state === "suspended") this.ctx.resume();
  },
  tono(freq, dur, tipo = "sine", vol = 0.08, desliz = null) {
    if (!this.activo || !this.ctx) return;
    const t = this.ctx.currentTime;
    const o = this.ctx.createOscillator();
    const g = this.ctx.createGain();
    o.type = tipo;
    o.frequency.setValueAtTime(freq, t);
    if (desliz) o.frequency.exponentialRampToValueAtTime(desliz, t + dur);
    g.gain.setValueAtTime(vol, t);
    g.gain.exponentialRampToValueAtTime(0.0001, t + dur);
    o.connect(g).connect(this.ctx.destination);
    o.start(t);
    o.stop(t + dur + 0.02);
  },
  clic() { this.tono(2400, 0.025, "square", 0.025); }, // muesca de la escala
  golpe() { this.tono(180, 0.09, "triangle", 0.12, 90); }, // la ficha cae en su sitio
  acierto() { this.tono(1320, 0.18, "sine", 0.07); setTimeout(() => this.tono(1760, 0.28, "sine", 0.06), 90); },
  fallo() { this.tono(330, 0.22, "sine", 0.07, 260); },
  falloSeguro() { this.tono(220, 0.35, "sawtooth", 0.05, 110); },
};

// ---------- Hemiciclo: logo y escala del medidor ----------
const FILAS = [
  [150, 30],
  [130, 26],
  [110, 22],
  [90, 18],
  [70, 14],
];
function hemiciclo(svg, cx, cy, radioEscano) {
  const escanos = [];
  for (const [r, n] of FILAS) {
    for (let k = 0; k < n; k++) {
      const a = Math.PI - (Math.PI * k) / (n - 1);
      const c = document.createElementNS(SVG, "circle");
      c.setAttribute("cx", (cx + r * Math.cos(a)).toFixed(1));
      c.setAttribute("cy", (cy - r * Math.sin(a)).toFixed(1));
      c.setAttribute("r", radioEscano);
      c.setAttribute("class", "escano");
      c.dataset.angulo = (90 - (a * 180) / Math.PI).toFixed(1); // -90 izquierda, +90 derecha
      svg.appendChild(c);
      escanos.push(c);
    }
  }
  return escanos;
}

function texto(svg, x, y, cadena, clase, ancla = "middle") {
  const t = document.createElementNS(SVG, "text");
  t.setAttribute("x", x);
  t.setAttribute("y", y);
  t.setAttribute("text-anchor", ancla);
  t.setAttribute("class", clase);
  t.textContent = cadena;
  svg.appendChild(t);
}

function construirLogo() {
  const svg = $("logo");
  hemiciclo(svg, 170, 170, 4.2);
  texto(svg, 170, 168, "?", "interrogante");
}

let escanosMedidor = [];
function construirMedidor() {
  const svg = $("medidor");
  escanosMedidor = hemiciclo(svg, 170, 176, 3.6);
  texto(svg, 14, 194, "IZQUIERDA", "rotulo", "start");
  texto(svg, 326, 194, "DERECHA", "rotulo", "end");
  // Escala grabada: marcas finas fuera del hemiciclo; mas largas en los umbrales de la apuesta.
  const grados = new Set([0, ANGULO.neutro, -ANGULO.neutro, ANGULO.seguro, -ANGULO.seguro]);
  for (let g = -90; g <= 90; g += 6) grados.add(g);
  for (const g of grados) {
    const a = ((90 - g) * Math.PI) / 180;
    const umbral = [0, ANGULO.neutro, ANGULO.seguro].includes(Math.abs(g));
    const r1 = 160, r2 = umbral ? 170 : 165;
    const l = document.createElementNS(SVG, "line");
    l.setAttribute("x1", (170 + r1 * Math.cos(a)).toFixed(1));
    l.setAttribute("y1", (176 - r1 * Math.sin(a)).toFixed(1));
    l.setAttribute("x2", (170 + r2 * Math.cos(a)).toFixed(1));
    l.setAttribute("y2", (176 - r2 * Math.sin(a)).toFixed(1));
    l.setAttribute("class", umbral ? "marca umbral" : "marca");
    svg.insertBefore(l, svg.firstChild);
  }
  const g = document.createElementNS(SVG, "g");
  g.setAttribute("class", "aguja reposo");
  g.id = "aguja";
  const l = document.createElementNS(SVG, "line");
  l.setAttribute("x1", 170);
  l.setAttribute("y1", 176);
  l.setAttribute("x2", 170);
  l.setAttribute("y2", 46);
  const c = document.createElementNS(SVG, "circle");
  c.setAttribute("cx", 170);
  c.setAttribute("cy", 176);
  c.setAttribute("r", 7);
  g.append(l, c);
  svg.appendChild(g);
}

// Angulo de la aguja -> zona de lectura.
function zonaDe(angulo) {
  const a = Math.abs(angulo);
  if (a < ANGULO.neutro) return null;
  return { lado: angulo < 0 ? "IZQ" : "DER", confianza: a >= ANGULO.seguro ? 2 : 1 };
}

// Vuelta a la respiracion de reposo, pendiente tras reposarAguja(). Se cancela en cuanto
// la aguja se mueve: si no, un arrastre rapido nada mas aparecer la ficha la devolvia
// al centro a mitad de gesto.
let temporizadorReposo = null;

function moverAguja(angulo, suelta) {
  const aguja = $("aguja");
  clearTimeout(temporizadorReposo);
  aguja.classList.remove("reposo");
  aguja.classList.toggle("suelta", !!suelta);
  aguja.style.transform = `rotate(${angulo}deg)`;
  for (const e of escanosMedidor) {
    const ae = Number(e.dataset.angulo);
    const encendido = Math.abs(ae) >= ANGULO.neutro && Math.sign(ae) === Math.sign(angulo) && Math.abs(ae) <= Math.abs(angulo);
    e.classList.toggle("encendido", encendido);
  }
  const z = zonaDe(angulo);
  const clave = z ? z.lado + z.confianza : "";
  if (clave !== zonaActual) {
    if (zonaActual !== undefined) sonido.clic();
    zonaActual = clave;
  }
  const lectura = $("lectura");
  lectura.textContent = z ? `${z.confianza === 2 ? "Seguro" : "Creo que"} · ${NOMBRE_LADO[z.lado]}` : "En reposo";
  lectura.classList.toggle("activa", !!z);
}

// Al acertar, los escanos del lado elegido se encienden de dentro afuera: la
// celebracion es el propio instrumento, sin confeti.
function barrido(lado) {
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  const signo = lado === "IZQ" ? -1 : 1;
  const lista = escanosMedidor
    .filter((e) => Math.sign(Number(e.dataset.angulo)) === signo)
    .sort((a, b) => Math.abs(a.dataset.angulo) - Math.abs(b.dataset.angulo));
  lista.forEach((e, i) => temporizadoresBarrido.push(setTimeout(() => e.classList.add("barrido"), i * 7)));
}

// Barrido pendiente: se cancela al cambiar de ficha para que no termine sobre la siguiente.
let temporizadoresBarrido = [];
function cancelarBarrido() {
  temporizadoresBarrido.forEach(clearTimeout);
  temporizadoresBarrido = [];
}

function reposarAguja() {
  const aguja = $("aguja");
  cancelarBarrido();
  for (const e of escanosMedidor) e.classList.remove("barrido");
  aguja.classList.add("suelta");
  aguja.style.transform = "rotate(0deg)";
  for (const e of escanosMedidor) e.classList.remove("encendido");
  zonaActual = undefined;
  $("lectura").textContent = "En reposo";
  $("lectura").classList.remove("activa");
  clearTimeout(temporizadorReposo);
  temporizadorReposo = setTimeout(() => {
    if (!respondida) {
      aguja.classList.remove("suelta");
      aguja.style.transform = "";
      aguja.classList.add("reposo");
    }
  }, 450);
}

// Arrastre en px -> angulo, por tramos que coinciden con los umbrales de la apuesta.
function anguloDeArrastre(dx) {
  const ancho = $("tarjeta").offsetWidth;
  const seguroPx = ancho * UMBRAL_SEGURO;
  const a = Math.abs(dx);
  let ang;
  if (a < UMBRAL_CREO) ang = (a / UMBRAL_CREO) * ANGULO.neutro;
  else if (a < seguroPx) ang = ANGULO.neutro + ((a - UMBRAL_CREO) / (seguroPx - UMBRAL_CREO)) * (ANGULO.seguro - ANGULO.neutro);
  else ang = ANGULO.seguro + Math.min(1, (a - seguroPx) / (ancho * 0.3)) * (ANGULO.max - ANGULO.seguro);
  return Math.sign(dx) * ang;
}

// ---------- Partida ----------
function barajar(lista) {
  const a = [...lista];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

// ---------- Reto diario: las mismas diez frases para todo el mundo cada dia ----------
// Se calcula en el navegador a partir de la fecha de Madrid y del catalogo: no hace falta
// servidor ni cuenta. Rejugarlo en la misma pestana cuenta como partida libre.
const LANZAMIENTO = "2026-10-05"; // reto nº 1
let modo = "libre";
let retoJugado = null;
// Percentil de la partida y las imagenes ya dibujadas. Se preparan al llegar al resultado
// para que "Compartir" llame al menu nativo sin esperas: Safari en iOS rechaza el menu si
// entre el toque y la llamada pasa demasiado trabajo.
let percentilPartida = null;
let imagenesListas = {};

function hoyMadrid() {
  return new Intl.DateTimeFormat("en-CA", { timeZone: "Europe/Madrid" }).format(new Date());
}

function numeroReto(dia) {
  return Math.floor((Date.parse(dia + "T12:00:00Z") - Date.parse(LANZAMIENTO + "T12:00:00Z")) / 864e5) + 1;
}

function generador(semilla) {
  let h = 2166136261;
  for (const c of semilla) h = Math.imul(h ^ c.charCodeAt(0), 16777619);
  return () => {
    h = (h + 0x6d2b79f5) | 0;
    let t = Math.imul(h ^ (h >>> 15), 1 | h);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

function barajarCon(lista, azar) {
  const a = [...lista];
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(azar() * (i + 1));
    [a[i], a[j]] = [a[j], a[i]];
  }
  return a;
}

function retoDelDia(dia) {
  const azar = generador(`${catalogo.version}|${dia}`);
  const ordenadas = [...catalogo.frases].sort((a, b) => (a.id < b.id ? -1 : 1));
  const de = (b) => barajarCon(ordenadas.filter((f) => f.bloque === b), azar).slice(0, POR_RONDA / 2);
  return barajarCon([...de("IZQ"), ...de("DER")], azar);
}

// Eventos agregados para Umami (web/medir.js): que paso, nunca datos de la partida.
function medir(nombre) {
  if (window.medir) window.medir(nombre);
}

function nuevaRonda(tipo = "libre") {
  sonido.asegurar();
  const dia = hoyMadrid();
  modo = tipo === "reto" && retoJugado !== dia ? "reto" : "libre";
  if (modo === "reto") {
    ronda = retoDelDia(dia);
    retoJugado = dia;
    for (const f of ronda) vistas[f.bloque].add(f.id);
  } else {
    const izq = elegir("IZQ");
    const der = elegir("DER");
    ronda = barajar([...izq, ...der]);
  }
  indice = aciertos = puntos = seguras = fallosSeguros = respondidas = 0;
  historial = [];
  percentilPartida = null;
  imagenesListas = {};
  sesion = crypto.randomUUID();
  medir(modo === "reto" ? "reto_empezado" : "libre_empezada");
  mostrar("juego");
  pintarFrase();
}

function mostrar(id) {
  for (const s of document.querySelectorAll(".pantalla")) s.hidden = s.id !== id;
  window.scrollTo(0, 0);
  enfocarPantalla(id);
}

const dos = (n) => String(n).padStart(2, "0");

function pintarMarcador(cambio) {
  const m = $("marcador-vivo");
  m.textContent = `${puntos > 0 ? "+" : ""}${puntos} pts`;
  if (!cambio) return;
  m.dataset.cambio = `${cambio > 0 ? "+" : "−"}${Math.abs(cambio)}`;
  m.classList.remove("sube", "baja");
  void m.offsetWidth; // reinicia la animacion
  m.classList.add(cambio > 0 ? "sube" : "baja");
}

function pintarFrase() {
  const f = ronda[indice];
  // Marcador en directo (decidido 2026-10-05). Para no perder la medida de la confianza,
  // cada respuesta guarda los puntos que llevaba el jugador (puntos_antes): el analisis
  // puede separar si quien va perdiendo apuesta "seguro" por estrategia.
  $("contador").textContent = `Frase ${dos(indice + 1)}/${POR_RONDA}`;
  pintarMarcador();
  $("tema").textContent = f.tema;
  $("registro-num").textContent = `Reg. ${f.ds ? f.ds.replace("DSCD-15-", "") : ""}`;
  $("tema-dorso").textContent = `Reg. ${f.ds ? f.ds.replace("DSCD-15-", "") : ""}`;
  $("frase").textContent = `“${f.frase}”`;
  $("ficha-num").textContent = `Ficha ${dos(indice + 1)}`;
  $("tarjeta").style.transform = "";
  $("giro").className = "";
  $("sello").className = "sello";
  $("botones-lado").hidden = false;
  $("revelacion").hidden = true;
  respondida = false;
  $("tarjeta").classList.remove("avanzable");
  vistas[f.bloque].add(f.id);
  pintarProgreso();
  accesibilidadFrase(f);
  reposarAguja();
  mostradaEn = performance.now();
  if (!demoHecha && matchMedia("(pointer: coarse)").matches) demostrarGesto();
}

// En tactil, la primera ficha se balancea sola y la aguja la acompana: ensena el gesto.
function demostrarGesto() {
  demoHecha = true;
  const t = $("tarjeta");
  $("pista-gesto").hidden = false;
  if (matchMedia("(prefers-reduced-motion: reduce)").matches) return;
  t.classList.add("demo");
  const pasos = [[500, 0], [940, -22], [1490, -5], [1930, 22], [2370, 4], [2700, 0]];
  for (const [ms, ang] of pasos) setTimeout(() => !respondida && moverAguja(ang, true), ms);
  setTimeout(() => {
    t.classList.remove("demo");
    if (!respondida) reposarAguja();
  }, 2800);
}

function responder(lado, confianza) {
  if (respondida) return;
  respondida = true;
  const ms = Math.round(performance.now() - mostradaEn);
  const f = ronda[indice];
  const acierto = lado === f.bloque;
  const p = puntuar(acierto, confianza);
  const puntosAntes = puntos;
  aciertos += acierto ? 1 : 0;
  puntos += p;
  setTimeout(() => pintarMarcador(p), 600); // tras el giro, como el resto de la revelacion
  respondidas++;
  if (confianza === 2) seguras++;
  if (!acierto && confianza === 2) fallosSeguros++;
  historial.push({ acierto, confianza, lado, puntos: p, frase: f, ms }); // en memoria, para el repaso final

  const signo = lado === "IZQ" ? -1 : 1;
  moverAguja(signo * (confianza === 2 ? ANGULO.seguroFijo : ANGULO.creo), true);
  sonido.golpe();
  if (acierto) temporizadoresBarrido.push(setTimeout(() => barrido(lado), 600));
  setTimeout(() => (acierto ? sonido.acierto() : confianza === 2 ? sonido.falloSeguro() : sonido.fallo()), 560);
  alGirar(acierto, confianza);

  $("botones-lado").hidden = true;
  $("pista-gesto").hidden = true;
  $("tarjeta").classList.remove("demo");
  $("tarjeta").style.transform = "";
  $("giro").className = "girada";
  const sello = $("sello");
  sello.textContent = acierto ? "Acierto" : "Fallo";
  sello.className = "sello " + (acierto ? "acierto" : "fallo");
  $("frase-dorso").textContent = `“${f.frase}”`; // el reverso recuerda lo que se dijo
  $("autor").textContent = f.orador;
  $("bloque").textContent = `${f.grupo} · ${NOMBRE_LADO[f.bloque]}`;
  $("fecha").textContent = fechaCorta(f.fecha);
  $("apuesta").textContent =
    `${confianza === 2 ? "Seguro" : "Creo que"} ${NOMBRE_LADO[lado]} · ${p > 0 ? "+" : p < 0 ? "−" : ""}${Math.abs(p)}`;
  $("fuente").href = f.pdf;
  // Retrato oficial del Congreso, sin modificar (condiciones de reutilizacion de congreso.es).
  // Sin retrato oficial (escano dejado durante la legislatura): marco vacio, para que el
  // reverso tenga siempre la misma composicion y el sello no tape el texto.
  const retrato = $("retrato");
  retrato.hidden = false;
  retrato.classList.toggle("vacio", !f.foto);
  retrato.querySelector("figcaption").textContent = f.foto ? "Foto: Congreso" : "Sin retrato oficial";
  retrato.querySelector("img")?.remove();
  if (f.foto) {
    const foto = new Image(62, 82);
    foto.decoding = "async";
    foto.src = f.foto;
    foto.alt = `Retrato oficial de ${f.orador}`;
    retrato.prepend(foto);
  }
  $("revelacion").hidden = false;
  anunciarVeredicto(f, lado, confianza, acierto, p);
  enviar({
    sesion_juego: sesion,
    version_catalogo: catalogo.version,
    frase_id: f.id,
    swipe: lado,
    confianza,
    ms_reaccion: ms,
    reto: modo === "reto" ? retoJugado : null,
    origen: ORIGEN_JUGADOR,
    puntos_antes: puntosAntes,
  });
}

function enviar(datos) {
  // Si falla, el juego sigue: perder una respuesta es mejor que bloquear al jugador.
  fetch("/api/respuesta", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(datos),
  }).catch(() => {});
}

function fechaCorta(iso) {
  return new Date(iso + "T12:00:00").toLocaleDateString("es-ES", { day: "numeric", month: "short", year: "numeric" });
}

function fechaLarga(iso) {
  return new Date(iso + "T12:00:00").toLocaleDateString("es-ES", { day: "numeric", month: "long", year: "numeric" });
}

// ---------- Catalogo: si no llega o llega vacio, se dice y se ofrece reintentar ----------
const ERRORES_CATALOGO = {
  red: ["Sin señal", "El catálogo de frases no ha llegado. Sin frases no hay nada que medir. Suele ser la conexión."],
  vacio: ["Catálogo vacío", "El catálogo ha llegado sin frases suficientes para una partida. No es cosa de tu conexión."],
};

function catalogoValido(c) {
  return !!c && Array.isArray(c.frases) &&
    ["IZQ", "DER"].every((b) => c.frases.filter((f) => f.bloque === b).length >= POR_RONDA / 2);
}

// No devuelve hasta tener un catalogo valido: entre intento e intento espera a "Reintentar".
async function cargarCatalogo() {
  for (let intento = 1; ; intento++) {
    let motivo = "vacio";
    try {
      const r = await fetch("catalogo.json", intento > 1 ? { cache: "no-cache" } : undefined);
      if (!r.ok) throw new Error(`HTTP ${r.status}`);
      const c = await r.json();
      if (catalogoValido(c)) {
        mostrarErrorCatalogo(null);
        return c;
      }
    } catch (e) {
      motivo = e instanceof SyntaxError ? "vacio" : "red"; // JSON roto es contenido, no red
    }
    mostrarErrorCatalogo(motivo, intento);
    await new Promise((seguir) => {
      $("reintentar").onclick = () => {
        $("error-rotulo").textContent = "Reintentando…";
        seguir();
      };
    });
  }
}

function mostrarErrorCatalogo(motivo, intento) {
  const caja = $("error-catalogo");
  const empezar = $("empezar");
  if (!motivo) {
    const teniaFoco = caja.contains(document.activeElement);
    caja.hidden = true;
    empezar.hidden = false;
    $("libre").hidden = false;
    if (teniaFoco) enfocar(empezar);
    return;
  }
  const [rotulo, texto] = ERRORES_CATALOGO[motivo];
  $("error-rotulo").textContent = intento > 1 ? `${rotulo} · intento ${intento}` : rotulo;
  $("error-texto").textContent = texto;
  const teniaFoco = document.activeElement === empezar;
  caja.hidden = false;
  empezar.hidden = true; // sin catalogo, "Empezar" no haria nada
  $("libre").hidden = true;
  if (teniaFoco) enfocar($("reintentar"));
  anunciar(`${rotulo}. ${texto}`);
}

// ---------- Accesibilidad: anuncios, foco y caras de la ficha ----------
function prepararAccesibilidad() {
  // La lectura de la aguja cambia en cada muesca del arrastre y en la demostracion del
  // gesto: anunciada en directo es ruido. El veredicto se anuncia una vez, en #anuncio.
  $("lectura")?.removeAttribute("aria-live");
  const a = document.createElement("p");
  a.id = "anuncio";
  a.className = "solo-lector";
  a.setAttribute("role", "status");
  document.body.appendChild(a);
  const llegada = document.querySelector("#final .visor"); // punto de llegada del foco al terminar
  if (llegada) llegada.tabIndex = -1;
}

function enfocar(el) {
  if (el) el.focus({ preventScroll: true });
}

// Solo la cara visible es accesible: antes de girar, el dorso (con el registro de la
// frase anterior); despues de girar, el frente (si no, la frase se leeria dos veces).
function dorsoInerte(si) {
  const d = document.querySelector("#giro .dorso");
  const f = document.querySelector("#giro .frente");
  if (d) d.inert = si;
  if (f) f.inert = !si;
}

function anunciar(mensaje) {
  const a = $("anuncio");
  a.textContent = "";
  setTimeout(() => (a.textContent = mensaje), 100); // vaciar y rellenar: se anuncia aunque se repita
}

function enfocarPantalla(id) {
  if (id === "final") enfocar(document.querySelector("#final .visor"));
}

// Frase nueva: la ficha se nombra con su texto y recibe el foco. El dorso guarda el
// registro y el enlace de la frase anterior: fuera del lector y del tabulador hasta girar.
function accesibilidadFrase(f) {
  const t = $("tarjeta");
  t.setAttribute("aria-label", `Frase ${indice + 1} de ${POR_RONDA}, ${f.tema}: “${f.frase}”`);
  dorsoInerte(true);
  $("anuncio").textContent = "";
  enfocar(t);
}

// Tras responder: el dorso vuelve, el foco pasa a Siguiente y el veredicto se anuncia
// despues, para que el anuncio del foco no lo corte. Si ya se ha pasado de frase, se calla.
function anunciarVeredicto(f, lado, confianza, acierto, p) {
  dorsoInerte(false);
  enfocar($("siguiente"));
  const n = indice;
  const mensaje =
    `${acierto ? "Acierto" : "Fallo"}. Lo dijo ${f.orador}, de ${f.grupo}: ${NOMBRE_LADO[f.bloque]}. ` +
    `Tu apuesta: ${confianza === 2 ? "seguro" : "creo que"}, ${NOMBRE_LADO[lado]}. ` +
    `${p > 0 ? "+" : ""}${p} ${Math.abs(p) === 1 ? "punto" : "puntos"}.`;
  setTimeout(() => {
    if (respondida && indice === n && !$("juego").hidden) anunciar(mensaje);
  }, 300);
}

function siguiente() {
  indice++;
  if (indice < POR_RONDA) return pintarFrase();
  terminar();
}

const veces = (n) => `${n} ${n === 1 ? "vez" : "veces"}`;

// Una fila sin spoiler para compartir: no revela ninguna frase ni su respuesta.
// Mismo codigo de forma que los escanos del visor: lleno acierto, hueco fallo,
// anillo "seguro". Caracteres tipograficos monocromos con selector de texto (FE0E)
// para que ningun sistema los convierta en emoji.
function simbolo(h) {
  const c = h.confianza === 2 ? (h.acierto ? "◉" : "◎") : h.acierto ? "●" : "○";
  return c + "\uFE0E";
}

// En pantalla, la fila son los mismos escanos dibujados del visor (no caracteres).
function pintarTira() {
  const tira = $("tira");
  tira.textContent = "";
  for (const h of historial) {
    const p = document.createElement("span");
    p.className = "punto " + (h.acierto ? "acierto" : "fallo") + (h.confianza === 2 ? " seguro" : "");
    tira.appendChild(p);
  }
}

async function terminar() {
  mostrar("final");
  $("final-version").textContent = modo === "reto" ? `Reto nº ${numeroReto(retoJugado)}` : `${respondidas}/${POR_RONDA} frases`;
  const manana = $("manana");
  manana.hidden = modo !== "reto";
  if (modo === "reto") manana.textContent = `Mañana, reto nº ${numeroReto(retoJugado) + 1}. Mientras, puedes jugar partidas libres.`;
  $("puntuacion").textContent = `${puntos > 0 ? "+" : ""}${puntos}`;
  $("aciertos-final").textContent = `${aciertos}/${respondidas}`;
  $("fallos-final").textContent = `${fallosSeguros}/${seguras}`;
  pintarTira();
  $("copiado").textContent = "";
  pintarRepaso();
  avisarRepeticion();
  if (!respondidas) {
    $("resumen").textContent = "No has respondido ninguna frase.";
    $("percentil").textContent = "";
    return;
  }
  pintarTitulo();
  pintarSorpresa();
  pintarLectura();
  if (respondidas === POR_RONDA) medir(modo === "reto" ? "reto_terminado" : "libre_terminada");
  $("resumen").textContent = seguras
    ? `Has dicho "seguro" ${veces(seguras)}` + (fallosSeguros ? ` y te has equivocado en ${fallosSeguros}.` : " y has acertado en todas.")
    : 'No has dicho "seguro" ninguna vez.';
  if (respondidas < POR_RONDA) {
    $("percentil").textContent = "La comparación con el resto solo se hace con partidas completas de 10 frases.";
    return;
  }
  $("percentil").textContent = "Comparando con el resto de partidas…";
  try {
    const filtro = modo === "reto" ? `&reto=${retoJugado}` : "";
    const ronda0 = sesion;
    const r = await (await fetch(`/api/percentil?puntos=${puntos}&total=${POR_RONDA}${filtro}`)).json();
    if (sesion !== ronda0) return; // ya se juega otra ronda
    percentilPartida = Number.isInteger(r.percentil) ? r.percentil : null;
    // Partidas, no personas: una misma persona puede jugar varias y no hay forma de saberlo.
    $("percentil").textContent =
      percentilPartida === null
        ? "Todavía hay muy pocas partidas para compararte con el resto."
        : `Has sacado más puntos que el ${percentilPartida}% de las partidas${modo === "reto" ? " de este reto" : ""}.`;
  } catch {
    $("percentil").textContent = "";
  }
  prepararImagenes();
}

function textoPercentil() {
  return percentilPartida === null ? "" : `Mejor que el ${percentilPartida}% de las partidas${modo === "reto" ? " del reto" : ""}.`;
}

async function prepararImagenes() {
  const ronda0 = sesion; // si empieza otra ronda mientras se dibuja, se descarta
  try {
    const resultado = await imagenResultado();
    const h = modo === "libre" ? sorpresaPartida() : null;
    const sorpresa = h ? await imagenSorpresa(h) : null;
    if (sesion === ronda0) imagenesListas = { resultado, sorpresa };
  } catch {
    /* se dibujaran al pulsar */
  }
}

// Titulo de la partida: describe como apuesta el jugador (su calibracion), nunca su
// ideologia ni la de los partidos. Es lo que se comparte.
function tituloPartida() {
  if (!respondidas) return null;
  const tasa = aciertos / respondidas;
  if (seguras >= 3 && fallosSeguros === 0) return ["Instrumento calibrado", 'Cuando dices "seguro", aciertas.'];
  if (seguras >= 3 && fallosSeguros / seguras >= 0.5) return ["Aguja descalibrada", "Tu seguridad va por delante de tus aciertos."];
  if (seguras === 0) return ["Lectura prudente", 'No te la has jugado ni una vez con "seguro".'];
  if (tasa <= 0.5) return ["Ruido de fondo", "Has acertado lo mismo que una moneda al aire."];
  return ["Lectura fiable", "Más aciertos que fallos, y la aguja no se dispara."];
}

function pintarTitulo() {
  const t = tituloPartida();
  $("titulo-final").hidden = !t;
  if (!t) return;
  $("titulo-sello").textContent = t[0];
  $("titulo-texto").textContent = t[1];
}

// ---------- Lectura por tema y por bloque (2026-10-07) ----------
// El resultado habla del jugador a partir de sus atribuciones, nunca de su opinion (regla 5).
// Con 10 frases salen 3-4 por tema: se dan cuentas ("2 de 3"), no porcentajes.
const ORDEN_TEMAS = ["vivienda", "sanidad", "pensiones"];
const NOMBRE_TEMA = { vivienda: "Vivienda", sanidad: "Sanidad", pensiones: "Pensiones" };

function lecturaPartida() {
  const temas = ORDEN_TEMAS.map((tema) => {
    const h = historial.filter((x) => x.frase.tema === tema);
    return { tema, ok: h.filter((x) => x.acierto).length, n: h.length, marcas: h.map((x) => x.acierto) };
  }).filter((t) => t.n > 0);
  const bloque = (b) => {
    const h = historial.filter((x) => x.frase.bloque === b);
    return { ok: h.filter((x) => x.acierto).length, n: h.length };
  };
  return { temas, izq: bloque("IZQ"), der: bloque("DER") };
}

function fraseLectura(l) {
  const { izq, der, temas } = l;
  // Lo que mas llama: diferencia entre bloques (2 o mas aciertos de distancia), o el tema mas flojo.
  if (izq.n && der.n && Math.abs(izq.ok - der.ok) >= 2) {
    const peor = izq.ok < der.ok ? ["izquierda", izq, "derecha", der] : ["derecha", der, "izquierda", izq];
    return `Te cuestan más las frases de la ${peor[0]}: aciertas ${peor[1].ok} de ${peor[1].n}, frente a ${peor[3].ok} de ${peor[3].n} de la ${peor[2]}.`;
  }
  const conVarias = temas.filter((t) => t.n >= 2);
  if (conVarias.length >= 2) {
    const tasa = (t) => t.ok / t.n;
    const peor = conVarias.reduce((a, b) => (tasa(b) < tasa(a) ? b : a));
    const mejor = conVarias.reduce((a, b) => (tasa(b) > tasa(a) ? b : a));
    if (tasa(mejor) - tasa(peor) >= 0.5) {
      return `Donde más te engañan: ${NOMBRE_TEMA[peor.tema].toLowerCase()} (${peor.ok} de ${peor.n}). Donde mejor lees: ${NOMBRE_TEMA[mejor.tema].toLowerCase()} (${mejor.ok} de ${mejor.n}).`;
    }
  }
  return "Aciertas parecido en todos los temas y con los dos bloques.";
}

function pintarLectura() {
  if (!$("por-tema")) return; // HTML antiguo en cache con el JS nuevo
  const l = lecturaPartida();
  $("por-tema").hidden = respondidas < 4;
  if (respondidas < 4) return;
  const ul = $("por-tema-filas");
  ul.textContent = "";
  const fila = (etiqueta, ok, n, marcas) => {
    const li = nodo("li", "por-tema-fila");
    li.append(nodo("span", "por-tema-etq", etiqueta));
    if (marcas) li.append(nodo("span", "por-tema-marcas", marcas.map((m) => (m ? "●" : "○")).join("")));
    li.append(nodo("span", "por-tema-cifra", `${ok} de ${n}`));
    ul.append(li);
  };
  for (const t of l.temas) fila(NOMBRE_TEMA[t.tema], t.ok, t.n, t.marcas);
  if (l.izq.n) fila("Frases de la izquierda", l.izq.ok, l.izq.n);
  if (l.der.n) fila("Frases de la derecha", l.der.ok, l.der.n);
  $("por-tema-frase").textContent = fraseLectura(l);
}

function lineaTemas() {
  return lecturaPartida().temas.map((t) => `${NOMBRE_TEMA[t.tema]} ${t.ok}/${t.n}`).join(" · ");
}

function textoParaCompartir() {
  const t = tituloPartida();
  return (
    `Escañómetro${modo === "reto" ? ` · reto nº ${numeroReto(retoJugado)}` : ""}: ${aciertos}/${respondidas} y ${puntos > 0 ? "+" : ""}${puntos} puntos` +
    (t ? ` · «${t[0]}»` : "") + "\n" +
    `${historial.map(simbolo).join("")}\n` +
    (historial.length >= 4 ? lineaTemas() + "\n" : "") +
    `Dije "seguro" ${seguras} ${seguras === 1 ? "vez" : "veces"} y fallé ${fallosSeguros}. ` +
    (percentilPartida === null ? "" : textoPercentil() + " ") +
    "¿Distingues a la izquierda de la derecha por lo que dicen en el Congreso?\n" +
    location.origin
  );
}

// En movil, el menu nativo de compartir (WhatsApp, Telegram...); si no existe, copiar.
// ---------- Imagen del resultado (1080x1350, 4:5) ----------
// Se dibuja en el navegador: sin servidor y sin guardar nada. No revela ninguna frase,
// para no estropear el reto a quien aun no lo ha jugado.
const COLOR_IMG = {
  papel: "#F2EEE4", ficha: "#FBF8F1", tinta: "#1F1D1A", suave: "#655F54", linea: "#D3CBB9",
  laton: "#86600F", acierto: "#24524C", fallo: "#7E4220",
};

async function imagenResultado() {
  await Promise.all([
    document.fonts.load('600 80px "Plex Serif"'), document.fonts.load('italic 400 40px "Plex Serif"'),
    document.fonts.load('600 40px "Plex Mono"'), document.fonts.load('400 30px "Plex Mono"'),
  ]);
  const W = 1080, H = 1350, c = document.createElement("canvas");
  c.width = W; c.height = H;
  const g = c.getContext("2d");
  const C = COLOR_IMG;
  g.fillStyle = C.papel; g.fillRect(0, 0, W, H);
  const centrado = (txt, y, font, color, espaciado = 0) => {
    g.font = font; g.fillStyle = color; g.textAlign = "center";
    if ("letterSpacing" in g) g.letterSpacing = `${espaciado}px`;
    g.fillText(txt, W / 2, y);
    if ("letterSpacing" in g) g.letterSpacing = "0px";
  };
  // Hemiciclo tenue de fondo, arriba
  g.fillStyle = C.linea;
  for (const [r, n] of FILAS) for (let k = 0; k < n; k++) {
    const a = Math.PI - (Math.PI * k) / (n - 1);
    g.beginPath(); g.arc(W / 2 + r * 2.1 * Math.cos(a), 370 - r * 2.1 * Math.sin(a), 7, 0, 2 * Math.PI); g.fill();
  }
  centrado("ESCAÑÓMETRO", 190, '600 34px "Plex Mono"', C.laton, 10);
  centrado(modo === "reto" ? `RETO Nº ${numeroReto(retoJugado)} · ${fechaCorta(retoJugado).toUpperCase()}` : "PARTIDA LIBRE",
    240, '400 28px "Plex Mono"', C.suave, 4);
  // Sello del titulo
  const t = tituloPartida() || ["Resultado", ""];
  g.save(); g.translate(W / 2, 430); g.rotate((-3 * Math.PI) / 180);
  g.font = '600 58px "Plex Mono"';
  if ("letterSpacing" in g) g.letterSpacing = "8px";
  const ancho = g.measureText(t[0].toUpperCase()).width + 70;
  g.strokeStyle = C.laton; g.lineWidth = 4; g.strokeRect(-ancho / 2, -62, ancho, 104);
  g.lineWidth = 2; g.strokeRect(-ancho / 2 + 9, -53, ancho - 18, 86);
  g.fillStyle = C.laton; g.textAlign = "center"; g.fillText(t[0].toUpperCase(), 0, 10);
  g.restore();
  centrado(t[1], 560, 'italic 400 40px "Plex Serif"', C.suave);
  // Marcador
  const cajas = [["PUNTOS", `${puntos > 0 ? "+" : ""}${puntos}`], ["ACIERTOS", `${aciertos}/${respondidas}`], ["FALLOS SEGURO", `${fallosSeguros}/${seguras}`]];
  const x0 = 90, ancho3 = (W - 180) / 3, y0 = 630;
  g.fillStyle = C.ficha; g.fillRect(x0, y0, W - 180, 200);
  g.strokeStyle = C.linea; g.lineWidth = 2; g.strokeRect(x0, y0, W - 180, 200);
  cajas.forEach(([etq, val], i) => {
    const x = x0 + i * ancho3;
    if (i) { g.beginPath(); g.moveTo(x, y0); g.lineTo(x, y0 + 200); g.stroke(); }
    g.textAlign = "left"; g.fillStyle = C.suave; g.font = '600 24px "Plex Mono"';
    g.fillText(etq, x + 28, y0 + 52);
    g.fillStyle = C.tinta; g.font = '600 84px "Plex Mono"'; g.fillText(val, x + 28, y0 + 158);
  });
  // Los diez escanos del resultado: lleno acierto, hueco fallo, anillo "seguro"
  const n = historial.length, paso = 78, xi = W / 2 - ((n - 1) * paso) / 2, yd = 930;
  historial.forEach((h, i) => {
    const x = xi + i * paso, col = h.acierto ? C.acierto : C.fallo;
    g.lineWidth = 5; g.strokeStyle = col; g.fillStyle = col;
    g.beginPath(); g.arc(x, yd, 20, 0, 2 * Math.PI);
    if (h.acierto) g.fill(); else g.stroke();
    if (h.confianza === 2) { g.lineWidth = 3; g.beginPath(); g.arc(x, yd, 31, 0, 2 * Math.PI); g.stroke(); }
  });
  const conPercentil = percentilPartida !== null;
  const conTemas = historial.length >= 4;
  if (conTemas) centrado(lineaTemas().toUpperCase(), 1003, '600 26px "Plex Mono"', C.suave, 3);
  centrado(seguras ? `Dije "seguro" ${seguras} ${seguras === 1 ? "vez" : "veces"} y fallé ${fallosSeguros}.` : 'No dije "seguro" ni una vez.',
    conTemas ? (conPercentil ? 1053 : 1065) : (conPercentil ? 1025 : 1050), '400 40px "Plex Serif"', C.tinta);
  if (conPercentil) {
    const txt = textoPercentil().replace(/\.$/, "").toUpperCase();
    let tam = 34;
    g.font = `600 ${tam}px "Plex Mono"`;
    while (g.measureText(txt).width + txt.length * 3 > W - 180 && tam > 22) g.font = `600 ${--tam}px "Plex Mono"`;
    centrado(txt, conTemas ? 1103 : 1088, `600 ${tam}px "Plex Mono"`, C.laton, 3);
  }
  g.strokeStyle = C.linea; g.lineWidth = 2; g.beginPath(); g.moveTo(90, 1130); g.lineTo(W - 90, 1130); g.stroke();
  centrado("¿Lo dijo la izquierda o la derecha?", 1200, 'italic 400 44px "Plex Serif"', C.tinta);
  centrado(location.host.toUpperCase(), 1275, '600 30px "Plex Mono"', C.laton, 6);
  return await new Promise((ok) => c.toBlob(ok, "image/png"));
}

// ---------- "Mi sorpresa": una sola frase, elegida por el fallo del jugador ----------
// Nunca la elige el proyecto: es el fallo estando seguro (el mas rapido) o, si no hay, el
// fallo mas rapido. El mensaje va sobre el error del jugador, no sobre el politico, y la
// fuente va siempre visible. En el reto no se ofrece: desvelaria frases a quien no ha jugado.
function sorpresaPartida() {
  const fallos = historial.filter((h) => !h.acierto);
  if (!fallos.length) return null;
  const seguros = fallos.filter((h) => h.confianza === 2);
  return (seguros.length ? seguros : fallos).reduce((a, b) => (b.ms < a.ms ? b : a));
}

function fraseSorpresa(h) {
  // Sin marca de genero: quien juega no ha dicho quien es.
  const lado = NOMBRE_LADO[h.lado];
  return h.confianza === 2 ? `Lo tenía claro: esto lo dijo la ${lado}.` : `Creía que esto lo dijo la ${lado}.`;
}

function pintarSorpresa() {
  const h = sorpresaPartida();
  $("sorpresa").hidden = !h;
  if (!h) return;
  $("sorpresa-texto").textContent = `${fraseSorpresa(h)} Lo dijo ${h.frase.orador} (${h.frase.grupo}).`;
  const enReto = modo === "reto";
  $("compartir-sorpresa").disabled = enReto;
  $("sorpresa-nota").textContent = enReto
    ? "En el reto del día no se comparten frases: desvelaría las respuestas a quien aún no ha jugado. En partida libre, sí."
    : "Se comparte una sola frase, con su autor y su fuente.";
}

function partirEnLineas(g, texto, ancho) {
  const lineas = [];
  let actual = "";
  for (const palabra of texto.split(" ")) {
    const prueba = actual ? actual + " " + palabra : palabra;
    if (g.measureText(prueba).width > ancho && actual) {
      lineas.push(actual);
      actual = palabra;
    } else actual = prueba;
  }
  if (actual) lineas.push(actual);
  return lineas;
}

async function imagenSorpresa(h) {
  await Promise.all([
    document.fonts.load('400 56px "Plex Serif"'), document.fonts.load('italic 400 40px "Plex Serif"'),
    document.fonts.load('600 30px "Plex Mono"'), document.fonts.load('400 26px "Plex Mono"'),
  ]);
  const W = 1080, H = 1350, C = COLOR_IMG, f = h.frase;
  const c = document.createElement("canvas");
  c.width = W; c.height = H;
  const g = c.getContext("2d");
  g.fillStyle = C.papel; g.fillRect(0, 0, W, H);
  g.textAlign = "left";
  g.fillStyle = C.laton; g.font = '600 30px "Plex Mono"';
  if ("letterSpacing" in g) g.letterSpacing = "8px";
  g.fillText("ESCAÑÓMETRO · MI SORPRESA", 90, 140);
  if ("letterSpacing" in g) g.letterSpacing = "0px";
  g.fillStyle = C.tinta; g.font = 'italic 400 46px "Plex Serif"';
  partirEnLineas(g, fraseSorpresa(h), W - 180).forEach((l, i) => g.fillText(l, 90, 230 + i * 58));
  // Ficha de archivo a la medida de la frase; ficha y autoria, centradas entre cabecera y pie
  const fx = 70, fw = W - 140;
  let tam = 66, lineas;
  do {
    g.font = `400 ${tam}px "Plex Serif"`;
    lineas = partirEnLineas(g, `“${f.frase}”`, fw - 90);
    tam -= 2;
  } while (lineas.length * (tam + 2) * 1.38 > 560 && tam > 34);
  tam += 2;
  const interlinea = tam * 1.38, fh = 150 + lineas.length * interlinea;
  const fy = Math.round(330 + (1170 - 330 - (fh + 150)) / 2);
  g.fillStyle = C.ficha; g.fillRect(fx, fy, fw, fh);
  g.strokeStyle = C.linea; g.lineWidth = 2; g.strokeRect(fx, fy, fw, fh);
  g.fillStyle = C.suave; g.font = '600 24px "Plex Mono"';
  if ("letterSpacing" in g) g.letterSpacing = "4px";
  g.fillText("DIARIO DE SESIONES", fx + 40, fy + 60);
  g.textAlign = "right"; g.fillText(f.tema.toUpperCase(), fx + fw - 40, fy + 60);
  if ("letterSpacing" in g) g.letterSpacing = "0px";
  g.beginPath(); g.moveTo(fx + 40, fy + 82); g.lineTo(fx + fw - 40, fy + 82); g.stroke();
  g.textAlign = "left"; g.fillStyle = C.tinta; g.font = `400 ${tam}px "Plex Serif"`;
  lineas.forEach((l, i) => g.fillText(l, fx + 45, fy + 105 + tam + i * interlinea));
  // Quien lo dijo y fuente
  const ya = fy + fh + 80;
  g.fillStyle = C.tinta; g.font = '600 40px "Plex Serif"';
  g.fillText(`Lo dijo ${f.orador} (${f.grupo})`, 90, ya);
  g.fillStyle = C.suave; g.font = '400 26px "Plex Mono"';
  g.fillText(`${NOMBRE_LADO[f.bloque].toUpperCase()} · ${fechaLarga(f.fecha).toUpperCase()} · ${f.ds || ""}`, 90, ya + 50);
  g.strokeStyle = C.linea; g.beginPath(); g.moveTo(90, 1190); g.lineTo(W - 90, 1190); g.stroke();
  g.fillStyle = C.tinta; g.font = 'italic 400 40px "Plex Serif"';
  g.fillText("¿Y tú? ¿La habrías acertado?", 90, 1260);
  g.textAlign = "right"; g.fillStyle = C.laton; g.font = '600 28px "Plex Mono"';
  g.fillText(location.host.toUpperCase(), W - 90, 1260);
  return await new Promise((ok) => c.toBlob(ok, "image/png"));
}

async function compartirSorpresa() {
  const h = sorpresaPartida();
  if (!h || modo === "reto") return;
  medir("compartir_sorpresa");
  const blob = imagenesListas.sorpresa || (await imagenSorpresa(h));
  const nombre = "escanometro-mi-sorpresa.png";
  const texto = `${fraseSorpresa(h)} Lo dijo ${h.frase.orador} (${h.frase.grupo}). ¿Y tú? ${location.origin}`;
  const archivo = new File([blob], nombre, { type: "image/png" });
  if (navigator.share && navigator.canShare && navigator.canShare({ files: [archivo] })) {
    try {
      await navigator.share({ title: "Escañómetro", text: texto, files: [archivo] });
      return;
    } catch (e) {
      if (e && e.name === "AbortError") return;
    }
  }
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = nombre;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 2000);
}

function nombreImagen() {
  return modo === "reto" ? `escanometro-reto-${numeroReto(retoJugado)}.png` : "escanometro-resultado.png";
}

async function guardarImagen() {
  medir("guardar_imagen");
  const blob = imagenesListas.resultado || (await imagenResultado());
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = nombreImagen();
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 2000);
}

async function compartir() {
  medir("compartir_resultado");
  const texto = textoParaCompartir();
  if (navigator.share) {
    try {
      const blob = imagenesListas.resultado || (await imagenResultado());
      const archivo = new File([blob], nombreImagen(), { type: "image/png" });
      const conImagen = navigator.canShare && navigator.canShare({ files: [archivo] });
      await navigator.share(conImagen ? { title: "Escañómetro", text: texto, files: [archivo] } : { title: "Escañómetro", text: texto });
      return;
    } catch (e) {
      if (e && e.name === "AbortError") return; // el jugador cerro el menu
    }
  }
  try {
    await navigator.clipboard.writeText(texto);
    $("copiado").textContent = "Copiado. Pégalo donde quieras.";
  } catch {
    $("copiado").textContent = texto;
  }
}

// ---------- Progreso, avance, repaso y vibracion ----------
function nodo(tag, clase, txt) {
  const e = document.createElement(tag);
  if (clase) e.className = clase;
  if (txt !== undefined) e.textContent = txt;
  return e;
}

// Frases del bloque sin ver en esta visita. Si no quedan cinco, entran las que quedan y el
// bloque vuelve a empezar con el resto: nunca se rompe el 5 + 5 de la ronda.
const sinVer = (bloque) => catalogo.frases.filter((f) => f.bloque === bloque && !vistas[bloque].has(f.id));
function elegir(bloque) {
  const n = POR_RONDA / 2;
  let elegidas = barajar(sinVer(bloque)).slice(0, n);
  if (elegidas.length < n) {
    vistas[bloque].clear();
    const resto = barajar(sinVer(bloque).filter((f) => !elegidas.includes(f)));
    elegidas = [...elegidas, ...resto.slice(0, n - elegidas.length)];
  }
  return elegidas;
}

// Se avisa una sola vez, en la pantalla final, antes de la ronda que ya repetiria frases.
function avisarRepeticion() {
  const p = $("aviso-repeticion");
  p.hidden = true;
  if (avisoRepeticionDado) return;
  if (sinVer("IZQ").length >= POR_RONDA / 2 && sinVer("DER").length >= POR_RONDA / 2) return;
  avisoRepeticionDado = true;
  p.textContent = "Has visto casi todas las frases del archivo: en la próxima ronda empiezan a repetirse.";
  p.hidden = false;
}

// Mismo codigo que la fila de compartir, en grafico: lleno = acierto, hueco = fallo,
// anillo = "seguro". La forma distingue el resultado; el color solo lo refuerza.
const claseDe = (h) => `punto ${h.acierto ? "acierto" : "fallo"}${h.confianza === 2 ? " seguro" : ""}`;
function describir(h) {
  if (h.confianza === 2) return h.acierto ? "acierto estando seguro" : "fallo estando seguro";
  return h.acierto ? "acierto con «creo que»" : "fallo con «creo que»";
}

// Diez escanos en el visor. El de la frase respondida se sella al acabar el giro, no antes:
// el visor no adelanta el resultado.
function pintarProgreso(recien) {
  const ol = $("progreso");
  ol.replaceChildren();
  for (let i = 0; i < POR_RONDA; i++) {
    const h = historial[i];
    const li = nodo("li", h ? claseDe(h) : i === indice ? "punto actual" : "punto");
    if (i === recien) li.classList.add("recien");
    if (i === indice) li.setAttribute("aria-current", "step");
    li.append(nodo("span", "solo-lector", `Frase ${i + 1} de ${POR_RONDA}: ${h ? describir(h) : i === indice ? "en juego" : "pendiente"}`));
    ol.append(li);
  }
}

// Al girar la ficha: vibra con el sonido y, cuando el giro acaba, el punto se sella y la
// ficha se puede tocar para seguir. Las guardas evitan pintar sobre otra frase u otra ronda.
function alGirar(acierto, confianza) {
  const n = indice;
  const s = sesion;
  setTimeout(() => vibrar(acierto, confianza), T_GIRO);
  setTimeout(() => {
    if (sesion !== s || indice !== n || !respondida) return;
    pintarProgreso(n);
    $("tarjeta").classList.add("avanzable");
  }, T_AVANCE);
}

// Corta al acertar, larga y doble al fallar estando seguro. Obedece al interruptor de sonido.
function vibrar(acierto, confianza) {
  if (!sonido.activo || typeof navigator.vibrate !== "function") return;
  try {
    navigator.vibrate(acierto ? 15 : confianza === 2 ? [70, 60, 160] : 40);
  } catch {}
}

// Tocar la ficha girada pasa a la siguiente. El enlace a la fuente sigue siendo un enlace.
// El clic que sigue al arrastre llega antes de "avanzable" (T_AVANCE) y se ignora.
function activarAvance() {
  const t = $("tarjeta");
  t.addEventListener("click", (e) => {
    if (!respondida || !t.classList.contains("avanzable") || e.target.closest("a, button")) return;
    siguiente();
  });
}

// Repaso en la pantalla final: cada frase jugada en miniatura, con su fuente.
function pintarRepaso() {
  const lista = $("repaso-lista");
  lista.replaceChildren();
  $("repaso").hidden = !historial.length;
  historial.forEach((h, i) => {
    const f = h.frase;
    const falloSeguro = h.confianza === 2 && !h.acierto;
    const li = nodo("li", "repaso-item" + (falloSeguro ? " fallo-seguro" : ""));
    const cab = nodo("div", "repaso-cab");
    const marca = nodo("span", claseDe(h));
    marca.setAttribute("aria-hidden", "true");
    const resultado = falloSeguro ? "Fallo estando seguro" : h.acierto ? "Acierto" : "Fallo";
    cab.append(marca, nodo("span", "", `${dos(i + 1)} · ${f.tema}`), nodo("span", "repaso-resultado " + (h.acierto ? "acierto" : "fallo"), resultado));
    const pie = nodo("div", "repaso-pie");
    const apuesta = `Tu apuesta: ${h.confianza === 2 ? "seguro" : "creo que"}, ${NOMBRE_LADO[h.lado]} · ${h.puntos > 0 ? "+" : ""}${h.puntos}`;
    const a = nodo("a", "repaso-fuente", "Fuente ↗");
    a.href = f.pdf;
    a.target = "_blank";
    a.rel = "noopener";
    a.setAttribute("aria-label", `Fuente de la frase ${i + 1}, en el Diario de Sesiones`);
    pie.append(nodo("span", "", apuesta), a);
    li.append(
      cab,
      nodo("blockquote", "repaso-frase", `“${f.frase}”`),
      nodo("p", "repaso-autor", `${f.orador} (${f.grupo}), ${NOMBRE_LADO[f.bloque]}`),
      pie,
    );
    lista.append(li);
  });
}

// ---------- Entrada: arrastre, teclas y teclado ----------
// Arrastre con bloqueo de eje. Los primeros px deciden si el gesto es vertical (scroll:
// la ficha no se mueve) u horizontal (apuesta). Una cancelacion del navegador, que llega
// cuando empieza el scroll, nunca cuenta como apuesta: antes podia registrar una.
const ZONA_MUERTA = 12; // px antes de decidir el eje
function activarArrastre() {
  const t = $("tarjeta");
  let x0 = null, y0 = null, eje = null;
  const reiniciar = () => {
    x0 = y0 = eje = null;
    t.style.transform = "";
    if (!respondida) reposarAguja();
  };
  t.addEventListener("pointerdown", (e) => {
    if (respondida) return;
    sonido.asegurar();
    x0 = e.clientX;
    y0 = e.clientY;
    eje = null;
  });
  t.addEventListener("pointermove", (e) => {
    if (x0 === null) return;
    const dx = e.clientX - x0;
    const dy = e.clientY - y0;
    if (eje === null) {
      if (Math.hypot(dx, dy) < ZONA_MUERTA) return;
      eje = Math.abs(dx) > Math.abs(dy) * 1.2 ? "h" : "v";
      if (eje === "h") t.setPointerCapture(e.pointerId);
    }
    if (eje !== "h") return;
    t.style.transform = `translateX(${dx * 0.6}px) rotate(${dx / 40}deg)`;
    moverAguja(anguloDeArrastre(dx), false);
  });
  t.addEventListener("pointerup", (e) => {
    if (x0 === null) return;
    const z = eje === "h" ? zonaDe(anguloDeArrastre(e.clientX - x0)) : null;
    if (z) {
      x0 = y0 = eje = null;
      responder(z.lado, z.confianza);
    } else reiniciar();
  });
  t.addEventListener("pointercancel", () => x0 !== null && reiniciar());
}

// Al usar el teclado, la tecla equivalente en pantalla se hunde: un solo aparato.
function hundir(el) {
  if (!el) return;
  el.classList.add("pulsada");
  setTimeout(() => el.classList.remove("pulsada"), 140);
}

function activarTeclado() {
  document.addEventListener("keydown", (e) => {
    if ($("juego").hidden) return;
    if (!respondida && (e.key === "ArrowLeft" || e.key === "ArrowRight")) {
      e.preventDefault();
      sonido.asegurar();
      const lado = e.key === "ArrowLeft" ? "IZQ" : "DER";
      const confianza = e.shiftKey ? 2 : 1;
      hundir(document.querySelector(`#botones-lado .tecla[data-lado="${lado}"][data-confianza="${confianza}"]`));
      const kbds = [...document.querySelectorAll(".teclas-ayuda kbd")];
      hundir(kbds.find((k) => k.textContent === (lado === "IZQ" ? "←" : "→")));
      responder(lado, confianza);
    } else if (respondida && e.key === "Enter" && !e.target.closest("a, button")) {
      // Sobre un enlace o un boton, Intro hace lo suyo (abrir la fuente, terminar...).
      e.preventDefault();
      siguiente();
    }
  });
}

function activarSonido() {
  const b = $("sonido");
  b.onclick = () => {
    sonido.activo = !sonido.activo;
    b.setAttribute("aria-pressed", String(sonido.activo));
    b.textContent = `Sonido: ${sonido.activo ? "sí" : "no"}`;
    if (sonido.activo) {
      sonido.asegurar();
      sonido.clic();
    }
  };
}

// El marco de foco de la ficha solo con teclado: con el dedo o el raton parece un error.
function modoEntrada() {
  document.addEventListener("keydown", () => document.body.classList.add("con-teclado"));
  document.addEventListener("pointerdown", () => document.body.classList.remove("con-teclado"));
}

// Aviso de error sobre la frase en curso: anonimo, a /api/aviso (sustituye al buzon).
function activarAviso() {
  const d = $("dialogo-aviso");
  const form = $("form-aviso");
  $("abrir-aviso").onclick = (e) => {
    e.stopPropagation();
    form.reset();
    $("aviso-estado").textContent = "";
    $("enviar-aviso").disabled = false;
    d.showModal();
  };
  $("cancelar-aviso").onclick = () => d.close();
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const datos = new FormData(form);
    const f = ronda && ronda[indice];
    if (!f) return d.close();
    $("enviar-aviso").disabled = true;
    try {
      const r = await fetch("/api/aviso", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ frase_id: f.id, motivo: datos.get("motivo"), texto: datos.get("texto") || "" }),
      });
      if (!r.ok) throw new Error(String(r.status));
      $("aviso-estado").textContent = "Gracias. Lo revisaremos contra el Diario de Sesiones.";
      setTimeout(() => d.close(), 1600);
    } catch {
      $("aviso-estado").textContent = "No se ha podido enviar. Inténtalo de nuevo en un momento.";
      $("enviar-aviso").disabled = false;
    }
  });
}

async function arrancar() {
  modoEntrada();
  construirLogo();
  construirMedidor();
  prepararAccesibilidad();
  catalogo = await cargarCatalogo();
  $("version").textContent = `Versión ${VERSION} · catálogo ${catalogo.version}` + (catalogo.provisional ? " (provisional, sin cotejar)" : "");
  $("empezar").onclick = () => nuevaRonda("reto");
  $("libre").onclick = () => nuevaRonda("libre");
  $("otra").onclick = () => nuevaRonda("libre");
  $("reto-num").textContent = `Reto nº ${numeroReto(hoyMadrid())} · ${fechaCorta(hoyMadrid())}`;
  $("siguiente").onclick = siguiente;
  $("terminar").onclick = terminar;
  $("compartir").onclick = compartir;
  $("guardar-imagen").onclick = guardarImagen;
  $("compartir-sorpresa").onclick = compartirSorpresa;
  for (const b of document.querySelectorAll("#botones-lado .tecla")) {
    b.onclick = () => {
      sonido.asegurar();
      responder(b.dataset.lado, Number(b.dataset.confianza));
    };
  }
  activarArrastre();
  activarTeclado();
  activarSonido();
  activarAvance();
  activarAviso();
}

arrancar();
