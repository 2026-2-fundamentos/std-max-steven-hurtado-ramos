import csv
import gzip
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"


def pregunta_03():
    totals = {}

    with gzip.open(DATA_FILE, "rt", encoding="utf-8", newline="") as file:
        for row in csv.reader(file, delimiter="\t"):
            letter = row[0]
            value = int(row[1])
            totals[letter] = totals.get(letter, 0) + value

    return sorted(totals.items())