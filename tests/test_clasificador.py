"""Tests del clasificador, la muestra de revision y la comparacion.

Cada test cubre un fallo que falsearia la medicion sin hacer ruido.
"""

import collections
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import clasificar
import comparar
import filtros
import muestra_revision

LOTE = [
    {"id": "a", "tema": "sanidad", "frase": "Las listas de espera crecen.", "grupo": "PP", "orador": "X"},
    {"id": "b", "tema": "vivienda", "frase": "El alquiler sube.", "grupo": "PSOE", "orador": "Y"},
]


def test_id_estable_y_dependiente_de_la_fuente():
    assert filtros.id_frase("DS1", "X", "frase") == filtros.id_frase("DS1", "X", "frase")
    assert filtros.id_frase("DS1", "X", "frase") != filtros.id_frase("DS2", "X", "frase")


def test_el_modelo_no_ve_grupo_ni_orador():
    texto = clasificar.renderizar("PROMPT", LOTE)
    assert "PP" not in texto and "PSOE" not in texto
    assert "X" not in texto.split("PROMPT", 1)[1]
    assert "1. [sanidad] Las listas de espera crecen." in texto


def test_parsear_tolera_razonamiento_y_texto_alrededor():
    crudo = '<think>{"resultados": []}</think>Aqui va: {"resultados": [{"n": 1, "tema": true, "postura": false}]} fin'
    assert clasificar.parsear(crudo, 2) == {1: (True, False)}


def test_parsear_descarta_lo_que_no_es_booleano_ni_posicion_valida():
    crudo = '{"resultados": [{"n": 1, "tema": "si", "postura": true}, {"n": 3, "tema": true, "postura": true}]}'
    assert clasificar.parsear(crudo, 2) == {}


def test_parsear_json_roto_devuelve_vacio():
    assert clasificar.parsear('{"resultados": [{"n": 1,', 2) == {}


def test_lo_que_falta_se_reintenta_y_no_se_toma_por_veredicto():
    llamadas = []

    def falsa(contenido):
        llamadas.append(contenido)
        if len(llamadas) == 1:
            return '{"resultados": [{"n": 1, "tema": true, "postura": true}]}'
        return '{"resultados": [{"n": 1, "tema": false, "postura": false}]}'

    inc = collections.Counter()
    res = clasificar.clasificar_lote(LOTE, "P", falsa, inc)
    assert res == {("a", "sanidad"): (True, True), ("b", "vivienda"): (False, False)}
    assert len(llamadas) == 2
    assert inc["parcial"] == 1 and inc["recuperada"] == 1


def test_sin_respuesta_no_se_escribe():
    inc = collections.Counter()
    res = clasificar.clasificar_lote(LOTE, "P", lambda c: "no puedo", inc)
    assert res == {}
    assert inc["sin_respuesta"] == 2


def test_muestra_equilibrada_y_repetible():
    filas = [{"id": str(i), "bloque": "DER" if i % 3 else "IZQ", "tema": "t", "frase": "f"} for i in range(60)]
    a = muestra_revision.muestra_equilibrada(filas, 10, 1)
    b = muestra_revision.muestra_equilibrada(filas, 10, 1)
    assert [f["id"] for f in a] == [f["id"] for f in b]
    assert sum(f["bloque"] == "DER" for f in a) == 5


def test_hoja_ciega_no_lleva_fuente():
    fila = {"id": "a", "tema": "t", "frase": "f", "bloque": "DER", "grupo": "PP", "orador": "X"}
    hoja = muestra_revision.hoja_ciega([fila])[0]
    assert set(hoja) == {"id", "tema", "frase", "tema_ok", "postura"}


def test_kappa_descuenta_el_azar():
    # Un modelo que dice siempre "si" acierta el 80% cuando el 80% es "si", pero no sabe nada.
    pares = [(True, True)] * 8 + [(False, True)] * 2
    m = comparar.metricas(pares)
    assert m["acuerdo"] == 0.8
    assert m["kappa"] == 0
    assert m["deja_pasar"] == 2 and m["descarta"] == 0


def test_revision_con_duda_cuenta_su_valor_y_se_marca(tmp_path):
    ruta = tmp_path / "rev.csv"
    ruta.write_text("id,tema,frase,tema_ok,postura\na,t,f,1,1?\nb,t,f,1,0\nc,t,f,1,\n", encoding="utf-8")
    humano, dudas, _ = comparar.leer_revision(str(ruta))
    assert humano == {"a": {"tema_ok": True, "postura": True}, "b": {"tema_ok": True, "postura": False}}
    assert dudas == {"a"}


def test_misma_frase_en_dos_temas_son_dos_resultados():
    fila = {"id": "a", "frase": "Las pensiones y la sanidad publica se defienden."}
    lote = [dict(fila, tema="pensiones"), dict(fila, tema="sanidad")]
    respuesta = '{"resultados": [{"n": 1, "tema": true, "postura": true}, {"n": 2, "tema": false, "postura": true}]}'
    res = clasificar.clasificar_lote(lote, "P", lambda c: respuesta, collections.Counter())
    assert res == {("a", "pensiones"): (True, True), ("a", "sanidad"): (False, True)}


def test_v3_pide_y_exige_rol():
    assert clasificar.campos_de('{"rol": true}') == ("tema", "postura", "rol")
    sin_rol = '{"resultados": [{"n": 1, "tema": true, "postura": true}]}'
    con_rol = '{"resultados": [{"n": 1, "tema": true, "postura": true, "rol": false}]}'
    campos = ("tema", "postura", "rol")
    assert clasificar.parsear(sin_rol, 1, campos) == {}
    assert clasificar.parsear(con_rol, 1, campos) == {1: (True, True, False)}


