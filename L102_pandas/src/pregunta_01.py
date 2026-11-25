import pandas as pd
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "tbl0.tsv"


def pregunta_01():
    data = pd.read_csv(DATA_FILE, sep="\t")
    return int(len(data))
