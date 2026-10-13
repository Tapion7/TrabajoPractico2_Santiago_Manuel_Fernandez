"""Fuentes de datos: una abstracción común y dos implementaciones (CSV y JSON)."""

import csv
import json
from abc import ABC, abstractmethod
from pathlib import Path


class FuenteDatos(ABC):
    """Contrato común: toda fuente sabe cargar sus registros como lista de dicts."""

    def __init__(self, ruta):
        self.ruta = Path(ruta)

    @abstractmethod
    def cargar(self):
        """Devuelve una lista de diccionarios, uno por fila (una vuelta de un piloto)."""


class FuenteCSV(FuenteDatos):
    def cargar(self):
        with self.ruta.open(encoding="utf-8", newline="") as archivo:
            return list(csv.DictReader(archivo))


class FuenteJSON(FuenteDatos):
    def cargar(self):
        with self.ruta.open(encoding="utf-8") as archivo:
            return json.load(archivo)
