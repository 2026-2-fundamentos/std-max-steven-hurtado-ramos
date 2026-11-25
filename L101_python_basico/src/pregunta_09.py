import csv
import gzip
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"


def pregunta_09():
    counts = {}

    with gzip.open(DATA_FILE, "rt", encoding="utf-8", newline="") as file:
        for row in csv.reader(file, delimiter="\t"):
            for pair in row[4].split(","):
                key, _ = pair.split(":", 1)
                counts[key] = counts.get(key, 0) + 1

    return dict(sorted(counts.items()))
