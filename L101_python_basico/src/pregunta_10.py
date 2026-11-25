import csv
import gzip
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"


def pregunta_10():
    result = []

    with gzip.open(DATA_FILE, "rt", encoding="utf-8", newline="") as file:
        for row in csv.reader(file, delimiter="\t"):
            codes_count = len(row[3].split(",")) if row[3] else 0
            metrics_count = len(row[4].split(",")) if row[4] else 0
            result.append((row[0], codes_count, metrics_count))

    return result
