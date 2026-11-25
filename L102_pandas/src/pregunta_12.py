from pathlib import Path

import pandas as pd


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "tbl2.tsv"


def pregunta_12():
    data = pd.read_csv(DATA_FILE, sep="\t")
    data["par"] = data["c5a"].astype(str) + ":" + data["c5b"].astype(str)

    return (
        data.groupby("c0", sort=True)["par"]
        .agg(lambda values: ",".join(sorted(values)))
        .reset_index(name="c5")
    )