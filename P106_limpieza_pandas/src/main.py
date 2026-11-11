from pathlib import Path
import re

import pandas as pd

ACTIVITY_DIR = Path(__file__).resolve().parents[1]
INPUT_FILE = ACTIVITY_DIR / "data" / "ventas.csv"
OUTPUT_FILE = ACTIVITY_DIR / "submission" / "ventas.csv"

SUPPLIER_REPLACEMENTS = {
    "amazon web services colombia": "Amazon Web Services Colombia",
    "BANCOLOMBIA S.A.": "Bancolombia S.A.",
    "Cementos Argos SA": "Cementos Argos S.A.",
    "cementos argos s.a.": "Cementos Argos S.A.",
    "Corona SAS": "Corona S.A.S.",
    "Ecopetrol  S.A.": "Ecopetrol S.A.",
    "GOOGLE COLOMBIA LTDA.": "Google Colombia Ltda.",
    "Grupo  Éxito  S.A.": "Grupo Éxito S.A.",
    "IBM Colombia SAS.": "IBM Colombia S.A.S.",
    "ibm colombia s.a.s.": "IBM Colombia S.A.S.",
    "MICROSOFT COLOMBIA INC.": "Microsoft Colombia Inc.",
    "Nutresa SA": "Nutresa S.A.",
    "nutresa s.a.": "Nutresa S.A.",
    "oracle colombia ltda.": "Oracle Colombia Ltda.",
    "POSTOBÓN S.A.": "Postobon S.A.",
    "SAP Colombia SAS": "SAP Colombia S.A.S.",
    "Schneider  Electric": "Schneider Electric",
    "SIEMENS S.A.S.": "Siemens S.A.S.",
    "siemens s.a.s.": "Siemens S.A.S.",
    "Sura  S.A.": "Sura S.A.",
    "Telefónica  Colombia": "Telefónica Colombia",
}

COUNTRY_REPLACEMENTS = {
    "CO": "COL",
    "COLOMBIA": "COL",
    "Colombia": "COL",
    "colombia": "COL",
}

CITY_REPLACEMENTS = {
    "bogotá": "Bogotá",
    "BOGOTÁ": "Bogotá",
    "Medellin": "Medellín",
    "medellín": "Medellín",
    "MEDELLÍN": "Medellín",
}


def clean_column_names(df):
    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
        .str.replace(r"[^a-z0-9_]+", "_", regex=True)
        .str.replace(r"_+", "_", regex=True)
        .str.replace(r"^_|_$", "", regex=True)
    )
    return df


def clean_supplier_id_column(df):
    df.loc[:, "supplier_id"] = df["supplier_id"].astype("string").str.strip()
    return df


def clean_supplier_column(df):
    series = df["supplier"].astype("string").str.strip().str.replace(r"\s+", " ", regex=True)
    normalized = {k.casefold(): v for k, v in SUPPLIER_REPLACEMENTS.items()}
    df.loc[:, "supplier"] = series.str.casefold().map(normalized).fillna(series)
    return df


def clean_country_column(df):
    series = df["country"].astype("string").str.strip().str.replace(r"\s+", " ", regex=True)
    normalized = {k.casefold(): v for k, v in COUNTRY_REPLACEMENTS.items()}
    df.loc[:, "country"] = series.str.casefold().map(normalized).fillna(series)
    df.loc[:, "country"] = df["country"].str.strip()
    return df


def clean_city_column(df):
    series = df["city"].astype("string").str.strip().str.replace(r"\s+", " ", regex=True)
    normalized = {k.casefold(): v for k, v in CITY_REPLACEMENTS.items()}
    df.loc[:, "city"] = series.str.casefold().map(normalized).fillna(series)
    return df


def _normalize_numeric_string(text):
    text = str(text).strip()
    if text == "" or text.upper() in {"N/A", "NA", "NULL"}:
        return pd.NA

    text = text.replace("COP", "").replace("$", "").replace(" ", "")
    text = text.replace("(", "-").replace(")", "")

    if text.endswith("K"):
        try:
            value = float(text[:-1].replace(".", "").replace(",", ""))
            return value * 1000
        except ValueError:
            return pd.NA

    if "." in text and "," in text:
        if text.rfind(".") > text.rfind(","):
            text = text.replace(",", "")
        else:
            text = text.replace(".", "").replace(",", ".")
    elif "," in text:
        parts = text.split(",")
        if len(parts) > 1 and len(parts[-1]) in {1, 2} and len(parts) > 1:
            text = ".".join(parts)
        else:
            text = "".join(parts)
    elif "." in text and text.count(".") > 1:
        text = text.replace(".", "")

    try:
        return float(text)
    except ValueError:
        return pd.NA


