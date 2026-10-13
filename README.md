# TP2 – Telemetría de Fórmula 1

**Autor:** Santiago Manuel Fernandez
**Materia:** Programación Orientada a Datos – Licenciatura en Ciencia de Datos – UCA, 2026

## Pregunta guía

> **¿Qué piloto fue más consistente y cuál tuvo el mejor ritmo en una carrera de Fórmula 1, a partir de los tiempos de vuelta registrados?**

Para responderla, el programa va a comparar los tiempos de vuelta de cada piloto en una carrera (promedio, mediana y dispersión), descartando vueltas no representativas (por ejemplo, vueltas de entrada o salida de boxes) y registrando qué filas se rechazaron y por qué.

## Problema y usuario

- **Problema:** los registros de vueltas en bruto tienen datos faltantes o atípicos, y no alcanza con mirar la vuelta más rápida para saber quién rindió mejor durante toda la carrera.
- **Usuario:** una persona aficionada a la F1 o estudiante de datos que quiere comparar el rendimiento entre pilotos de forma reproducible.
- **Resultado esperado:** una tabla con el ranking de pilotos por ritmo y por consistencia, y un archivo de salida con las filas rechazadas.

## Alcance de la primera versión

Incluye:
- una sola carrera (una muestra manejable);
- lectura de datos en CSV y JSON;
- validación y limpieza de los registros de vueltas;
- ranking por ritmo y por consistencia.

Queda fuera: aplicación web, aprendizaje automático, análisis de estrategia de neumáticos y comparación entre varias temporadas.

## Datos

_(A completar en el Paso 2: fuente, URL o procedimiento de obtención, licencia o condiciones de uso, fecha de consulta, unidad de análisis y variables.)_

Ver [`data/README.md`](data/README.md).

## Requisitos

Python 3.

## Ejecución

```
python src/main.py
```

## Resultado esperado

_(A completar cuando el programa produzca su primera salida.)_

## Organización del código

```
tp2-apellido/
|-- README.md
|-- requirements.txt
|-- .gitignore
|-- src/
|   |-- main.py
|   |-- fuentes.py
|   `-- pipeline.py
|-- tests/
|   `-- README.md
|-- data/
|   `-- README.md
`-- outputs/   (solo si las salidas se conservan)
```

## Decisiones de limpieza, interpretación y limitaciones

_(A completar a medida que avance el trabajo.)_
