"""Pruebas de las reglas de la app."""
import csv
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent))
from logica import DATOS, TODAS, cargar, filtrar, localidades, mas_peligroso, resumen  # noqa: E402


def caso():
    """Puntos inventados solo para probar las reglas (no son los datos de la app)."""
    return pd.DataFrame({
        "id": ["a", "b", "c"], "actor": ["Peatones"] * 3, "via": ["Local"] * 3,
        "direccion": ["Cl 1 x K 1", "Cl 2 x K 2", "Cl 3 x K 3"],
        "localidad": ["Bosa", "Bosa", "Suba"], "fallecidos": [1, 1, 0], "lesionados": [5, 9, 30],
    })


def test_resumen_suma_puntos_fallecidos_y_lesionados():
    assert resumen(filtrar(caso(), "Peatones", "Local", "Bosa")) == {"puntos": 2, "fallecidos": 2, "lesionados": 14}


def test_mas_peligroso_desempata_por_lesionados():
    assert mas_peligroso(caso())["direccion"] == "Cl 2 x K 2"


def test_localidades_unificadas_sin_duplicados_por_tildes():
    nombres = localidades(cargar(), "Todos los vulnerables", "Local")
    assert nombres[0] == TODAS
    assert "Fontibón" in nombres and "Fontibon" not in nombres


def test_cifra_de_control_por_otro_camino():
    """Cifra de control: lesionados en puntos críticos de vías arteriales (todos los vulnerables) = 1273.

    Se recalcula sin pandas, leyendo el CSV línea por línea, y se compara con la app.
    """
    with open(DATOS, encoding="utf-8", newline="") as archivo:
        total = sum(int(fila["lesionados"]) for fila in csv.DictReader(archivo)
                    if fila["actor"] == "Todos los vulnerables" and fila["via"] == "Arterial")
    app = resumen(filtrar(cargar(), "Todos los vulnerables", "Arterial"))["lesionados"]
    assert app == total == 1273
