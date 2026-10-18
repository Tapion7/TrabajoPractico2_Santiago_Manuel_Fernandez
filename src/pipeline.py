"""Flujo de datos: leer, validar, limpiar, analizar y comunicar."""

import csv
from dataclasses import dataclass
import math
from pathlib import Path
import re
import statistics
from typing import Any

try:
    from src.fuentes import ErrorDatos, FuenteDatos
except ImportError:
    from fuentes import ErrorDatos, FuenteDatos


COLUMNAS_REQUERIDAS = (
    "vuelta_id",
    "piloto",
    "numero_vuelta",
    "tiempo_total",
    "sector_1",
    "sector_2",
    "sector_3",
    "en_boxes",
)

PATRON_ID = re.compile(r"V[0-9]{3}")
PATRON_PILOTO = re.compile(r"[A-Z]{3}")
PATRON_TIEMPO = re.compile(r"([0-9]):([0-5][0-9]\.[0-9]{3})")

SECTOR_MINIMO_SEG = 10.0
TOLERANCIA_SECTORES_SEG = 0.05


def convertir_tiempo(texto: Any) -> float:
    """Convierte un tiempo en formato 'M:SS.mmm' a segundos totales."""
    if not isinstance(texto, str):
        raise ErrorDatos("El tiempo total debe ser una cadena de texto.")
    coincidencia = PATRON_TIEMPO.fullmatch(texto.strip())
    if coincidencia is None:
        raise ErrorDatos(f"Formato de tiempo inválido: {texto!r}")
    minutos = int(coincidencia.group(1))
    segundos = float(coincidencia.group(2))
    total = round(minutos * 60.0 + segundos, 3)
    if total <= 0:
        raise ErrorDatos("El tiempo total en segundos debe ser positivo.")
    return total


def _interpretar_booleano(valor: Any) -> bool:
    """Normaliza valores booleanos provenientes de CSV o JSON."""
    if isinstance(valor, bool):
        return valor
    if isinstance(valor, str):
        limpio = valor.strip().lower()
        if limpio == "true":
            return True
        if limpio == "false":
            return False
    raise ErrorDatos(f"Valor booleano inválido en en_boxes: {valor!r}")


@dataclass(frozen=True)
class Vuelta:
    """Representa una vuelta válida de un piloto con sus tres sectores."""

    vuelta_id: str
    piloto: str
    numero_vuelta: int
    tiempo_total: str
    sector_1: float
    sector_2: float
    sector_3: float
    en_boxes: bool = False

    def __post_init__(self) -> None:
        """Valida los invariantes de formato, rango y consistencia."""
        if (
            not isinstance(self.vuelta_id, str)
            or PATRON_ID.fullmatch(self.vuelta_id) is None
        ):
            raise ErrorDatos("vuelta_id inválido (debe cumplir V000).")
        if (
            not isinstance(self.piloto, str)
            or PATRON_PILOTO.fullmatch(self.piloto) is None
        ):
            raise ErrorDatos("Código de piloto inválido (3 letras A-Z).")
        if (
            not isinstance(self.numero_vuelta, int)
            or isinstance(self.numero_vuelta, bool)
            or self.numero_vuelta <= 0
        ):
            raise ErrorDatos("numero_vuelta debe ser un entero positivo.")

        convertir_tiempo(self.tiempo_total)

        sectores = (self.sector_1, self.sector_2, self.sector_3)
        if not all(
            isinstance(s, (int, float))
            and not isinstance(s, bool)
            and math.isfinite(s)
            and s >= SECTOR_MINIMO_SEG
            for s in sectores
        ):
            raise ErrorDatos("Sectores inválidos o menores al mínimo.")

    def tiempo_segundos(self) -> float:
        """Devuelve la duración total de la vuelta en segundos."""
        return convertir_tiempo(self.tiempo_total)

    def suma_sectores(self) -> float:
        """Devuelve la suma de los tres sectores parciales en segundos."""
        return round(self.sector_1 + self.sector_2 + self.sector_3, 3)

    def diferencia_sectores(self) -> float:
        """Calcula la diferencia absoluta entre el total y los sectores."""
        return round(abs(self.tiempo_segundos() - self.suma_sectores()), 3)


