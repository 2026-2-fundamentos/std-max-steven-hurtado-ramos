import csv
import gzip
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"


def pregunta_08():
    letters_by_value = {}

    with gzip.open(DATA_FILE, "rt", encoding="utf-8", newline="") as file:
        for row in csv.reader(file, delimiter="\t"):
            value = int(row[1])
            letters_by_value.setdefault(value, set()).add(row[0])

    return [
        (value, sorted(letters_by_value[value]))
        for value in sorted(letters_by_value)
    ]
