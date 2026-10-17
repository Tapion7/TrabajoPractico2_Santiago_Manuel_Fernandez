# TP2 – Telemetría de Fórmula 1

**Autor:** Santiago Manuel Fernandez  
**Materia:** Programación Orientada a Datos – Licenciatura en Ciencia de Datos – UCA, 2026

## Pregunta guía

> ¿Qué piloto fue más consistente y cuál tuvo el mejor ritmo en una carrera de Fórmula 1, a partir de los tiempos de vuelta registrados?

Para responderla, el programa procesa los giros registrados en una carrera, convierte los tiempos a segundos, descarta vueltas no representativas (como entradas o salidas de boxes y registros con errores) y compara a los pilotos según su mejor vuelta, promedio, mediana y dispersión.

## Problema y usuario

* **Problema:** los registros de vueltas en bruto suelen traer tiempos como texto (`M:SS.mmm`), datos faltantes, vueltas lentas por paso por boxes o diferencias entre la suma de los sectores y el tiempo total. Además, mirar solo la vuelta rápida no alcanza para saber quién rindió mejor durante toda la carrera.
* **Usuario:** una persona aficionada a la F1 o estudiante de datos que quiera comparar el rendimiento entre pilotos de forma rápida y reproducible.
* **Resultado esperado e interpretación:** una tabla con el ranking de pilotos (`outputs/resumen_pilotos.csv`) y un archivo con las filas descartadas y su motivo (`outputs/rechazados.csv`). Un menor tiempo promedio o mediana indica mejor ritmo de carrera, mientras que un menor desvío estándar refleja mayor consistencia vuelta a vuelta.

## Alcance de la primera versión

Incluye:

* procesamiento de una carrera a partir de archivos locales equivalentes en CSV y JSON;
* validación de códigos de piloto, números de vuelta, tiempos y consistencia entre los tres sectores y el tiempo total;
* limpieza de registros inválidos y exclusión de vueltas con paso por boxes;
* generación del ranking de pilotos por ritmo y consistencia.

Queda fuera: análisis de degradación por compuesto de neumáticos, impacto del clima o auto de seguridad, telemetría curva a curva y comparación entre varias temporadas.

## Datos

* **Fuente y licencia:** muestra reproducible de tiempos de vuelta de Fórmula 1 (basada en registros públicos de cronometraje FIA / FastF1, uso público académico, consultada en octubre de 2026).
* **Unidad de análisis:** cada fila representa una vuelta registrada por un piloto en una sesión de carrera.
* **Variables principales:** `vuelta_id` (identificador `V001`), `piloto` (código de 3 letras, ej. `VER`, `NOR`, `LEC`, `COL`), `numero_vuelta`, `tiempo_total` (`M:SS.mmm`), `sector_1`, `sector_2`, `sector_3` (en segundos) y `en_boxes` (`True`/`False`).

El detalle completo se encuentra en `data/README.md`.

## Requisitos e instalación

Se requiere Python 3.10 o superior. Para instalar las dependencias:

    pip install -r requirements.txt

## Ejecución

Para ejecutar el flujo principal con CSV o JSON:

    python src/main.py --input data/vueltas.csv --formato csv
    python src/main.py --input data/vueltas.json --formato json

Para ejecutar las pruebas automatizadas:

    python -m unittest discover -s tests -v

## Resultado esperado

Al correr el programa se muestra en consola la auditoría de lectura (`entrada = validos + rechazados`) y se guarda en `outputs/resumen_pilotos.csv` una tabla como la siguiente:

| piloto | vueltas_validas | mejor_vuelta_s | promedio_s | mediana_s | desvio_s |
|---|---|---|---|---|---|
| VER | 14 | 81.420 | 81.890 | 81.860 | 0.310 |
| NOR | 14 | 81.350 | 81.940 | 81.910 | 0.420 |
| LEC | 13 | 81.610 | 82.120 | 82.090 | 0.350 |
| COL | 13 | 82.150 | 82.540 | 82.510 | 0.290 |

## Organización del código

    TrabajoPractico2_Santiago_Manuel_Fernandez/
    |-- README.md
    |-- requirements.txt
    |-- .gitignore
    |-- src/
    |   |-- main.py
    |   |-- fuentes.py
    |   `-- pipeline.py
    |-- tests/
    |   `-- test_pipeline.py
    |-- data/
    |   |-- README.md
    |   |-- vueltas.csv
    |   `-- vueltas.json
    `-- outputs/

## Decisiones de limpieza, interpretación y limitaciones

* **Decisiones de limpieza:** se apartan las filas con campos vacíos, formatos de tiempo o código de piloto inválidos, números de vuelta duplicados para un mismo piloto, diferencias mayores a `0.05` s entre la suma de los tres sectores y el tiempo total, y las vueltas con paso por boxes (`en_boxes = True`). Todas las filas descartadas se registran en `outputs/rechazados.csv` con su motivo sin modificar los datos originales.
* **Interpretación:** el ranking ordena por tiempo promedio en pista limpia (`promedio_s`), permitiendo distinguir entre quién hizo una única vuelta rápida aislada y quién sostuvo el mejor ritmo y menor dispersión (`desvio_s`).
* **Limitaciones:** los tiempos no están ajustados por la descarga progresiva de combustible a lo largo de la carrera ni por el tráfico en pista.
