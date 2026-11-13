"""Catalogo 2: filtro de calidad con jueces y cifras agrupadas (2026-10-05)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "scripts"))

import catalogo  # noqa: E402
import exportar_catalogo  # noqa: E402


def test_agrupar_cifras_como_el_diario_de_sesiones():
    f = exportar_catalogo.agrupar_cifras
    assert f("van a costar 346000 euros") == "van a costar 346 000 euros"
    assert f("son 1196000.") == "son 1 196 000."
    assert f("en 2025 y 8771 personas") == "en 2025 y 8771 personas"  # cuatro cifras, sin tocar
    assert f("el 12,9% y 3,4 al 8") == "el 12,9% y 3,4 al 8"


def test_apta_exige_todos_los_jueces():
    k = ("a1", "vivienda")
    bien = {k: {"entiende": True, "afirma": True, "delata": False}}
    mal = {k: {"entiende": True, "afirma": False, "delata": False}}
    assert catalogo.apta([bien, bien], k)
    assert not catalogo.apta([bien, mal], k)
    assert not catalogo.apta([bien, {}], k)  # sin veredicto de un juez, no entra
    assert catalogo.apta([], k)  # sin jueces, el filtro no se aplica (catalogo 1)
