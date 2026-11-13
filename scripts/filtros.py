"""Filtros y saneamiento del corpus parlamentario.

Un candidato entra al catalogo si sobrevive a tres exclusiones y a un
saneamiento previo. El criterio es publico y esta documentado en
docs/03_metodologia.md: nadie elige frases a mano.
"""

import hashlib
import re

# Grupos del catalogo inicial. Solo los cuatro estatales: en ellos el eje
# izquierda/derecha no admite discusion. Junts y PNV quedan fuera a proposito
# (ver docs/03_metodologia.md, seccion "Por que solo cuatro grupos").
DERECHA = {"PP", "VOX"}
IZQUIERDA = {"PSOE", "SUMAR"}

# Longitud util: por debajo no hay afirmacion, por encima no se lee en un swipe.
LONGITUD_MIN = 80
LONGITUD_MAX = 180

# Temas del catalogo inicial. Elegidos por balance y volumen medidos, no por
# interes editorial: ver docs/02_investigacion.md, tabla de temas.
TEMAS = {
    "sanidad": r"sanidad|sanitari|lista de espera|atenci.n primaria|hospital",
    "vivienda": r"vivienda|alquiler|inquilin|desahucio|okupa|hipotec",
    "pensiones": r"pensi(o|ó)n|jubilaci|cotizaci",
}

# 1. Autodelacion: la frase revela el emisor sin que el jugador razone.
#    Incluye nombres y siglas de grupo, referencias a la propia bancada,
#    apelaciones al rival y el aparato de la sesion.
_AUTODELATA = re.compile(
    r"se(ñ|n)or|presidenta|gracias|votaci|art.culo|enmienda|usted|"
    r"(Partido|Grupo|Portavoz)\s+(Popular|Socialista|Parlamentario)|"
    r"PSOE|\bPP\b|\bVOX\b|Vox|Sumar|Podemos|"
    r"\bnosotras\b|"  # el femenino generico del grupo delata a Sumar (2026-10-05)
    r"Gobierno|Ejecutivo|ministr|ministerio|Moncloa|izquierda|derecha|"
    r"Bildu|Esquerra|\bERC\b|Junts|\bPNV\b|"
    r"S(a|á)nchez|sanchismo|Feij(o|ó)o|Ayuso|Abascal|"
    # Personas politicas: delatan igual que unas siglas. Lista cerrada, ampliada el
    # 2026-10-04 con las que aparecian en el pool (32 frases, casi todas de un solo bloque).
    r"\bIlla\b|Moreno Bonilla|Juanma Moreno|Ma(ñ|n)ueco|Maz(o|ó)n|L(o|ó)pez Miras|Garc(i|í)a-Page|"
    r"Pradales|Clavijo|Barb(o|ó)n|Azc(o|ó)n|Guardiola|Chivite|Prohens|Puigdemont|Junqueras|Rufi(a|á)n|"
    r"Rajoy|Zapatero|Aznar|Felipe Gonz(a|á)lez|Pablo Iglesias|Errej(o|ó)n|Belarra|Yolanda D(i|í)az|"
    r"\bMontero\b|Bola(ñ|n)os|(O|Ó)scar Puente|Tellado|Gamarra|Bendodo|Almeida|"
    r"este grupo|nuestro grupo|su grupo|bancada|proposici.n|moci.n",
    re.I,
)

# 2. Cita de terceros: el corpus atribuye la frase a quien la pronuncia, no a
#    quien la dijo primero. Sin este filtro el juego produciria atribuciones
#    falsas con datos correctos, que es el fallo que no se puede permitir.
_CITA = re.compile(
    r"[\"“”«»]|\b(dijo|dijeron|afirm(o|ó)|declar(o|ó)|prometi(o|ó)|"
    r"seg.n\s+(el|la|los)|cito|textualmente|palabras de|"
    r"(dicen|afirman|aseguran|sostienen) que)\b",
    re.I,
)

