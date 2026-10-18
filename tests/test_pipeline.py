"""Pruebas automatizadas para el flujo de telemetría de Fórmula 1."""

import copy
from pathlib import Path
import tempfile
import unittest

from src.fuentes import ErrorDatos, FuenteCSV, FuenteJSON
from src.pipeline import (
    COLUMNAS_REQUERIDAS,
    AplicacionTelemetria,
    Vuelta,
    analizar,
    convertir_tiempo,
    limpiar,
    validar,
)


RUTA_BASE = Path(__file__).resolve().parent.parent
RUTA_CSV = RUTA_BASE / "data" / "vueltas.csv"
RUTA_JSON = RUTA_BASE / "data" / "vueltas.json"


class PruebasTelemetriaF1(unittest.TestCase):
    """Suite de pruebas para fuentes, dominio, limpieza y análisis."""

    def test_conversion_y_clase_vuelta_caso_normal(self) -> None:
        """Verifica conversión M:SS.mmm y cálculo de sectores en Vuelta."""
        self.assertAlmostEqual(convertir_tiempo("1:21.420"), 81.420, places=3)
        vuelta = Vuelta(
            vuelta_id="V001",
            piloto="VER",
            numero_vuelta=1,
            tiempo_total="1:21.420",
            sector_1=26.869,
            sector_2=30.940,
            sector_3=23.611,
            en_boxes=False,
        )
        self.assertAlmostEqual(vuelta.tiempo_segundos(), 81.420, places=3)
        self.assertAlmostEqual(vuelta.suma_sectores(), 81.420, places=3)
        self.assertEqual(vuelta.diferencia_sectores(), 0.0)

    def test_equivalencia_csv_y_json(self) -> None:
        """Comprueba que las muestras CSV y JSON generen idéntica salida."""
        app_csv = AplicacionTelemetria(FuenteCSV(RUTA_CSV))
        app_json = AplicacionTelemetria(FuenteJSON(RUTA_JSON))

        res_csv, rech_csv, aud_csv = app_csv.ejecutar()
        res_json, rech_json, aud_json = app_json.ejecutar()

        self.assertEqual(res_csv, res_json)
        self.assertEqual(aud_csv, aud_json)
        ids_rech_csv = [fila["vuelta_id"] for fila in rech_csv]
        ids_rech_json = [fila["vuelta_id"] for fila in rech_json]
        self.assertEqual(ids_rech_csv, ids_rech_json)

    def test_conservacion_de_cantidades_y_resultado_conocido(self) -> None:
        """Verifica entrada = válidos + rechazados y métricas del ranking."""
        app = AplicacionTelemetria(FuenteCSV(RUTA_CSV))
        resumen, rechazadas, auditoria = app.ejecutar()

        self.assertEqual(
            auditoria,
            {"entrada": 60, "validos": 54, "rechazados": 6},
        )
        self.assertEqual(
            auditoria["entrada"],
            auditoria["validos"] + auditoria["rechazados"],
        )
        self.assertEqual(
            {f["vuelta_id"] for f in rechazadas},
            {"V055", "V056", "V057", "V058", "V059", "V060"},
        )
        self.assertEqual(resumen[0]["piloto"], "VER")
        self.assertEqual(resumen[0]["vueltas_validas"], 14)
        self.assertAlmostEqual(resumen[0]["promedio_s"], 81.890, places=3)

    def test_no_mutacion_de_entrada(self) -> None:
        """Garantiza que limpiar() no modifique la lista de diccionarios."""
        original = FuenteCSV(RUTA_CSV).cargar()
        copia_antes = copy.deepcopy(original)
        limpiar(original)
        self.assertEqual(original, copia_antes)

    def test_caso_limite_una_sola_vuelta_valida(self) -> None:
        """Verifica que un piloto con una única vuelta tenga desvío 0.0."""
        unica = [
            Vuelta(
                vuelta_id="V001",
                piloto="COL",
                numero_vuelta=1,
                tiempo_total="1:22.150",
                sector_1=27.110,
                sector_2=31.217,
                sector_3=23.823,
                en_boxes=False,
            )
        ]
        resumen = analizar(unica)
        self.assertEqual(len(resumen), 1)
        self.assertEqual(resumen[0]["vueltas_validas"], 1)
        self.assertEqual(resumen[0]["desvio_s"], 0.0)

    def test_entradas_invalidas_y_errores_de_lectura(self) -> None:
        """Comprueba fallos explícitos ante esquema roto o archivo ausente."""
        with self.assertRaises(ErrorDatos):
            validar([])

        fila_incompleta = {col: "1" for col in COLUMNAS_REQUERIDAS[:-1]}
        with self.assertRaisesRegex(ErrorDatos, "Faltan columnas"):
            validar([fila_incompleta])

        with self.assertRaises(FileNotFoundError):
            FuenteCSV(RUTA_BASE / "data" / "no_existe.csv").cargar()

        with tempfile.TemporaryDirectory() as tmp:
            ruta_mal_json = Path(tmp) / "invalido.json"
            ruta_mal_json.write_text('{"no_es": "lista"}', encoding="utf-8")
            with self.assertRaises(ErrorDatos):
                FuenteJSON(ruta_mal_json).cargar()


if __name__ == "__main__":
    unittest.main()