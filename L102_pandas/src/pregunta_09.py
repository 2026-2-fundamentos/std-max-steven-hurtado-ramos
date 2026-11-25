from pathlib import Path

import pandas as pd


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "tbl0.tsv"


def pregunta_09():
    data = pd.read_csv(DATA_FILE, sep="\t")
    data["year"] = pd.to_datetime(data["c3"]).dt.strftime("%Y")
    return data