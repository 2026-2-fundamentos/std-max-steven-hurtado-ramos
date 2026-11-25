import csv
import gzip
import json
import re
from collections import Counter
from decimal import Decimal, InvalidOperation
from pathlib import Path


ACTIVITY_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = ACTIVITY_DIR / "data" / "ventas.csv.gz"
REPORT_FILE = ACTIVITY_DIR / "submission" / "data_quality_report.json"

REQUIRED_COLUMNS = {
    "supplier_id",
    "supplier",
    "country",
    "city",
    "purchase_date",
    "amount",
    "discount",
    "weight",
    "units",
    "unit_price",
    "contact_email",
}

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


def is_missing(value):
    value = value.strip()
    return value == "" or value == "N/A"


def is_positive_integer(value):
    try:
        number = Decimal(value.strip())
    except InvalidOperation:
        return False

    return (
        number.is_finite()
        and number > 0
        and number == number.to_integral_value()
    )


def main():
    with gzip.open(DATA_FILE, "rt", encoding="utf-8", newline="") as file:
        reader = csv.reader(file)
        raw_headers = next(reader, [])
        headers = [
            re.sub(
                r"\s+",
                "_",
                header.replace("\ufeff", "").strip().lower(),
            )
            for header in raw_headers
        ]
        rows = [row for row in reader if row]

    column_indexes = {column: index for index, column in enumerate(headers)}

    missing_value_count_by_column = {}
    for index, column in enumerate(headers):
        missing_value_count_by_column[column] = sum(
            is_missing(row[index] if index < len(row) else "")
            for row in rows
        )

    duplicate_counts = Counter(tuple(row) for row in rows)
    duplicate_row_count = sum(count - 1 for count in duplicate_counts.values())

    supplier_id_index = column_indexes.get("supplier_id")
    if supplier_id_index is None:
        duplicate_supplier_id_row_count = 0
    else:
        supplier_ids = [
            row[supplier_id_index]
            for row in rows
            if supplier_id_index < len(row)
            and not is_missing(row[supplier_id_index])
        ]
        supplier_id_counts = Counter(supplier_ids)
        duplicate_supplier_id_row_count = sum(
            count
            for count in supplier_id_counts.values()
            if count > 1
        )

    email_index = column_indexes.get("contact_email")
    if email_index is None:
        invalid_email_count = 0
    else:
        invalid_email_count = sum(
            not is_missing(row[email_index])
            and EMAIL_PATTERN.fullmatch(row[email_index]) is None
            for row in rows
            if email_index < len(row)
        )

    units_index = column_indexes.get("units")
    if units_index is None:
        invalid_unit_count = 0
    else:
        invalid_unit_count = sum(
            not is_missing(row[units_index])
            and not is_positive_integer(row[units_index])
            for row in rows
            if units_index < len(row)
        )

    country_index = column_indexes.get("country")
    if country_index is None:
        country_values = []
    else:
        country_values = sorted({
            row[country_index]
            for row in rows
            if country_index < len(row)
        })

    report = {
        "row_count": len(rows),
        "column_count": len(headers),
        "missing_required_columns": sorted(REQUIRED_COLUMNS - set(headers)),
        "unexpected_columns": sorted(set(headers) - REQUIRED_COLUMNS),
        "duplicate_row_count": duplicate_row_count,
        "duplicate_supplier_id_row_count": duplicate_supplier_id_row_count,
        "missing_value_count_by_column": missing_value_count_by_column,
        "invalid_email_count": invalid_email_count,
        "invalid_unit_count": invalid_unit_count,
        "country_values": country_values,
    }

    REPORT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with REPORT_FILE.open("w", encoding="utf-8") as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    return report