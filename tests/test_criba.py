"""Tests del criterio 11: los bordes del umbral fijado antes de tener datos."""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import catalogo
import criba


def respuestas(frase, aciertos, total, ms=2000, prefijo="s"):
    return [
        {"sesion_juego": f"{prefijo}{frase}{i}", "frase_id": frase, "acierto": int(i < aciertos),
         "confianza": 2, "ms_reaccion": ms}
        for i in range(total)
    ]


def test_14_respuestas_no_bastan_aunque_acierten_todas():
    retiradas, _ = criba.criba(respuestas("a", 14, 14))
    assert retiradas == []


def test_13_de_15_sale_y_12_de_15_se_queda():
    retiradas, _ = criba.criba(respuestas("a", 13, 15) + respuestas("b", 12, 15))
    assert [r["frase_id"] for r in retiradas] == ["a"]
    assert retiradas[0]["tasa"] == round(13 / 15, 3)


def test_partidas_de_reflejo_no_cuentan():
    # 15 respuestas acertadas, pero 5 de partidas con tiempos imposibles: quedan 10.
    filas = respuestas("a", 10, 10) + respuestas("a", 5, 5, ms=150, prefijo="bot")
    retiradas, descartadas = criba.criba(filas)
    assert retiradas == [] and descartadas == 5


def test_catalogo_final_salta_las_retiradas_y_tira_de_reservas():
    cands = [{"id": str(i), "tema": t, "bloque": b, "orden": str(i)}
             for t in catalogo.TEMAS for b in catalogo.BLOQUES for i in (1, 2, 3)]
    conf = {(c["id"], c["tema"]): {"tema_ok": True, "postura": True} for c in cands}
    fin = catalogo.final(cands, conf, {}, 2, excluir={"1"})
    assert {c["id"] for c in fin} == {"2", "3"}
