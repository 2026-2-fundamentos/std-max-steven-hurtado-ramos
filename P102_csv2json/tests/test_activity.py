import json
import runpy
import sys
from pathlib import Path

import pytest

ACTIVITY_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ACTIVITY_DIR))

from src.main import convert_csv_to_json

IS_PROFESSOR = any((path / ".PROFESSOR").exists() for path in ACTIVITY_DIR.parents)
CODE_DIR = ACTIVITY_DIR / ("professor" if IS_PROFESSOR else "src")
SUBMISSION_FILE = ACTIVITY_DIR / "submission" / "drivers.json"


def test_01(monkeypatch):
    monkeypatch.chdir(ACTIVITY_DIR)
    runpy.run_path(str(CODE_DIR / "main.py"), run_name="__main__")

    assert SUBMISSION_FILE.is_file()

    records = json.loads(SUBMISSION_FILE.read_text(encoding="utf-8"))

    assert len(records) == 34
    assert all(set(record) == {"driverId", "name", "certified", "wage-plan"} for record in records)
    assert records[0] == {
        "driverId": "10",
        "name": "George Vetticaden",
        "certified": "N",
        "wage-plan": "miles",
    }


def test_02_convert_csv_to_json_removes_sensitive_fields(tmp_path):
    csv_file = tmp_path / "drivers.csv"
    output_file = tmp_path / "output" / "drivers.json"

    csv_file.write_text(
        "driverId,name,ssn,location,certified,wage-plan\n"
        "10,George Vetticaden,621011971,244-4532 Nulla Rd.,N,miles\n"
        "11,Jamie Engesser,262112338,366-4125 Ac Street,Y,hours\n",
        encoding="utf-8",
    )

    records = convert_csv_to_json(csv_file, output_file)

    expected = [
        {
            "driverId": "10",
            "name": "George Vetticaden",
            "certified": "N",
            "wage-plan": "miles",
        },
        {
            "driverId": "11",
            "name": "Jamie Engesser",
            "certified": "Y",
            "wage-plan": "hours",
        },
    ]

    assert records == expected
    assert json.loads(output_file.read_text(encoding="utf-8")) == expected
    assert all(set(record) == {"driverId", "name", "certified", "wage-plan"} for record in records)
    assert all("ssn" not in record and "location" not in record for record in records)


def test_03_validate_required_columns_raises_for_missing_fields(tmp_path):
    csv_file = tmp_path / "drivers.csv"
    csv_file.write_text(
        "driverId,name,certified\n"
        "10,George Vetticaden,N\n",
        encoding="utf-8",
    )

    with pytest.raises(ValueError, match="Faltan columnas requeridas"):
        convert_csv_to_json(csv_file, tmp_path / "output" / "drivers.json")
