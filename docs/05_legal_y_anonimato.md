# Legal y anonimato

> Nota (2026-11-13): el proyecto dejó de ser anónimo y su autor es público. Las
> partes sobre anonimato describen el diseño original; ver `DECISIONES.md`.

Verificado el 2026-09-29. Lo que está marcado como incógnita hay que comprobarlo
antes de publicar; no se convierte en conclusión por repetirlo.

## Derechos sobre las frases: cubierto

El **art. 33 TRLPI** permite reproducir, distribuir y comunicar públicamente los
discursos pronunciados en público, y añade algo que no aplica al resto de discursos:
para los **pronunciados en sesiones parlamentarias no se exige que el uso sea
meramente informativo**. Un juego construido con frases del Diario de Sesiones
entra en el límite.

Los datos del corpus son del Congreso, reutilizables al amparo de la **Ley
37/2007**, y el procesado intermedio (`escano-abierto`) es MIT.

## Por qué no se traduce

Tres razones, y la primera basta:

1. **Una traducción deja de ser una cita.** El jugador vería una frase que el
   diputado no pronunció, con un enlace a un documento donde dice otra cosa. Todo
   el proyecto se sostiene en que cualquiera pueda cotejar en diez segundos.
2. **Traducir es elegir palabras, y en política las palabras elegidas son la marca
   ideológica.** Sería reintroducir criterio propio en el único sitio donde se ha
   conseguido quitarlo, y de forma invisible para quien audite el procedimiento.
3. **Incógnita legal.** El art. 33 ampara reproducir, distribuir y comunicar. La
   traducción es **transformación**, que el TRLPI regula aparte (art. 21). Que el
   límite cubra la reproducción no implica que cubra la traducción. Sin verificar,
   y no hace falta verificarlo porque no se va a traducir.

Coste de no traducir: cero. Hay más de 4.000 frases limpias en castellano.

## Derechos morales, que no caducan

Paternidad e integridad (arts. 14-15 TRLPI) son perpetuos. Consecuencias:

- **Hay que atribuir**, y atribuir bien. Cada frase con su fuente.
- **No se puede deformar.** Sin recortes que cambien el sentido, sin frases
  sacadas de una subordinada que invierta lo dicho. El filtro de longitud mínima y
  la exigencia de frase autocontenida sirven también para esto.
- **Atribuir mal es peor que no atribuir.** Es el riesgo principal del proyecto y
  el motivo del filtro de citas de terceros.

## RGPD y LSSI: el diseño evita las obligaciones en vez de cumplirlas

### Anonimato y ranking con alias son incompatibles

El responsable de un tratamiento **tiene que identificarse ante el interesado**
(art. 13 RGPD). No existe el responsable anónimo. Si se recogen alias libres, hay
datos potencialmente identificables y hay que firmar el proyecto con nombre y
contacto.

Por eso **no hay ranking de personas: hay percentil**. Es un agregado, no hay dato
personal, y se comparte mejor ("he acertado más que el 78%") que un puesto en una
tabla. Beneficios adicionales: no hay que moderar alias, que en un juego político
significa insultos en el leaderboard en 24 horas.

La excepción de actividad personal o doméstica del art. 2.2.c del RGPD **no
cubre** una web pública abierta a cualquiera (caso Lindqvist), así que no era una
salida.

### Nada se guarda en el dispositivo

El **art. 22.2 LSSI no habla de cookies**, habla de dispositivos de almacenamiento
y recuperación en el equipo del usuario, y `localStorage` y `sessionStorage` entran
igual que una cookie. Que se borre al cerrar la pestaña no exime (Directrices
2/2023 del CEPD, §37).

Por tanto el estado de la partida vive **solo en memoria de JavaScript**. Coste: al
recargar se pierde la racha. Beneficio: no hay banner y la página de cookies dice
la verdad.

### Términos y condiciones y aviso legal

- **Términos y condiciones: no son obligatorios.** Ninguna norma los exige. Son un
  contrato que protege a quien publica.
- **Aviso legal (art. 10 LSSI):** aplica a quien presta un servicio de la sociedad
  de la información, concepto que se activa con actividad económica **aunque sea
  indirecta**: publicidad, afiliación o promocionar la propia actividad
  profesional. Sin anuncios, sin donaciones y sin enlace al portfolio del autor,
  hay argumento sólido para quedar fuera.
  **El día que se ponga un "invítame a un café" o se enlace desde el portfolio,
  entra.** Es un interruptor, no una zona gris permanente.
- **No se pregunta la opinión del jugador**, solo su atribución. Preguntar opinión
  política convertiría las respuestas en datos del art. 9 del RGPD, categoría
  especial, y cambiaría el proyecto de categoría legal entera.

## Incógnitas abiertas

1. Si el conjunto "Intervenciones" del portal oficial del Congreso incluye el texto
   de los discursos. Si lo incluyera, sería mejor fuente que parsear PDF.
2. Alcance exacto del art. 21 frente al art. 33 para traducciones. Irrelevante
   mientras no se traduzca.
