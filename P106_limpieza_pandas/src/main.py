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
    # Casos tipicos en la columna
    # ' Supplier ID ' -> "supplier_id"
    # 'City ' -> "city"
    # 'Purchase Date' -> "purchase_date"
    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")
    return df


def clean_supplier_id_column(df):
    # Los identificadores son etiquetas: conserva los ceros iniciales.
    df.loc[:, "supplier_id"] = df["supplier_id"].astype("string").str.strip()
    return df


def clean_supplier_column(df):
    df.loc[:, "supplier"] = df["supplier"].str.strip()
    df.loc[:, "supplier"] = df["supplier"].replace(SUPPLIER_REPLACEMENTS)
    return df


def clean_country_column(df):
    df.loc[:, "country"] = df["country"].str.strip()
    df.loc[:, "country"] = df["country"].replace(COUNTRY_REPLACEMENTS)
    return df


def clean_city_column(df):
    df.loc[:, "city"] = df["city"].str.strip()
    df.loc[:, "city"] = df["city"].replace(CITY_REPLACEMENTS)
    return df


def clean_purchase_date_column(df):

    def convert_yyyy_s_mm_s_dd_to_yyyy_mm_dd(series):
        # Convierte fechas en formato "YYYY/MM/DD" a "YYYY-MM-DD"
        series = series.str.replace(r"(\d{4})/(\d{2})/(\d{2})", r"\1-\2-\3", regex=True)
        return series

    def convert_mmddyyyy_to_yyyy_mm_dd(series):
        # Corrige solo fechas con el día primero, cuando el día es mayor que 12.
        def convert_date(match):
            g1, g2, g3 = match.groups()
            if int(g2) > 12:  # el dia aparece en la mitad
                return f"{g3}-{g1}-{g2}"
            return f"{g3}-{g2}-{g1}"

        return series.str.replace(r"(\d{2})/(\d{2})/(\d{4})", convert_date, regex=True)

    def convert_dd_mm_yyyy_to_yyyy_mm_dd_separated_with_dots(series):
        # Corrige fechas en formato "DD.MM.YYYY" a "YYYY-MM-DD"
        return series.str.replace(r"(\d{2})\.(\d{2})\.(\d{4})", r"\3-\2-\1", regex=True)

    def convert_dd_mm_yy_to_yyyy_mm_dd_separated_with_hyphens(series):
        # Corrige fechas en formato "DD-MM-YY" a "YYYY-MM-DD"
        return series.str.replace(
            r"^(\d{2})-(\d{2})-(\d{2})$", r"20\3-\2-\1", regex=True
        )

    df.loc[:, "purchase_date"] = df["purchase_date"].str.strip()
    df.loc[:, "purchase_date"] = convert_yyyy_s_mm_s_dd_to_yyyy_mm_dd(df["purchase_date"])
    df.loc[:, "purchase_date"] = convert_mmddyyyy_to_yyyy_mm_dd(df["purchase_date"])
    df.loc[:, "purchase_date"] = convert_dd_mm_yyyy_to_yyyy_mm_dd_separated_with_dots(
        df["purchase_date"]
    )
    df.loc[:, "purchase_date"] = convert_dd_mm_yy_to_yyyy_mm_dd_separated_with_hyphens(
        df["purchase_date"]
    )

    return df


def _parse_numeric_value(value):
    """Parsea números con separadores de miles/decimales y moneda opcional."""
    if pd.isna(value):
        return pd.NA

    text = str(value).strip()
    if not text or text.upper() in {"N/A", "NA", "NULL"}:
        return pd.NA

    text = re.sub(r"(?i)COP", "", text).replace("$", "").replace(" ", "")
    sign = ""
    if text[:1] in {"+", "-"}:
        sign, text = text[0], text[1:]

    if not text or not text[0].isdigit() or any(char not in "0123456789.," for char in text):
        raise ValueError(f"Valor numérico no válido: {value!r}")

    separators = [index for index, char in enumerate(text) if char in ".,"]
    if not separators:
        return float(sign + text)

    last_separator = separators[-1]
    digits_after_last = len(text) - last_separator - 1
    has_decimal_part = digits_after_last in {1, 2}
    if has_decimal_part:
        integer_part = text[:last_separator].replace(".", "").replace(",", "")
        decimal_part = text[last_separator + 1 :]
        normalized = f"{integer_part}.{decimal_part}"
    else:
        normalized = text.replace(".", "").replace(",", "")

    return float(sign + normalized)


def clean_amount_column(df):
    def parse_amount(value):
        if pd.isna(value):
            return pd.NA

        text = str(value).strip()
        is_thousands = text.upper().endswith("K")
        parsed = _parse_numeric_value(text[:-1] if is_thousands else text)
        if is_thousands and not pd.isna(parsed):
            return parsed * 1000
        return parsed

    df.loc[:, "amount"] = pd.to_numeric(df["amount"].map(parse_amount), errors="raise")
    return df


def clean_unit_price_column(df):
    df.loc[:, "unit_price"] = pd.to_numeric(
        df["unit_price"].map(_parse_numeric_value), errors="raise"
    )
    return df


def clean_discount_column(df):
    def parse_discount(value):
        if pd.isna(value):
            return pd.NA

        text = str(value).strip()
        if not text or text.upper() in {"N/A", "NA", "NULL"}:
            return pd.NA

        has_percent_sign = text.endswith("%")
        if has_percent_sign:
            text = text[:-1].strip()

        try:
            numeric_value = float(text)
        except ValueError as error:
            raise ValueError(f"Descuento no válido: {value!r}") from error

        if has_percent_sign or numeric_value > 1:
            numeric_value /= 100
        return numeric_value

    df.loc[:, "discount"] = pd.to_numeric(
        df["discount"].map(parse_discount), errors="raise"
    )
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
    df = pd.read_csv(INPUT_FILE, dtype="string")
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
    df.to_csv(OUTPUT_FILE, index=False)


if __name__ == "__main__":
    main()