# 3. Lengua distinta del castellano: el idioma delata el grupo sin leer el
#    contenido. Se descarta en vez de traducir (traducir deja de ser cita y
#    reintroduce criterio propio en el texto; ver docs/05_legal_y_anonimato.md).
#    Catalan y valenciano, gallego y euskera. Ampliado el 2026-10-04: dos frases en
#    gallego y una en valenciano pasaban con la lista anterior.
_NO_CASTELLANO = re.compile(
    r"\b(és|amb|aquest|aquesta|això|dels|les|nostra|molt|perquè|hem|volem|"
    r"també|però|hui|avui|venim|voldria|senyories|lloc|habitatge|sanitat|"
    r"Govern|president|conseller|consellera|"
    r"non|moi|tamén|unha|unhas|dunha|nunha|cunha|algunha|algunhas|ningunha|"
    r"moito|moita|moitos|moitas|xa|xente|isto|aquilo|queiran|cousas|sanidade|"
    r"dugu|baina)\b|\bqu[èé]\b",
    re.I,
)

# 4. Anafora inicial: la frase empieza remitiendo a lo dicho antes ("Eso es...",
#    "Fueron esas politicas..."). Sin la frase anterior no se sabe de que habla, y el
#    jugador rellena el hueco a su manera: el fallo mediria el contexto que falta, no
#    el eje. Anadido el 2026-10-05; los sujetos implicitos ("No son un grupo mas...") no
#    caben en una regla de texto sin quitar frases buenas y quedan para el aviso de
#    "fuera de contexto" y la criba con jugadores.
_ANAFORA = re.compile(
    r"^[¿¡\"“]*(?:Y |Pero |Porque |Pues |Por eso,? )?(Eso|Esto|Ello)\b|"
    r"^[¿¡\"“]*(?:Y |Pero )?(?:\w+ )?(?:fueron |son |eran |es |fue )?(esas|estas|esos|estos|dichas|dichos|tales)\s+"
    r"(políticas|medidas|leyes|propuestas|reformas|decisiones|cifras|personas|familias|ayudas|normas|datos)\b",
    re.I,
)

# 5. Continuacion de lo anterior (anadido 2026-10-05, catalogo 2): la frase arranca
#    enlazando con algo que no esta en ella ("Lo hizo con...", "A esto se suma...",
#    "Frente a esto...", "Esta la han hecho...") o es un punto de una enumeracion
#    ("Y, quinto, ...", "La primera fue..."). Salieron de leer a ciegas las 150 frases
#    del catalogo 1: 40 dependian del contexto.
_CONTINUACION = re.compile(
    r"^[¿¡\"“]*(?:Y,? |Pero |E )?(?:"
    r"Lo (?:hizo|hicieron|hace|hacen|hac[ií]a|har[aá]n?)\b|"
    r"(?:A|Frente a|Ante) (?:esto|ello|eso)\b|"
    r"De ah[ií]\b|De (?:este|ese) modo\b|De (?:esta|esa) (?:manera|forma)\b|Es m[aá]s\b|Dicho esto\b|"
    r"Por cambiar de tema\b|En (?:primer|segundo|tercer|[uú]ltimo) lugar\b|"
    r"(?:Primero|Segundo|Tercero|Cuarto|Quinto|Sexto),|"
    r"(?:La|El) (?:primera|primero|segunda|segundo|tercera|tercero)\b|"
    r"(?:Esta|Este|Esa|Ese|Estas|Estos|Esas|Esos) (?:la|lo|las|los|le|les|es|son|fue|ha|han)\b)",
    re.I,
)
# 6. Texto roto: dos frases pegadas por un punto sin espacio ("autonomica.Aqui") o
#    cortada con puntos suspensivos al final.
_ROTA = re.compile(r"[a-záéíóúñ0-9]\.[A-ZÁÉÍÓÚÑ¿¡]|(?:\.\.\.|…)\s*$")