def test_revision_sin_columna_rol_sigue_valiendo(tmp_path):
    ruta = tmp_path / "rev.csv"
    ruta.write_text("id,tema,frase,tema_ok,postura\na,t,f,1,0\n", encoding="utf-8")
    humano, _, _ = comparar.leer_revision(str(ruta))
    assert humano == {"a": {"tema_ok": True, "postura": False}}


def test_main_de_punta_a_punta(tmp_path, monkeypatch):
    entrada = tmp_path / "e.csv"
    entrada.write_text("id,tema,frase\na,sanidad,Las listas de espera crecen.\n", encoding="utf-8")
    prompt = tmp_path / "p_v9.txt"
    prompt.write_text('PROMPT "rol"', encoding="utf-8")
    respuesta = '{"resultados": [{"n": 1, "tema": true, "postura": true, "rol": false}]}'
    monkeypatch.setattr(clasificar, "llamar", lambda *a, **k: respuesta)
    monkeypatch.setenv("LITELLM_API_KEY", "x")
    monkeypatch.setattr(sys, "argv", ["c", "--entrada", str(entrada), "--modelo", "m",
                                      "--prompt", str(prompt), "--dir", str(tmp_path)])
    clasificar.main()
    import json
    registro = json.loads((tmp_path / "m__p_v9.jsonl").read_text())
    assert registro["id"] == "a" and registro["tema"] == "sanidad"
    assert (registro["tema_ok"], registro["postura"], registro["rol"]) == (True, True, False)


def _pool_falso():
    import catalogo
    pool, clas = [], {}
    for tema in catalogo.TEMAS:
        for bloque in catalogo.BLOQUES:
            for k in range(6):
                f = {"id": f"{tema}{bloque}{k}", "tema": tema, "bloque": bloque, "frase": "x"}
                pool.append(f)
                clas[(f["id"], tema)] = {"tema_ok": True, "postura": k != 0}
    return pool, clas


def test_catalogo_candidatos_reproducible_y_solo_supervivientes():
    import catalogo
    pool, clas = _pool_falso()
    a = catalogo.candidatos(pool, clas, 2, 1, 7)
    b = catalogo.candidatos(pool, clas, 2, 1, 7)
    assert [x["id"] for x in a] == [x["id"] for x in b]
    assert len(a) == 18 and not any(x["id"].endswith("0") for x in a)


def test_catalogo_una_frase_no_entra_dos_veces():
    import catalogo
    pool, clas = _pool_falso()
    gemela = {"id": "pensionesDER1", "tema": "sanidad", "bloque": "DER", "frase": "x"}
    pool.append(gemela)
    clas[("pensionesDER1", "sanidad")] = {"tema_ok": True, "postura": True}
    ids = [x["id"] for x in catalogo.candidatos(pool, clas, 5, 0, 1)]
    assert len(ids) == len(set(ids))


def test_catalogo_final_tira_de_reservas_en_orden():
    import catalogo
    cands = [{"id": str(i), "tema": t, "bloque": b, "orden": str(i)}
             for t in catalogo.TEMAS for b in catalogo.BLOQUES for i in (1, 2, 3)]
    conf = {(c["id"], c["tema"]): {"tema_ok": True, "postura": c["id"] != "1"} for c in cands}
    fin = catalogo.final(cands, conf, {}, 2)
    assert {c["id"] for c in fin} == {"2", "3"} and len(fin) == 12


def test_exportar_catalogo_version_cambia_con_el_contenido():
    import exportar_catalogo
    filas = [{"id": "a", "tema": "t", "frase": "f", "bloque": "IZQ", "orden": "1"},
             {"id": "b", "tema": "t", "frase": "g", "bloque": "DER", "orden": "30"}]
    prov = exportar_catalogo.construir(filas, provisional=True)
    assert [f["id"] for f in prov["frases"]] == ["a"] and prov["version"].startswith("provisional-")
    v1 = exportar_catalogo.construir(filas)["version"]
    filas[0]["frase"] = "otra"
    assert exportar_catalogo.construir(filas)["version"] != v1


def test_timeout_de_socket_es_incidencia_no_caida():
    # En Python 3.9 socket.timeout no es TimeoutError: tumbaba el script entero.
    import socket

    def cuelga(contenido):
        raise socket.timeout("timed out")

    inc = collections.Counter()
    assert clasificar.clasificar_lote(LOTE, "P", cuelga, inc) == {}
    assert inc["transporte"] == 1 and inc["sin_respuesta"] == 2


def test_catalogo_quitar_una_frase_no_reordena_las_demas():
    import catalogo
    pool, clas = _pool_falso()
    antes = [x["id"] for x in catalogo.candidatos(pool, clas, 3, 2, 1)]
    quitada = antes[0]
    pool2 = [f for f in pool if f["id"] != quitada]
    despues = [x["id"] for x in catalogo.candidatos(pool2, clas, 3, 2, 1)]
    assert [i for i in antes if i != quitada] == [i for i in despues if i in antes]


def test_prompt_de_calidad_pide_sus_tres_campos():
    with open("prompts/calidad_v1.txt", encoding="utf-8") as fh:
        prompt = fh.read()
    assert clasificar.campos_de(prompt) == ("entiende", "afirma", "delata")
    texto = '{"resultados": [{"n": 1, "entiende": true, "afirma": false, "delata": false}, {"n": 2, "entiende": "si"}]}'
    assert clasificar.parsear(texto, 2, clasificar.campos_de(prompt)) == {1: (True, False, False)}