def validar(registros: list[dict[str, Any]]) -> None:
    """Chequea el esquema y que la colección de entrada no esté vacía."""
    if not isinstance(registros, list) or not registros:
        raise ErrorDatos("La tabla de entrada está vacía.")

    for fila in registros:
        if not isinstance(fila, dict):
            raise ErrorDatos("Cada registro debe ser un diccionario.")
        faltantes = set(COLUMNAS_REQUERIDAS) - set(fila.keys())
        if faltantes:
            columnas = ", ".join(sorted(faltantes))
            raise ErrorDatos(f"Faltan columnas requeridas: {columnas}")


def limpiar(
    registros: list[dict[str, Any]],
    tolerancia: float = TOLERANCIA_SECTORES_SEG,
) -> tuple[list[Vuelta], list[dict[str, Any]]]:
    """Separa vueltas válidas en pista limpia y registra las rechazadas."""
    validar(registros)

    conteo_ids: dict[str, int] = {}
    conteo_piloto_vuelta: dict[tuple[str, str], int] = {}
    for fila in registros:
        vid = str(fila.get("vuelta_id", "")).strip()
        piloto = str(fila.get("piloto", "")).strip()
        num = str(fila.get("numero_vuelta", "")).strip()
        conteo_ids[vid] = conteo_ids.get(vid, 0) + 1
        clave_pv = (piloto, num)
        conteo_piloto_vuelta[clave_pv] = (
            conteo_piloto_vuelta.get(clave_pv, 0) + 1
        )

    validas: list[Vuelta] = []
    rechazadas: list[dict[str, Any]] = []

    for fila in registros:
        motivos: list[str] = []
        vid = str(fila.get("vuelta_id") or "").strip()
        piloto = str(fila.get("piloto") or "").strip()
        num_raw = fila.get("numero_vuelta")
        tiempo_raw = fila.get("tiempo_total")

        if PATRON_ID.fullmatch(vid) is None:
            motivos.append("vuelta_id inválido")
        elif conteo_ids.get(vid, 0) > 1:
            motivos.append("vuelta_id duplicado")

        if PATRON_PILOTO.fullmatch(piloto) is None:
            motivos.append("piloto inválido")

        numero_vuelta = 0
        try:
            if num_raw is None or str(num_raw).strip() == "":
                raise ValueError
            numero_vuelta = int(str(num_raw).strip())
            if numero_vuelta <= 0:
                raise ValueError
        except ValueError:
            motivos.append("numero_vuelta inválido")
        else:
            if conteo_piloto_vuelta.get((piloto, str(num_raw).strip()), 0) > 1:
                motivos.append("vuelta repetida para el piloto")

        tiempo_seg = 0.0
        try:
            tiempo_seg = convertir_tiempo(
                tiempo_raw if isinstance(tiempo_raw, str) else ""
            )
        except ErrorDatos:
            motivos.append("tiempo_total inválido")

        sectores_num: list[float] = []
        for nombre_sec in ("sector_1", "sector_2", "sector_3"):
            val_sec = fila.get(nombre_sec)
            try:
                if val_sec is None or str(val_sec).strip() == "":
                    raise ValueError
                num_s = float(val_sec)
                if not math.isfinite(num_s) or num_s < SECTOR_MINIMO_SEG:
                    raise ValueError
                sectores_num.append(num_s)
            except (ValueError, TypeError):
                motivos.append(f"{nombre_sec} inválido")

        en_boxes = False
        try:
            en_boxes = _interpretar_booleano(fila.get("en_boxes"))
        except ErrorDatos:
            motivos.append("en_boxes inválido")

        if len(sectores_num) == 3 and tiempo_seg > 0:
            dif = abs(tiempo_seg - sum(sectores_num))
            if dif > tolerancia:
                motivos.append("diferencia con sectores supera tolerancia")

        if en_boxes:
            motivos.append("vuelta en boxes")

        if motivos:
            copia_rechazo = dict(fila)
            copia_rechazo["motivo"] = "; ".join(motivos)
            rechazadas.append(copia_rechazo)
        else:
            validas.append(
                Vuelta(
                    vuelta_id=vid,
                    piloto=piloto,
                    numero_vuelta=numero_vuelta,
                    tiempo_total=str(tiempo_raw).strip(),
                    sector_1=sectores_num[0],
                    sector_2=sectores_num[1],
                    sector_3=sectores_num[2],
                    en_boxes=en_boxes,
                )
            )

    if not validas:
        raise ErrorDatos("No quedaron vueltas válidas para analizar.")

    return validas, rechazadas


