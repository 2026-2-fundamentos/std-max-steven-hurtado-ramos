from pathlib import Path

import pandas as pd


ACTIVITY_DIR = Path(__file__).resolve().parents[1]
TBL0_FILE = ACTIVITY_DIR / "data" / "tbl0.tsv"
TBL2_FILE = ACTIVITY_DIR / "data" / "tbl2.tsv"


def pregunta_13():
    tbl0 = pd.read_csv(TBL0_FILE, sep="\t")
    tbl2 = pd.read_csv(TBL2_FILE, sep="\t")

    combined = tbl0.merge(tbl2, on="c0")
    return combined.groupby("c1")["c5b"].sum().sort_index()