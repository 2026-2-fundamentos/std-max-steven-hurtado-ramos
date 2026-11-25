import csv
import gzip
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"


def pregunta_12():
    totals = {}

    with gzip.open(DATA_FILE, "rt", encoding="utf-8", newline="") as file:
        for row in csv.reader(file, delimiter="\t"):
            letter = row[0]
            metrics_total = sum(
                int(pair.split(":", 1)[1])
                for pair in row[4].split(",")
            )
            totals[letter] = totals.get(letter, 0) + metrics_total

    return dict(sorted(totals.items()))
    