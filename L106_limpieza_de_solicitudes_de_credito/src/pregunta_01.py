from pathlib import Path

import pandas as pd


ACTIVITY_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = ACTIVITY_DIR / "data" / "solicitudes_de_credito.csv.gz"
OUTPUT_FILE = ACTIVITY_DIR / "submission" / "solicitudes_de_credito.csv"

COLUMNS = [
    "sexo",
    "tipo_de_emprendimiento",
    "idea_negocio",
    "barrio",
    "estrato",
    "comuna_ciudadano",
    "fecha_de_beneficio",
    "monto_del_credito",
    "línea_credito",
]

TEXT_COLUMNS = [
    "sexo",
    "tipo_de_emprendimiento",
    "idea_negocio",
    "barrio",
    "línea_credito",
]


def pregunta_01():
    data = pd.read_csv(DATA_FILE, sep=";", compression="gzip")

    data.columns = (
        data.columns.astype(str)
        .str.replace("\ufeff", "", regex=False)
        .str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
    )
    data = data[COLUMNS].copy()

    # Este bloque debe quedar dentro de la función.
    for column in TEXT_COLUMNS:
        data[column] = (
            data[column]
            .astype("string")
            .str.lower()
            .str.replace("-", " ", regex=False)
            .str.replace(r"\s+", " ", regex=True)
            .str.strip()
            .replace("", pd.NA)
        )

    estrato = data["estrato"].astype("string").str.extract(
        r"(-?\d+)", expand=False
    )
    data["estrato"] = pd.to_numeric(
        estrato, errors="coerce"
    ).astype("Int64")

    monto = (
        data["monto_del_credito"]
        .astype("string")
        .str.strip()
        .str.replace(r"\.00$", "", regex=True)
        .str.replace(r"[^\d-]", "", regex=True)
        .replace("", pd.NA)
    )
    data["monto_del_credito"] = pd.to_numeric(
        monto, errors="coerce"
    ).astype("Int64")

    comuna = data["comuna_ciudadano"].astype("string").str.strip()
    data["comuna_ciudadano"] = pd.to_numeric(
        comuna, errors="coerce"
    ).astype("Int64")

    date_text = data["fecha_de_beneficio"].astype("string").str.strip()
    dates = pd.to_datetime(
        date_text, format="%d/%m/%Y", errors="coerce"
    )

    for date_format in ("%Y-%m-%d", "%Y/%m/%d"):
        dates = dates.fillna(
            pd.to_datetime(date_text, format=date_format, errors="coerce")
        )

    data["fecha_de_beneficio"] = dates.dt.strftime("%Y-%m-%d")

    required_columns = [
        column for column in COLUMNS
        if column != "comuna_ciudadano"
    ]
    data = data.dropna(subset=required_columns)
    data = data.drop_duplicates(subset=COLUMNS)

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(OUTPUT_FILE, sep=";", index=False)