# Vías Seguras Bogotá — puntos críticos de siniestralidad vial (2022-2025)
- URL pública: https://vias-seguras-moises.onrender.com
- Repositorio: https://github.com/Clydex-hub/vias-seguras-bogota
- Correr: `docker build -t vias-seguras . && docker run --rm -p 8765:8765 --env-file .env vias-seguras` y abrir http://localhost:8765
- Datos: Puntos Críticos de Siniestralidad 2022-2025, Secretaría Distrital de Movilidad (SIMUR, datos.movilidadbogota.gov.co), licencia CC BY 4.0, en `datos/puntos_criticos_siniestralidad_2022_2025.csv`
- Variables: `NOMBRE_APP`, `CLAVE_ADMIN` (se configuran en Render; copie `.env.example` como `.env` para correrla local)
