import csv
import gzip
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"


def pregunta_05():
    ranges = {}

    with gzip.open(DATA_FILE, "rt", encoding="utf-8", newline="") as file:
        for row in csv.reader(file, delimiter="\t"):
            letter = row[0]
            value = int(row[1])

            if letter not in ranges:
                ranges[letter] = [value, value]  # mínimo, máximo
            else:
                ranges[letter][0] = min(ranges[letter][0], value)
                ranges[letter][1] = max(ranges[letter][1], value)

    return [
        (letter, ranges[letter][1], ranges[letter][0])
        for letter in sorted(ranges)
    ]