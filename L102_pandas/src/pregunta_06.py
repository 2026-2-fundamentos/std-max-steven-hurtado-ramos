from pathlib import Path

import pandas as pd


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "tbl1.tsv"


def pregunta_06():
    data = pd.read_csv(DATA_FILE, sep="\t")
    values = data["c4"].dropna().astype(str).str.upper().unique()
    return sorted(values.tolist())
