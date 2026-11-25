from pathlib import Path

import pandas as pd


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "tbl1.tsv"


def pregunta_11():
    data = pd.read_csv(DATA_FILE, sep="\t")

    return (
        data.groupby("c0", sort=True)["c4"]
        .agg(lambda letters: ",".join(sorted(letters)))
        .reset_index()
    )