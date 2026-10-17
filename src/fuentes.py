

from abc import ABC, abstractmethod
import csv
import json
from pathlib import Path
from typing import Any


class ErrorDatos(ValueError):
    """Excepción para entradas que incumplen el contrato de datos."""


class FuenteDatos(ABC):
    """Contrato común para cargar registros de vueltas como lista de dicts."""

    def __init__(self, ruta: str | Path) -> None:
        """Inicializa la fuente con la ruta al archivo de origen."""
        self._ruta = Path(ruta)

    @property
    def ruta(self) -> Path:
        """Devuelve la ruta del archivo asociada a la fuente."""
        return self._ruta

    def comprobar_archivo(self) -> None:
        """Verifica que el archivo exista antes de intentar leerlo."""
        if not self._ruta.is_file():
            raise FileNotFoundError(
                f"No se encontró el archivo de datos: {self._ruta}"
            )

    @abstractmethod
    def cargar(self) -> list[dict[str, Any]]:
        """Devuelve una lista de diccionarios, uno por cada fila leída."""
        raise NotImplementedError


class FuenteCSV(FuenteDatos):
    """Lectura de registros de telemetría desde archivos CSV."""

    def cargar(self) -> list[dict[str, Any]]:
        """Lee el archivo CSV y devuelve sus filas como diccionarios."""
        self.comprobar_archivo()
        with self._ruta.open(encoding="utf-8", newline="") as archivo:
            lector = csv.DictReader(archivo)
            if lector.fieldnames is None:
                raise ErrorDatos("El archivo CSV no contiene encabezados.")
            return list(lector)


class FuenteJSON(FuenteDatos):
    """Lectura de registros de telemetría desde archivos JSON."""

    def cargar(self) -> list[dict[str, Any]]:
        """Lee el archivo JSON validando que sea una lista de objetos."""
        self.comprobar_archivo()
        try:
            with self._ruta.open(encoding="utf-8") as archivo:
                contenido = json.load(archivo)
        except json.JSONDecodeError as error:
            raise ErrorDatos(f"Archivo JSON mal formado: {error}") from error

        if not isinstance(contenido, list) or not all(
            isinstance(fila, dict) for fila in contenido
        ):
            raise ErrorDatos(
                "El archivo JSON debe contener una lista de objetos."
            )
        return contenido