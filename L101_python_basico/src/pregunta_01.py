import csv
import gzip
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"


def pregunta_01():
    with gzip.open(DATA_FILE, "rt", encoding="utf-8", newline="") as file:
        rows = csv.reader(file, delimiter="\t")
        return sum(int(row[1]) for row in rows)