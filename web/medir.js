// Contador de visitas sin cookies (Umami, via /api/u/send). No lee ni escribe nada en el
// dispositivo (regla dura 4): ni cookies, ni localStorage, ni identificadores propios.
// Respeta "Do Not Track" y "Global Privacy Control". Solo mide en escanometro.com.
(function () {
  var activo =
    location.hostname === "escanometro.com" &&
    navigator.doNotTrack !== "1" &&
    navigator.globalPrivacyControl !== true;
  function enviar(nombre) {
    if (!activo) return;
    // Etiqueta de campana (?o=...), que app.js lee y quita de la barra: a Umami va como
    // utm_campaign para que salga en su informe de campanas.
    var o = window.ESCANOMETRO_ORIGEN || "";
    var payload = {
      website: "00000000-0000-0000-0000-000000000000",
      hostname: location.hostname,
      url: location.pathname + (o.indexOf("c:") === 0 ? "?utm_campaign=" + o.slice(2) : ""),
      title: document.title,
      referrer: document.referrer,
      language: navigator.language,
      screen: screen.width + "x" + screen.height,
    };
    if (nombre) payload.name = nombre;
    try {
      fetch("/api/u/send", {
        method: "POST",
        headers: { "content-type": "application/json" },
        body: JSON.stringify({ type: "event", payload: payload }),
        keepalive: true,
      }).catch(function () {});
    } catch (e) {}
  }
  // Modo equipo (?o=equipo): las pruebas propias se etiquetan como "c:equipo" y se separan en
  // el analisis. La etiqueta viaja en los enlaces internos para que no se pierda al navegar;
  // no se guarda nada en el dispositivo.
  if (/(^|[?&])o=equipo(&|$)/.test(location.search)) {
    if (!window.ESCANOMETRO_ORIGEN) window.ESCANOMETRO_ORIGEN = "c:equipo";
    var marcar = function () {
      var enlaces = document.querySelectorAll("a[href]");
      for (var i = 0; i < enlaces.length; i++) {
        var a = enlaces[i];
        if (a.origin !== location.origin || a.protocol.indexOf("http") !== 0) continue;
        var u = new URL(a.href);
        if (!u.searchParams.has("o")) { u.searchParams.set("o", "equipo"); a.href = u.toString(); }
      }
    };
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", marcar); else marcar();
  }
  // Eventos del juego (sin datos de la partida): window.medir("partida_terminada")
  window.medir = enviar;
  enviar();
  // Primera interaccion (tocar, tecla o scroll): un robot que carga la pagina casi nunca la
  // produce, asi que "visitantes con interaccion" se acerca a "personas". Una vez por pagina.
  var hecha = false;
  function interaccion() {
    if (hecha) return;
    hecha = true;
    enviar("interaccion");
    ["pointerdown", "keydown", "scroll"].forEach(function (t) { removeEventListener(t, interaccion, true); });
  }
  ["pointerdown", "keydown", "scroll"].forEach(function (t) { addEventListener(t, interaccion, { capture: true, passive: true }); });
})();