def analizar(
    vueltas_validas: list[Vuelta],
    pilotos: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Calcula ritmo (promedio, mediana, mejor vuelta) y consistencia."""
    if not vueltas_validas:
        raise ErrorDatos("Se requiere al menos una vuelta válida.")

    seleccion = vueltas_validas
    if pilotos:
        filtro = {p.strip().upper() for p in pilotos}
        seleccion = [v for v in vueltas_validas if v.piloto in filtro]
        if not seleccion:
            raise ErrorDatos("No hay vueltas válidas para esos pilotos.")

    por_piloto: dict[str, list[float]] = {}
    for vuelta in seleccion:
        por_piloto.setdefault(vuelta.piloto, []).append(
            vuelta.tiempo_segundos()
        )

    resumen: list[dict[str, Any]] = []
    for piloto, tiempos in por_piloto.items():
        desvio = (
            round(statistics.stdev(tiempos), 3) if len(tiempos) > 1 else 0.0
        )
        resumen.append(
            {
                "piloto": piloto,
                "vueltas_validas": len(tiempos),
                "mejor_vuelta_s": round(min(tiempos), 3),
                "promedio_s": round(statistics.mean(tiempos), 3),
                "mediana_s": round(statistics.median(tiempos), 3),
                "desvio_s": desvio,
            }
        )

    resumen.sort(key=lambda item: (item["promedio_s"], item["mejor_vuelta_s"]))
    return resumen


def verificar_resultado(
    resumen: list[dict[str, Any]],
    cantidad_validas: int,
) -> None:
    """Verifica invariantes sobre la tabla resumen generada."""
    if not resumen:
        raise ErrorDatos("El resumen de pilotos está vacío.")
    suma_vueltas = sum(int(fila["vueltas_validas"]) for fila in resumen)
    if suma_vueltas != cantidad_validas:
        raise ErrorDatos(
            "La suma de vueltas del resumen no coincide con las válidas."
        )
    for fila in resumen:
        if fila["mejor_vuelta_s"] <= 0 or fila["promedio_s"] <= 0:
            raise ErrorDatos("Los tiempos del resumen deben ser positivos.")
        if fila["desvio_s"] < 0:
            raise ErrorDatos("El desvío estándar no puede ser negativo.")


def comunicar(
    resumen: list[dict[str, Any]],
    rechazadas: list[dict[str, Any]],
    directorio_salida: str | Path = "outputs",
) -> None:
    """Guarda el ranking y los rechazos en CSV y los muestra en consola."""
    salida = Path(directorio_salida)
    salida.mkdir(parents=True, exist_ok=True)

    ruta_resumen = salida / "resumen_pilotos.csv"
    campos_resumen = [
        "piloto",
        "vueltas_validas",
        "mejor_vuelta_s",
        "promedio_s",
        "mediana_s",
        "desvio_s",
    ]
    with ruta_resumen.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos_resumen)
        escritor.writeheader()
        for fila in resumen:
            escritor.writerow(
                {
                    "piloto": fila["piloto"],
                    "vueltas_validas": fila["vueltas_validas"],
                    "mejor_vuelta_s": f"{fila['mejor_vuelta_s']:.3f}",
                    "promedio_s": f"{fila['promedio_s']:.3f}",
                    "mediana_s": f"{fila['mediana_s']:.3f}",
                    "desvio_s": f"{fila['desvio_s']:.3f}",
                }
            )

    ruta_rechazos = salida / "rechazados.csv"
    campos_rechazos = [*COLUMNAS_REQUERIDAS, "motivo"]
    with ruta_rechazos.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=campos_rechazos)
        escritor.writeheader()
        escritor.writerows(rechazadas)


class AplicacionTelemetria:
    """Coordina la lectura, limpieza, análisis y auditoría de la sesión."""

    def __init__(
        self,
        fuente: FuenteDatos,
        tolerancia: float = TOLERANCIA_SECTORES_SEG,
    ) -> None:
        """Recibe la fuente de datos por inyección de dependencia."""
        self._fuente = fuente
        self._tolerancia = tolerancia

    def ejecutar(
        self,
        pilotos: list[str] | None = None,
    ) -> tuple[list[dict[str, Any]], list[dict[str, Any]], dict[str, int]]:
        """Ejecuta el flujo completo y devuelve resumen, rechazos y conteos."""
        registros = self._fuente.cargar()
        validas, rechazadas = limpiar(registros, tolerancia=self._tolerancia)
        resumen = analizar(validas, pilotos=pilotos)
        if pilotos is None:
            verificar_resultado(resumen, len(validas))
        auditoria = {
            "entrada": len(registros),
            "validos": len(validas),
            "rechazados": len(rechazadas),
        }
        return resumen, rechazadas, auditoria