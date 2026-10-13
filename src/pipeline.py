"""Flujo de procesamiento: leer -> validar -> limpiar -> analizar -> comunicar."""


def validar(registros):
    """Chequea el esquema y las condiciones necesarias para el análisis.

    A completar: columnas esperadas, tiempos numéricos y positivos, etc.
    """
    raise NotImplementedError


def limpiar(registros):
    """Devuelve (filas_validas, filas_rechazadas) para registrar qué se descartó y por qué.

    A completar.
    """
    raise NotImplementedError


def analizar(registros):
    """Calcula ritmo y consistencia por piloto.

    A completar.
    """
    raise NotImplementedError


def comunicar(resultado):
    """Muestra o guarda el resultado ligado a la pregunta guía.

    A completar.
    """
    raise NotImplementedError
