"""Punto de entrada del TP2: análisis de tiempos de vuelta de Fórmula 1."""

import argparse
from pathlib import Path
import sys

try:
    from src.fuentes import ErrorDatos, FuenteCSV, FuenteDatos, FuenteJSON
    from src.pipeline import (
        TOLERANCIA_SECTORES_SEG,
        AplicacionTelemetria,
        comunicar,
    )
except ImportError:
    from fuentes import ErrorDatos, FuenteCSV, FuenteDatos, FuenteJSON
    from pipeline import (
        TOLERANCIA_SECTORES_SEG,
        AplicacionTelemetria,
        comunicar,
    )


def crear_fuente(ruta: str | Path, formato: str) -> FuenteDatos:
    """Instancia la fuente correspondiente según el formato solicitado."""
    formato_limpio = formato.strip().lower()
    if formato_limpio == "csv":
        return FuenteCSV(ruta)
    if formato_limpio == "json":
        return FuenteJSON(ruta)
    raise ErrorDatos(f"Formato no soportado: {formato!r}. Use 'csv' o 'json'.")


def configurar_argumentos() -> argparse.Namespace:
    """Define los argumentos de línea de comandos de la aplicación."""
    parser = argparse.ArgumentParser(
        description="Validador de sesiones y comparador de vueltas de F1."
    )
    parser.add_argument(
        "--input",
        default="data/vueltas.csv",
        help="Ruta al archivo de entrada (por defecto: data/vueltas.csv).",
    )
    parser.add_argument(
        "--formato",
        choices=("csv", "json"),
        default="csv",
        help="Formato del archivo de entrada: csv o json.",
    )
    parser.add_argument(
        "--output",
        default="outputs",
        help="Directorio donde se guardan los archivos de salida.",
    )
    parser.add_argument(
        "--pilotos",
        nargs="*",
        default=None,
        help="Filtro opcional de códigos de piloto (ej. VER NOR LEC COL).",
    )
    parser.add_argument(
        "--tolerancia",
        type=float,
        default=TOLERANCIA_SECTORES_SEG,
        help="Tolerancia máxima en segundos entre sectores y tiempo total.",
    )
    return parser.parse_args()


def mostrar_resumen_consola(
    resumen: list[dict[str, object]],
    auditoria: dict[str, int],
) -> None:
    """Imprime en consola la auditoría de lectura y el ranking de pilotos."""
    print(
        f"Auditoría -> Entrada: {auditoria['entrada']} | "
        f"Válidas: {auditoria['validos']} | "
        f"Rechazadas: {auditoria['rechazados']}"
    )
    encabezado = (
        f"{'Piloto':<8} {'Vueltas':>7} {'Mejor (s)':>10} "
        f"{'Promedio (s)':>13} {'Mediana (s)':>12} {'Desvío (s)':>11}"
    )
    print("\n" + encabezado)
    print("-" * len(encabezado))
    for fila in resumen:
        print(
            f"{str(fila['piloto']):<8} "
            f"{int(fila['vueltas_validas']):>7d} "
            f"{float(fila['mejor_vuelta_s']):>10.3f} "
            f"{float(fila['promedio_s']):>13.3f} "
            f"{float(fila['mediana_s']):>12.3f} "
            f"{float(fila['desvio_s']):>11.3f}"
        )


def main() -> int:
    """Coordina la lectura, ejecución del pipeline y guardado de salidas."""
    args = configurar_argumentos()
    try:
        fuente = crear_fuente(args.input, args.formato)
        app = AplicacionTelemetria(fuente=fuente, tolerancia=args.tolerancia)
        resumen, rechazadas, auditoria = app.ejecutar(pilotos=args.pilotos)
        comunicar(resumen, rechazadas, directorio_salida=args.output)
        mostrar_resumen_consola(resumen, auditoria)
    except (FileNotFoundError, ErrorDatos) as error:
        print(f"Error en el procesamiento: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
