from pathlib import Path

import pandas as pd


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "tbl0.tsv"


def pregunta_10():
    data = pd.read_csv(DATA_FILE, sep="\t")

    result = data.groupby("c1")["c2"].apply(
        lambda values: ":".join(str(value) for value in sorted(values))
    )

    return result.to_frame()
