# prueba_29082025_ATENEA

Script para procesar los archivos **20251110_SICORE_Convocatorias_TExcp Algoritmo** y **20251118_JE-Talentos_PersonaOferta_cierre** de acuerdo con las reglas solicitadas:

1. Filtra las convocatorias donde `SUBLINEA_TALENTOS == TALENTOS-CAPACIDADES` y `ORIGEN == TALENTOS`.
2. Realiza un `merge` con el archivo de personas en `ID_PERSONA` (valioso para analizar casos con `PRIORIDAD` 1 y 2 como el `ID_PERSONA` 451965).
3. Ordena priorizando primero las filas con `NOMBRE_PROGRAMA == MEDICINA`, luego el resto por `ID_PERSONA` ascendente y `PRIORIDAD` ascendente.

## Requisitos

- Python 3.10+
- Dependencias de Python (instalar con `pip install -r requirements.txt`)

## Uso

```bash
python process_convocatorias.py \
  "20251110_SICORE_Convocatorias_TExcp Algoritmo.xlsx" \
  "20251118_JE-Talentos_PersonaOferta_cierre.xlsx" \
  --output output/asignaciones_procesadas.csv
```

El script detecta automáticamente si los archivos son CSV o Excel. El resultado se guarda en un CSV, creando la carpeta `output/` si no existe, y deja la asignación lista para continuar con el proceso de cupos.
