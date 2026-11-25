"""Vías Seguras Bogotá: puntos críticos de siniestralidad vial con datos abiertos de la SDM."""
import os

import solara

from logica import ACTORES, TODAS, VIAS, cargar, filtrar, localidades, mas_peligroso, por_localidad, ranking, resumen

# Configuración: viene del entorno, no del código.
NOMBRE = os.environ.get("NOMBRE_APP", "Vías Seguras Bogotá")
CLAVE_ADMIN = os.environ.get("CLAVE_ADMIN", "")  # secreto: nunca escriba su valor aquí

NECESIDAD = (
    "Para peatones, ciclistas y motociclistas de Bogotá, y para quien planea rutas escolares o de trabajo: "
    "**¿cuáles son los cruces donde más personas mueren o resultan heridas en siniestros viales, y en qué "
    "localidades están?**"
)
FUENTE = (
    "Datos abiertos: Puntos Críticos de Siniestralidad en vías arteriales y locales (2022-2025), "
    "[Secretaría Distrital de Movilidad de Bogotá](https://datos.movilidadbogota.gov.co), servicio "
    "[SIMUR DatosAbiertos](https://sig.simur.gov.co/arcgis/rest/services/DatosAbiertos). "
    "Licencia [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). "
    "Cada punto suma los fallecidos y lesionados registrados entre 2022 y 2025."
)

PLURAL = {"Arterial": "arteriales", "Local": "locales"}

puntos = cargar()
actor = solara.reactive(ACTORES[0])
via = solara.reactive(VIAS[0])
localidad = solara.reactive(TODAS)
clave = solara.reactive("")


@solara.component
def Page():
    solara.Title(NOMBRE)
    solara.Markdown(f"# {NOMBRE}\n\n{NECESIDAD}")

    opciones = localidades(puntos, actor.value, via.value)

    def cambiar_actor(nuevo):
        actor.value = nuevo
        localidad.value = TODAS  # la lista de localidades cambia con el actor

    def cambiar_via(nueva):
        via.value = nueva
        localidad.value = TODAS

    with solara.Row():
        solara.Select(label="Actor vial", value=actor.value, values=ACTORES, on_value=cambiar_actor)
        solara.Select(label="Tipo de vía", value=via.value, values=VIAS, on_value=cambiar_via)
        solara.Select(label="Localidad", value=localidad, values=opciones)

    datos = filtrar(puntos, actor.value, via.value, localidad.value)
    total = resumen(datos)
    peor = mas_peligroso(datos)
    solara.Markdown(
        f"### {actor.value} · vías {PLURAL[via.value]} · {localidad.value}\n\n"
        f"- **Puntos críticos:** {total['puntos']}\n"
        f"- **Fallecidos en esos puntos:** {total['fallecidos']}\n"
        f"- **Lesionados en esos puntos:** {total['lesionados']}\n"
        + (f"- **Punto más peligroso:** {peor['direccion']} ({peor['localidad']}): "
           f"{peor['fallecidos']} fallecidos y {peor['lesionados']} lesionados\n" if peor else "")
    )
    solara.DataFrame(ranking(datos), items_per_page=15)

    if via.value == "Local":
        solara.Markdown(f"### Por localidad · {actor.value}")
        solara.DataFrame(por_localidad(puntos, actor.value, via.value), items_per_page=20)
    else:
        solara.Markdown("_La fuente no trae localidad para los puntos de vías arteriales._")

    # Vista privada: códigos y coordenadas de cada punto, para el equipo técnico.
    solara.InputText("Clave de administración (presione Enter)", value=clave, password=True)
    if CLAVE_ADMIN and clave.value == CLAVE_ADMIN:
        solara.Markdown("**Vista técnica:** código del punto y coordenadas (WGS84)")
        solara.DataFrame(datos[["id", "direccion", "localidad", "lat", "lon", "capa"]], items_per_page=15)

    solara.Markdown(FUENTE)
