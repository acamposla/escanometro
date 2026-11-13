"""Pruebas de los filtros, con los casos borde que aparecieron al medir el
corpus real el 2026-09-29. Cada test corresponde a un fallo observado, no a un
supuesto."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import filtros  # noqa: E402

VIVIENDA = filtros.TEMAS["vivienda"]


def test_pasa_una_frase_valida():
    frase = (
        "En España tenemos únicamente el 2,5% de vivienda pública frente al 9,3 "
        "de media en la Unión Europea, 7 puntos por debajo"
    )
    assert filtros.es_candidata(frase, VIVIENDA)


def test_descarta_autodelacion_por_grupo():
    # Caso real: decia "Grupo Popular", que el filtro inicial no cubria.
    frase = (
        "Hoy el Grupo Popular nos trae una propuesta para desbloquear suelo con "
        "el argumento de facilitar el acceso a la vivienda asequible"
    )
    assert not filtros.es_candidata(frase, VIVIENDA)


def test_descarta_cita_de_terceros():
    # Sin esto el corpus atribuye la frase a quien la lee en voz alta.
    frase = (
        "Ellos mismos dijeron que la vivienda no es un mercado sino un derecho "
        "constitucional que hay que garantizar por ley"
    )
    assert not filtros.es_candidata(frase, VIVIENDA)


def test_descarta_lengua_cooficial():
    frase = (
        "No és un Excel, no és una reestructuració, és la hipoteca, és la salut "
        "mental, és el torn de nit, és el pa a la taula"
    )
    assert not filtros.es_candidata(frase, VIVIENDA)


def test_descarta_por_longitud():
    assert not filtros.es_candidata("Vivienda pública ya", VIVIENDA)
    assert not filtros.es_candidata("vivienda " * 40, VIVIENDA)


def test_descarta_frase_sin_el_tema():
    frase = (
        "La transición energética necesita una planificación industrial seria y "
        "un calendario que las empresas puedan cumplir sin sobresaltos"
    )
    assert not filtros.es_candidata(frase, VIVIENDA)


def test_sanea_acotacion_del_taquigrafo():
    crudo = "Si quiere que hablemos de vivienda, aquí lo tiene (muestra un documento), por separado"
    assert "(" not in filtros.sanear(crudo)
    assert "muestra" not in filtros.sanear(crudo)


def test_detecta_palabra_pegada():
    # Caso real: "fondos comoAlquiler Seguro".
    assert filtros.tiene_pegada("las empresas y fondos comoAlquiler Seguro")
    assert not filtros.tiene_pegada("las empresas y fondos como Alquiler Seguro")


def test_lado_solo_reconoce_los_cuatro_estatales():
    assert filtros.lado("PP") == "DER"
    assert filtros.lado("SUMAR") == "IZQ"
    for fuera in ("JUNTS", "PNV", "ERC", "BILDU", "MESA", "GOB", "COMP", None):
        assert filtros.lado(fuera) is None


def test_sesion_sin_fecha_no_produce_candidatas():
    sesion = {
        "id": "DSCD-15-PL-161",
        "fecha": None,
        "intervenciones": [
            {
                "grupo": "PP",
                "orador": "X",
                "texto": (
                    "El acceso a la vivienda se ha convertido en un drama y no hay "
                    "una política estructural que lo aborde con seriedad."
                ),
            }
        ],
    }
    assert filtros.candidatas_de_sesion(sesion) == []


def test_sesion_valida_produce_candidata_con_fuente():
    sesion = {
        "id": "DSCD-15-CO-127",
        "fecha": "2024-06-18",
        "ds": "https://www.congreso.es/public_oficiales/L15/CONG/DS/CO/DSCD-15-CO-127.PDF",
        "intervenciones": [
            {
                "grupo": "PP",
                "orador": "Mesquida Mayans",
                "texto": (
                    "Más datos: en España tenemos únicamente el 2,5% de vivienda "
                    "pública frente al 9,3 de media en la Unión Europea, 7 puntos "
                    "por debajo."
                ),
            }
        ],
    }
    out = filtros.candidatas_de_sesion(sesion)
    assert len(out) == 1
    assert out[0]["bloque"] == "DER"
    assert out[0]["tema"] == "vivienda"
    assert out[0]["ds"] == "DSCD-15-CO-127"
    assert out[0]["pdf"].endswith(".PDF")


def test_ministerio_y_lideres_delatan():
    # Observado el 2026-10-04: "ministr" no atrapaba "Ministerio", y los nombres de
    # lideres delatan igual que las siglas.
    patron = filtros.TEMAS["sanidad"]
    assert not filtros.es_candidata("Nada de nada; cuestión a la que nos tiene acostumbradas el Ministerio de Sanidad.", patron)
    assert not filtros.es_candidata("Desde que Sánchez llegó, la sanidad pública ha perdido miles de profesionales en toda España.", patron)
    assert not filtros.es_candidata("La sanidad que Ayuso está desmantelando cada día es la que pagan todos los madrileños con sus impuestos.", patron)


def test_gallego_y_valenciano_fuera():
    # Observado el 2026-10-04 en el catalogo provisional.
    assert not filtros.es_candidata(
        "Reclamen o que queiran pero é unha carteira que está posta, pois, en fin, case desde o ano 86, da Lei Xeral de Sanidade.",
        filtros.TEMAS["sanidad"])
    assert not filtros.es_candidata(
        "Hui venim a parlar de sanitat, de serveis socials, de pensions, d’habitatge, però també d’educació.",
        filtros.TEMAS["pensiones"])


def test_castellano_con_palabras_parecidas_sigue_entrando():
    # Control: "ya", "uno", "mucho" no son gallego; "lo" y "la" no son elisiones.
    assert filtros.es_candidata(
        "La lista de espera ya supera los seis meses en muchos hospitales de provincias y nadie da explicaciones.",
        filtros.TEMAS["sanidad"])


def test_toponimo_catalan_no_es_otra_lengua():
    # Falso positivo observado al ampliar el filtro: "L'Hospitalet" en una frase en castellano.
    assert not filtros._NO_CASTELLANO.search(
        "¿Acaso Barcelona, L’Hospitalet, Badalona y Sant Adrià no tienen sus propias comisarías de Policía Nacional?")


def test_personas_politicas_y_siglas_regionales_delatan():
    # Observado el 2026-10-04: nombres de lideres autonomicos y expresidentes, citados
    # casi siempre desde un solo bloque.
    p = filtros.TEMAS["pensiones"]
    assert not filtros.es_candidata("Fíjense, con Rajoy, la mayoría de las personas autónomas cotizaban por la base mínima de pensión.", p)
    assert not filtros.es_candidata("Cuando Moreno Bonilla era secretario de Estado suprimió el derecho a la cotización de los cuidadores.", p)
    assert not filtros.es_candidata("Eso de la ley de vivienda de Bildu y de Esquerra pasará a los anales de la autonomía de Cataluña.", filtros.TEMAS["vivienda"])


def test_govern_y_president_son_catalan():
    assert not filtros.es_candidata(
        "Estamos contentos, estamos orgullosos de un Govern valiente y preocupado por la solución y estamos orgullosos del president Illa por haber aplicado la ley de vivienda.",
        filtros.TEMAS["vivienda"])


def test_presidente_y_montoro_no_son_falsos_positivos():
    # Control: "presidente" (castellano) y "Montoro" no deben confundirse con "president" ni "Montero".
    assert not filtros._NO_CASTELLANO.search("El presidente de la comunidad habló de las listas de espera.")
    assert not filtros._AUTODELATA.search("Con Montoro la pensión media era más baja.")


def test_pegados_que_destapo_el_cotejo():
    assert filtros.tiene_pegada("especialmente en salariosmedios,enbasesdecotización y en pensiones")
    assert filtros.tiene_pegada("Menos recaudación por IVAsupone menos recursos para financiar la sanidad")
    assert filtros.tiene_pegada("¿No son constitucionales entonceslosdesahuciosylosdespidos?")


def test_castellano_normal_no_es_pegado():
    # Controles: decimales, siglas en plural, palabras largas reales y tras signo con espacio.
    for t in ("para pasar del 3,4 al 8 por ciento", "los ERTEs salvaron empleo", "la internacionalización de la sanidad",
              "la anticonstitucionalidad, dijo, es evidente", "IVA: el impuesto"):
        assert not filtros.tiene_pegada(t), t


def test_anafora_inicial_fuera():
    # Observado el 2026-10-05: frases que solo se entienden con la anterior.
    p = filtros.TEMAS["pensiones"]
    assert not filtros.es_candidata("Eso es trabajar por la sostenibilidad de las pensiones, eso es trabajar por los españoles.", p)
    assert not filtros.es_candidata("Fueron esas políticas las que nos llevaron a recortar las pensiones de millones de jubilados.", p)


def test_frase_autocontenida_con_eso_dentro_sigue():
    # Control: "eso" en mitad de la frase no la hace dependiente del contexto.
    assert filtros.es_candidata(
        "Las pensiones mínimas suben un 9% y eso permite a millones de jubilados llegar mejor a fin de mes.",
        filtros.TEMAS["pensiones"])


# Catalogo 2 (2026-10-05): reglas sacadas de leer a ciegas las 150 frases del catalogo 1.
TEMA = r"vivienda|pensi|sanid|alquiler|sanitari"


def test_continuacion_de_lo_anterior_no_entra():
    for frase in [
        "Lo hizo con la reforma laboral, con la ley de vivienda, con la subida de las pensiones, con la subida de los salarios.",
        "A esto se le suma la crisis de la vivienda, señalada también por Cáritas, como uno de los mayores problemas sociales actuales.",
        "Frente a esto, tenemos la obligación de implementar mecanismos que impidan subir el precio del alquiler.",
        "Esta la han hecho para bajar los precios de los alquileres y los están disparando, reduciendo la oferta de vivienda.",
        "Y, quinto, conocer y utilizar recursos comunitarios tanto dentro como fuera del sistema sanitario.",
        "La primera fue la de los recortes: cada vez que se actuó en el sistema público de pensiones fue para recortar.",
        "Primero, que el deterioro de la natalidad ha sido muy superior al esperado y agrava la sostenibilidad de las pensiones.",
    ]:
        assert not filtros.es_candidata(frase, TEMA), frase


def test_texto_roto_y_citas_oidas_no_entran():
    for frase in [
        "Esa petrificación se impone sobre viviendas de protección estatal y autonómica.Aquí es donde está el problema.",
        "Esta Cámara tiene la posibilidad de regular el alquiler indefinido, de regular el alquiler de temporada y de habitaciones…",
        "Y lo mejor es que dicen que los fondos buitre extranjeros son peligrosos para la compra de vivienda.",
        "Por eso, nosotras nos esforzamos en hacer políticas que pretenden limitar la subida de los precios de la vivienda.",
    ]:
        assert not filtros.es_candidata(frase, TEMA), frase


def test_control_frases_buenas_siguen_entrando():
    # Que las reglas nuevas no se coman frases que se entienden solas.
    for frase in [
        "Así que hay que pagar impuestos, porque con esto se financia la sanidad pública.",
        "Esta Cámara tiene ahora mismo la posibilidad de regular el alquiler de temporada y de habitaciones.",
        "Primero la vivienda pública y después todo lo demás: sin techo no hay proyecto de vida.",
        "Necesitamos políticas de vivienda valientes que hoy por hoy no estamos teniendo.",
        "Un sistema público de pensiones fuerte convierte el crecimiento económico en seguridad vital.",
        "Estos años de alquileres disparados han expulsado a los jóvenes de los barrios donde crecieron.",
    ]:
        assert filtros.es_candidata(frase, TEMA), frase