def clean_purchase_date_column(df):
    def convert_yyyy_s_mm_s_dd_to_yyyy_mm_dd(series):
        return series.str.replace(r"(\d{4})/(\d{2})/(\d{2})", r"\1-\2-\3", regex=True)

    def convert_mmddyyyy_to_yyyy_mm_dd(series):
        def convert_date(match):
            g1, g2, g3 = match.groups()
            month = int(g1)
            day = int(g2)
            year = int(g3)
            if day > 12:
                month, day = month, day
            elif month > 12:
                day, month = month, day
            return f"{year:04d}-{month:02d}-{day:02d}"

        return series.str.replace(r"(\d{2})/(\d{2})/(\d{4})", convert_date, regex=True)

    def convert_dd_mm_yyyy_to_yyyy_mm_dd_separated_with_dots(series):
        return series.str.replace(r"(\d{2})\.(\d{2})\.(\d{4})", r"\3-\2-\1", regex=True)

    def convert_dd_mm_yy_to_yyyy_mm_dd_separated_with_hyphens(series):
        return series.str.replace(r"^(\d{2})-(\d{2})-(\d{2})$", r"20\3-\2-\1", regex=True)

    def convert_mm_dd_yy_to_yyyy_mm_dd(series):
        return series.str.replace(r"^(\d{2})-(\d{2})-(\d{2})$", r"20\3-\1-\2", regex=True)

    df.loc[:, "purchase_date"] = df["purchase_date"].astype("string").str.strip()
    df.loc[:, "purchase_date"] = convert_yyyy_s_mm_s_dd_to_yyyy_mm_dd(df["purchase_date"])
    df.loc[:, "purchase_date"] = convert_mmddyyyy_to_yyyy_mm_dd(df["purchase_date"])
    df.loc[:, "purchase_date"] = convert_dd_mm_yyyy_to_yyyy_mm_dd_separated_with_dots(
        df["purchase_date"]
    )
    df.loc[:, "purchase_date"] = convert_dd_mm_yy_to_yyyy_mm_dd_separated_with_hyphens(
        df["purchase_date"]
    )
    df.loc[:, "purchase_date"] = convert_mm_dd_yy_to_yyyy_mm_dd(df["purchase_date"])
    df.loc[:, "purchase_date"] = pd.to_datetime(df["purchase_date"], errors="coerce").dt.strftime("%Y-%m-%d")
    return df


def clean_amount_column(df):
    df.loc[:, "amount"] = df["amount"].map(_normalize_numeric_string)
    df.loc[:, "amount"] = pd.to_numeric(df["amount"], errors="coerce")
    return df


def clean_unit_price_column(df):
    df.loc[:, "unit_price"] = df["unit_price"].map(_normalize_numeric_string)
    df.loc[:, "unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")
    return df


def clean_discount_column(df):
    series = df["discount"].astype("string").str.strip()
    series = series.str.replace("%", "", regex=False)
    numeric = pd.to_numeric(series, errors="coerce")
    df.loc[:, "discount"] = numeric.where(numeric <= 1, numeric / 100)
    return df


def clean_weight_column(df):
    weights = df["weight"].astype("string").str.strip().str.lower()
    multipliers = (
        weights.str.extract(r"(kg|g|ton)$", expand=False)
        .map({"kg": 1, "g": 0.001, "ton": 1000})
        .fillna(1)
    )
    values = weights.str.replace(r"\s*(kg|g|ton)$", "", regex=True)
    values = values.str.replace(",", ".", regex=False)
    df.loc[:, "weight"] = pd.to_numeric(values, errors="coerce") * multipliers
    return df


def main():
    df = pd.read_csv(INPUT_FILE, dtype={" Supplier ID ": "string"}, encoding="utf-8-sig")
    df = clean_column_names(df)
    df = clean_supplier_id_column(df)
    df = clean_supplier_column(df)
    df = clean_country_column(df)
    df = clean_city_column(df)
    df = clean_purchase_date_column(df)
    df = clean_amount_column(df)
    df = clean_unit_price_column(df)
    df = clean_weight_column(df)
    df = clean_discount_column(df)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)


if __name__ == "__main__":
    main()
