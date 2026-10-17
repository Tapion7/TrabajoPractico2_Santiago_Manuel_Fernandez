# Datos del TP2 – Telemetría de Fórmula 1

* **Fuente / URL / procedimiento de obtención:** muestra controlada de 60 registros construida a partir de esquemas públicos de cronometraje de Fórmula 1 ([FastF1 Timing Data](https://docs.fastf1.dev/) / FIA Live Timing), adaptada para pruebas reproducibles en formatos equivalentes `data/vueltas.csv` y `data/vueltas.json`.
* **Responsable:** FIA Formula One World Championship / proyecto abierto FastF1 (muestra preparada para uso académico en la cátedra de Programación Orientada a Datos – UCA).
* **Licencia o condiciones de uso:** datos públicos de uso libre con fines educativos y de análisis no comercial (MIT / dominio público estadístico).
* **Fecha de consulta:** 17 de octubre de 2026.
* **Unidad de análisis:** cada fila representa una vuelta registrada por un piloto durante una sesión de carrera.
* **Variables utilizadas:**
  * `vuelta_id` (`str`): identificador único del registro con formato `V001` a `V060`.
  * `piloto` (`str`): código FIA de tres letras mayúsculas del piloto (`VER`, `NOR`, `LEC`, `COL`).
  * `numero_vuelta` (`int`): número de giro dentro de la sesión (entero positivo).
  * `tiempo_total` (`str`): duración total de la vuelta en formato `M:SS.mmm`.
  * `sector_1`, `sector_2`, `sector_3` (`float`): tiempos parciales de los tres sectores del circuito expresados en segundos.
  * `en_boxes` (`bool`): indica `True` si el piloto ingresó o salió de boxes en esa vuelta y `False` si fue una vuelta lanzada en pista limpia.
* **Limitaciones y sesgos:** la muestra abarca un tramo de carrera de cuatro pilotos (54 vueltas válidas y 6 registros con incidencias de prueba como paradas en boxes, datos faltantes, formatos inválidos o diferencias entre sectores). No desagrega el compuesto de neumático ni el efecto de la descarga de combustible vuelta a vuelta.
