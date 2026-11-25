from pathlib import Path

import pandas as pd


ACTIVITY_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ACTIVITY_DIR / "data"
SUBMISSION_DIR = ACTIVITY_DIR / "submission"


def clean_campaign_data() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    files = sorted(DATA_DIR.glob("bank-marketing-campaing-*.csv.gz"))
    data = pd.concat(
        [pd.read_csv(file, compression="gzip") for file in files],
        ignore_index=True,
    )

    client = data[
        [
            "client_id",
            "age",
            "job",
            "marital",
            "education",
            "credit_default",
            "mortgage",
        ]
    ].copy()

    client["job"] = (
        client["job"]
        .str.replace(".", "", regex=False)
        .str.replace("-", "_", regex=False)
    )
    client["education"] = (
        client["education"]
        .str.replace(".", "_", regex=False)
        .replace("unknown", pd.NA)
    )

    for column in ["credit_default", "mortgage"]:
        client[column] = (client[column] == "yes").astype(int)

    month_numbers = {
        "jan": 1,
        "feb": 2,
        "mar": 3,
        "apr": 4,
        "may": 5,
        "jun": 6,
        "jul": 7,
        "aug": 8,
        "sep": 9,
        "oct": 10,
        "nov": 11,
        "dec": 12,
    }

    date_parts = pd.DataFrame(
        {
            "year": 2022,
            "month": data["month"].str.lower().map(month_numbers),
            "day": data["day"],
        }
    )
    last_contact_date = pd.to_datetime(date_parts).dt.strftime("%Y-%m-%d")

    campaign = pd.DataFrame(
        {
            "client_id": data["client_id"],
            "number_contacts": data["number_contacts"],
            "contact_duration": data["contact_duration"],
            "previous_campaign_contacts": data["previous_campaign_contacts"],
            "previous_outcome": (data["previous_outcome"] == "success").astype(int),
            "campaign_outcome": (data["campaign_outcome"] == "yes").astype(int),
            "last_contact_date": last_contact_date,
        }
    )

    economics = data[
        ["client_id", "cons_price_idx", "euribor_three_months"]
    ].copy()

    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    client.to_csv(SUBMISSION_DIR / "client.csv", index=False)
    campaign.to_csv(SUBMISSION_DIR / "campaign.csv", index=False)
    economics.to_csv(SUBMISSION_DIR / "economics.csv", index=False)

    return client, campaign, economics