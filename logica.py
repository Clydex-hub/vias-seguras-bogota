"""Reglas de la app, sin pantalla. Se prueban con pytest (tests/test_logica.py).

Datos: Puntos Críticos de Siniestralidad (2022-2025) de la Secretaría Distrital de
Movilidad de Bogotá (SIMUR), capas de vías arteriales y locales para peatones,
ciclistas, motociclistas y todos los usuarios vulnerables.
"""
import unicodedata
from pathlib import Path

import pandas as pd

DATOS = Path(__file__).parent / "datos" / "puntos_criticos_siniestralidad_2022_2025.csv"
TODAS = "Todas"
SIN_LOCALIDAD = "Sin localidad en la fuente"

ACTORES = ["Peatones", "Ciclistas", "Motociclistas", "Todos los vulnerables"]
VIAS = ["Arterial", "Local"]


def _sin_tildes(texto):
    return "".join(c for c in unicodedata.normalize("NFD", texto) if unicodedata.category(c) != "Mn").lower()


def cargar(ruta=DATOS):
    """Lee el CSV y unifica los nombres de localidad (la fuente trae 'Fontibon' y 'Fontibón')."""
    df = pd.read_csv(ruta)
    df["localidad"] = df["localidad"].fillna("").astype(str).str.strip()
    # Para cada nombre sin tildes, usamos la versión con tildes si la fuente la trae.
    canonico = {}
    for nombre in sorted(df["localidad"].unique(), key=lambda n: -sum(ord(c) > 127 for c in n)):
        canonico.setdefault(_sin_tildes(nombre), nombre)
    df["localidad"] = df["localidad"].map(lambda n: canonico[_sin_tildes(n)] if n else SIN_LOCALIDAD)
    df["fallecidos"] = df["fallecidos"].astype(int)
    df["lesionados"] = df["lesionados"].astype(int)
    return df


def localidades(df, actor, via):
    """Opciones del selector de localidad para un actor y tipo de vía."""
    datos = df[(df["actor"] == actor) & (df["via"] == via)]
    return [TODAS] + sorted(datos["localidad"].unique())


def filtrar(df, actor, via, localidad=TODAS):
    """Puntos críticos de un actor vial, en un tipo de vía y (opcional) una localidad."""
    datos = df[(df["actor"] == actor) & (df["via"] == via)]
    if localidad != TODAS:
        datos = datos[datos["localidad"] == localidad]
    return datos


def resumen(datos):
    """Cantidad de puntos, fallecidos y lesionados de un conjunto de puntos."""
    return {
        "puntos": int(len(datos)),
        "fallecidos": int(datos["fallecidos"].sum()),
        "lesionados": int(datos["lesionados"].sum()),
    }


def mas_peligroso(datos):
    """El punto con más fallecidos; si empatan, el de más lesionados. None si no hay puntos."""
    if datos.empty:
        return None
    fila = datos.sort_values(["fallecidos", "lesionados"], ascending=False).iloc[0]
    return {"direccion": fila["direccion"], "localidad": fila["localidad"],
            "fallecidos": int(fila["fallecidos"]), "lesionados": int(fila["lesionados"])}


def ranking(datos):
    """Tabla de puntos, del más peligroso al menos peligroso."""
    tabla = datos.sort_values(["fallecidos", "lesionados"], ascending=False)
    tabla = tabla[["direccion", "localidad", "fallecidos", "lesionados"]].rename(columns={
        "direccion": "Punto", "localidad": "Localidad",
        "fallecidos": "Fallecidos", "lesionados": "Lesionados"})
    return tabla.reset_index(drop=True)


def por_localidad(df, actor, via):
    """Puntos, fallecidos y lesionados por localidad, de mayor a menor número de lesionados."""
    datos = df[(df["actor"] == actor) & (df["via"] == via)]
    tabla = datos.groupby("localidad").agg(Puntos=("id", "count"), Fallecidos=("fallecidos", "sum"),
                                            Lesionados=("lesionados", "sum"))
    tabla = tabla.sort_values(["Lesionados", "Fallecidos"], ascending=False).reset_index()
    return tabla.rename(columns={"localidad": "Localidad"})
