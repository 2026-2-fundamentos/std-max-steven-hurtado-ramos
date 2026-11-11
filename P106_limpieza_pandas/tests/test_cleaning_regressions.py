"""Pruebas de regresión para la limpieza de ventas de P106."""

import sys
from pathlib import Path

import pandas as pd
import pytest

ACTIVITY_DIR = Path(__file__).resolve().parents[1]
if str(ACTIVITY_DIR) not in sys.path:
    sys.path.insert(0, str(ACTIVITY_DIR))

from src import main as cleaning


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        ("96000.00", 96000.0),
        ("980.000.00", 980000.0),
        ("$125,000.00", 125000.0),
        ("$1,050,000.00", 1050000.0),
    ],
)
def test_unit_price_formats_are_normalized(raw_value, expected):
    sales = pd.DataFrame({"unit_price": [raw_value]})

    cleaning.clean_unit_price_column(sales)

    assert sales.loc[0, "unit_price"] == pytest.approx(expected)


@pytest.mark.parametrize(
    ("raw_value", "expected"),
    [
        ("0.5%", 0.005),
        ("20%", 0.2),
        ("0.2", 0.2),
        ("5", 0.05),
    ],
)
def test_discount_formats_are_normalized(raw_value, expected):
    sales = pd.DataFrame({"discount": [raw_value]})

    cleaning.clean_discount_column(sales)

    assert sales.loc[0, "discount"] == pytest.approx(expected)


def test_main_preserves_supplier_ids_and_cleans_numeric_values(tmp_path, monkeypatch):
    input_file = tmp_path / "ventas.csv"
    output_file = tmp_path / "limpias.csv"
    raw_sales = pd.DataFrame(
        {
            " Supplier ID ": [" 0007 "],
            "supplier": ["amazon web services colombia "],
            "COUNTRY": ["CO"],
            "City ": [" Bogotá "],
            "Purchase Date": ["2026/02/02"],
            "Amount": ["$480,000"],
            "Discount": ["0.5%"],
            "Weight": ["50000 g"],
            "Units": ["5"],
            "Unit Price": ["$1,050,000.00"],
            "Contact Email": ["compras@example.com"],
        }
    )
    raw_sales.to_csv(input_file, index=False)
    monkeypatch.setattr(cleaning, "INPUT_FILE", input_file)
    monkeypatch.setattr(cleaning, "OUTPUT_FILE", output_file)

    cleaning.main()

    cleaned = pd.read_csv(output_file, dtype={"supplier_id": "string"})
    assert cleaned.loc[0, "supplier_id"] == "0007"
    assert cleaned.loc[0, "amount"] == pytest.approx(480000)
    assert cleaned.loc[0, "unit_price"] == pytest.approx(1050000)
    assert cleaned.loc[0, "discount"] == pytest.approx(0.005)
