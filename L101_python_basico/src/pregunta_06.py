import csv
import gzip
from pathlib import Path


DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "data.csv.gz"


def pregunta_06():
    ranges = {}

    with gzip.open(DATA_FILE, "rt", encoding="utf-8", newline="") as file:
        for row in csv.reader(file, delimiter="\t"):
            for pair in row[4].split(","):
                key, raw_value = pair.split(":", 1)
                value = int(raw_value)

                if key not in ranges:
                    ranges[key] = [value, value]  # mínimo, máximo
                else:
                    ranges[key][0] = min(ranges[key][0], value)
                    ranges[key][1] = max(ranges[key][1], value)

    return [
        (key, ranges[key][0], ranges[key][1])
        for key in sorted(ranges)
    ]
