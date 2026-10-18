# Pruebas

Acá están las verificaciones ejecutables del proyecto (`test_pipeline.py`, `unittest`). Cubren:

1. un caso normal (conversión `M:SS.mmm` y clase `Vuelta`);
2. entradas inválidas y casos límite (tabla vacía, columnas faltantes, archivo inexistente, JSON mal formado, piloto con una sola vuelta);
3. propiedades del resultado (leer el CSV y el JSON da lo mismo; `entrada = válidos + rechazados`; `limpiar()` no modifica la entrada).

Comando para ejecutarlas (desde la raíz del repositorio):

    python -m unittest discover -s tests -v