# Saneamiento: acotaciones del taquigrafo entre parentesis.
_ACOTACION = re.compile(r"\s*\([^)]*\)")
# Saneamiento: palabras pegadas por el parseo del PDF ("fondos comoAlquiler").
_PEGADA = re.compile(r"([a-záéíóúñ])([A-ZÁÉÍÓÚÑ])")
# Otras formas de pegado que el cotejo con el PDF destapo el 2026-10-04: signo sin
# espacio entre letras ("medios,enbases"), sigla pegada a la palabra siguiente
# ("IVAsupone") y tramos sin ningun espacio ("entonceslosdesahucios").
_PEGADA_OTRA = re.compile(
    r"[a-záéíóúñ][,;:][a-záéíóúñ]|\b[A-ZÁÉÍÓÚÑ]{2,}[a-záéíóúñ]{3,}|[a-záéíóúñ]{23,}"
)


def sanear(texto):
    """Limpia los defectos de parseo del PDF sin alterar el contenido."""
    if not texto:
        return ""
    t = _ACOTACION.sub("", texto)
    t = _PEGADA.sub(r"\1 \2", t)
    return re.sub(r"\s+", " ", t).strip()


def tiene_pegada(texto):
    """True si el parseo dejo palabras unidas. Se descarta en vez de adivinar
    donde iba el espacio: una frase mal reconstruida ya no es la que se dijo."""
    return bool(_PEGADA.search(texto or "") or _PEGADA_OTRA.search(texto or ""))


def lado(grupo):
    """Bloque del grupo, o None si queda fuera del catalogo inicial."""
    if grupo in DERECHA:
        return "DER"
    if grupo in IZQUIERDA:
        return "IZQ"
    return None


def es_candidata(frase, patron_tema):
    """Aplica el filtro formal completo a una frase ya saneada."""
    if not (LONGITUD_MIN <= len(frase) <= LONGITUD_MAX):
        return False
    if not re.search(patron_tema, frase, re.I):
        return False
    if _AUTODELATA.search(frase):
        return False
    if _CITA.search(frase):
        return False
    if _NO_CASTELLANO.search(frase):
        return False
    if _ANAFORA.search(frase):
        return False
    if _CONTINUACION.search(frase) or _ROTA.search(frase):
        return False
    return True


def frases_de(texto):
    """Parte una intervencion en frases. El corpus trae discursos enteros: la
    mediana es de 240 caracteres pero el maximo pasa de 85.000."""
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", texto or "")]


def id_frase(ds, orador, frase):
    """Identificador estable de una candidata. Sale del contenido y de la fuente,
    no del orden de lectura, para que clasificacion, revision y catalogo se puedan
    cruzar aunque el corpus crezca."""
    clave = f"{ds}|{orador}|{frase}".encode("utf-8")
    return hashlib.sha1(clave).hexdigest()[:12]


def candidatas_de_sesion(sesion, temas=None):
    """Extrae las candidatas de una sesion ya cargada como dict.

    Descarta las sesiones sin fecha: sin fecha no hay fuente citable, y una
    frase sin fuente verificable no entra al catalogo.
    """
    temas = temas or TEMAS
    if not sesion.get("fecha"):
        return []
    salida = []
    for iv in sesion.get("intervenciones", []):
        bloque = lado(iv.get("grupo"))
        if not bloque:
            continue
        crudo = iv.get("texto") or ""
        for tema, patron in temas.items():
            if not re.search(patron, crudo, re.I):
                continue
            for frase in frases_de(crudo):
                if tiene_pegada(frase):
                    continue
                limpia = sanear(frase)
                if not es_candidata(limpia, patron):
                    continue
                salida.append(
                    {
                        "id": id_frase(sesion.get("id"), iv.get("orador"), limpia),
                        "tema": tema,
                        "bloque": bloque,
                        "grupo": iv.get("grupo"),
                        "orador": iv.get("orador"),
                        "fecha": sesion["fecha"],
                        "ds": sesion.get("id"),
                        "pdf": sesion.get("ds"),
                        "frase": limpia,
                    }
                )
    return salida
