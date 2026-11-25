from pathlib import Path

import pandas as pd


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "tbl0.tsv"


def pregunta_08():
    data = pd.read_csv(DATA_FILE, sep="\t")
    data["suma"] = data["c0"] + data["c2"]
    return data