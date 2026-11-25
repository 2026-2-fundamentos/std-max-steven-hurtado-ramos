from pathlib import Path

import pandas as pd


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "tbl0.tsv"


def pregunta_02():
    """
    ¿Cuántas columnas tiene la tabla `data/tbl0.tsv`?
    Retorne la cantidad como un número entero.
    """
    data = pd.read_csv(DATA_FILE, sep="\t")
    return int(data.shape[1])
