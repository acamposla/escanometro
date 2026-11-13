"""Tests del cotejo con el PDF: que encuentre lo que esta y, sobre todo, que no
de por bueno lo que no esta."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import cotejar

TEXTO = """El señor GARCÍA LÓPEZ: Gracias, presidenta.
La sanidad pública no puede depen-
der de conciertos con empresas privadas.
La señora PRESIDENTA: Silencio, por favor.
Y lo repetiré las veces que haga falta.
El señor DE OLANO VELA: Otra frase distinta sobre vivienda.
"""


def fila(frase, orador):
    return {"frase": frase, "orador": orador}


def test_encuentra_con_corte_de_linea_y_salta_presidencia():
    r = cotejar.cotejar(fila("La sanidad pública no puede depender de conciertos con empresas privadas.", "García López"), TEXTO)
    assert r == {"encontrada": 1, "orador_pdf": "GARCÍA LÓPEZ", "orador_ok": 1}
    r = cotejar.cotejar(fila("Y lo repetiré las veces que haga falta.", "García López"), TEXTO)
    assert r["orador_ok"] == 1


def test_frase_que_no_esta_no_se_encuentra():
    r = cotejar.cotejar(fila("La sanidad pública debe depender de conciertos.", "García López"), TEXTO)
    assert r["encontrada"] == 0


def test_orador_equivocado_no_pasa():
    r = cotejar.cotejar(fila("Otra frase distinta sobre vivienda.", "García López"), TEXTO)
    assert r["encontrada"] == 1 and r["orador_ok"] == 0


def test_particula_de_no_basta_para_coincidir():
    assert not cotejar.coincide_orador("De Olano Vela", "DE LA FUENTE")
    assert cotejar.coincide_orador("De Olano Vela", "DE OLANO VELA")


def test_numero_con_espacio_de_millares_y_acotacion():
    texto = "El señor PÉREZ GIL: Asciende a 28 394 millones, son la base de nuestras ciudades (aplausos), de nuestros pueblos."
    r = cotejar.cotejar(fila("Asciende a 28394 millones, son la base de nuestras ciudades, de nuestros pueblos.", "Pérez Gil"), texto)
    assert r == {"encontrada": 1, "orador_pdf": "PÉREZ GIL", "orador_ok": 1}


def test_cabecera_con_acento_catalan():
    texto = "El señor HOCES ÍÑIGUEZ: Otra cosa.\nEl señor SARRIÀ MORELL: Fueron esas políticas las que nos llevaron a la burbuja."
    r = cotejar.cotejar(fila("Fueron esas políticas las que nos llevaron a la burbuja.", "Sarrià Morell"), texto)
    assert r["orador_pdf"] == "SARRIÀ MORELL" and r["orador_ok"] == 1


def test_numero_distinto_sigue_sin_encontrarse():
    # Control: tolerar el espacio de millares no puede volver iguales dos cifras distintas.
    r = cotejar.cotejar(fila("Asciende a 28395 millones.", "Pérez Gil"), "El señor PÉREZ GIL: Asciende a 28 394 millones.")
    assert r["encontrada"] == 0
