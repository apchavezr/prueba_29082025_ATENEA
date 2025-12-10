from __future__ import annotations

import argparse
from pathlib import Path
from typing import Optional

import pandas as pd


def load_table(file_path: Path) -> pd.DataFrame:
    """Load a tabular file using pandas.

    Parameters
    ----------
    file_path: Path
        Path to the file to load. Excel formats are read with ``read_excel``;
        everything else defaults to ``read_csv``.
    """
    suffix = file_path.suffix.lower()
    if suffix in {".xlsx", ".xls", ".xlsm", ".xlsb"}:
        return pd.read_excel(file_path)
    return pd.read_csv(file_path)


def filter_convocatorias(convocatorias: pd.DataFrame) -> pd.DataFrame:
    """Filter convocatorias for TALENTOS-CAPACIDADES and TALENTOS origin."""
    mask = (
        convocatorias["SUBLINEA_TALENTOS"].astype(str).str.upper().eq("TALENTOS-CAPACIDADES")
        & convocatorias["ORIGEN"].astype(str).str.upper().eq("TALENTOS")
    )
    return convocatorias.loc[mask].copy()


def merge_datasets(filtered_convocatorias: pd.DataFrame, personas: pd.DataFrame) -> pd.DataFrame:
    """Merge filtered convocatorias with personas on ID_PERSONA."""
    return filtered_convocatorias.merge(
        personas,
        on="ID_PERSONA",
        how="inner",
        suffixes=("_CONVOCATORIA", "_PERSONA"),
    )


def order_assignments(merged: pd.DataFrame) -> pd.DataFrame:
    """Order merged records prioritizing MEDICINA then remaining programs.

    The ordering keys are:
    1. MEDICINA programs first (case-insensitive match on ``NOMBRE_PROGRAMA``).
    2. ``ID_PERSONA`` ascending.
    3. ``PRIORIDAD`` ascending to keep priority 1 before 2 for duplicates.
    """
    es_medicina = merged["NOMBRE_PROGRAMA"].astype(str).str.upper().str.strip().eq("MEDICINA")
    merged = merged.assign(_medicina_first=~es_medicina)
    ordered = merged.sort_values(by=["_medicina_first", "ID_PERSONA", "PRIORIDAD"], ascending=[True, True, True])
    return ordered.drop(columns=["_medicina_first"])


def process(conv_path: Path, persona_path: Path, output_path: Optional[Path] = None) -> Path:
    """Execute the full workflow and save the result to ``output_path``.

    If ``output_path`` is not provided, the file ``output/asignaciones_procesadas.csv``
    is created relative to the working directory.
    """
    convocatorias = load_table(conv_path)
    personas = load_table(persona_path)

    filtered = filter_convocatorias(convocatorias)
    merged = merge_datasets(filtered, personas)
    ordered = order_assignments(merged)

    destination = output_path or Path("output/asignaciones_procesadas.csv")
    destination.parent.mkdir(parents=True, exist_ok=True)
    ordered.to_csv(destination, index=False)
    return destination


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Filtra convocatorias TALENTOS-CAPACIDADES, realiza merge con personas "
            "y ordena asignaciones priorizando MEDICINA y la columna PRIORIDAD."
        )
    )
    parser.add_argument(
        "convocatorias_file",
        type=Path,
        help="Ruta al archivo 20251110_SICORE_Convocatorias_TExcp Algoritmo (CSV o Excel).",
    )
    parser.add_argument(
        "personas_file",
        type=Path,
        help="Ruta al archivo 20251118_JE-Talentos_PersonaOferta_cierre (CSV o Excel).",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        default=None,
        help="Ruta de salida opcional para el archivo CSV resultante.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    destination = process(args.convocatorias_file, args.personas_file, args.output)
    print(f"Archivo de asignaciones generado en: {destination}")


if __name__ == "__main__":
    main()
