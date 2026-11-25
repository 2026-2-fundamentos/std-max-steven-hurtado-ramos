from pathlib import Path

import pandas as pd


ACTIVITY_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = ACTIVITY_DIR / "data" / "flights_by_carrier_day_hour.csv.gz"
SUBMISSION_DIR = ACTIVITY_DIR / "submission"


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame]:
    data = pd.read_csv(DATA_FILE, compression="gzip")

    hourly = (
        data.groupby("scheduled_departure_hour", as_index=False)
        .agg(
            operated_flights=("operated_flights", "sum"),
            delayed_departure_15_flights=(
                "delayed_departure_15_flights",
                "sum",
            ),
        )
        .set_index("scheduled_departure_hour")
        .reindex(range(24), fill_value=0)
        .rename_axis("scheduled_departure_hour")
        .reset_index()
    )
    hourly["delay_rate"] = (
        hourly["delayed_departure_15_flights"] / hourly["operated_flights"]
    )

    data = data.merge(
        hourly[["scheduled_departure_hour", "delay_rate"]].rename(
            columns={"delay_rate": "hourly_delay_rate"}
        ),
        on="scheduled_departure_hour",
        how="left",
    )
    data["expected_delayed_flights"] = (
        data["operated_flights"] * data["hourly_delay_rate"]
    )

    carriers = (
        data.groupby("reporting_airline", as_index=False)
        .agg(
            operated_flights=("operated_flights", "sum"),
            delayed_departure_15_flights=(
                "delayed_departure_15_flights",
                "sum",
            ),
            expected_delayed_flights=("expected_delayed_flights", "sum"),
        )
    )

    carriers = carriers[carriers["operated_flights"] >= 100_000].copy()
    carriers["delay_rate"] = (
        carriers["delayed_departure_15_flights"] / carriers["operated_flights"]
    )
    carriers["observed_to_expected_ratio"] = (
        carriers["delayed_departure_15_flights"]
        / carriers["expected_delayed_flights"]
    )

    carriers["crude_rank"] = (
        carriers["delay_rate"]
        .rank(method="min", ascending=False)
        .astype(int)
    )
    carriers["adjusted_rank"] = (
        carriers["observed_to_expected_ratio"]
        .rank(method="min", ascending=False)
        .astype(int)
    )

    carriers = carriers.sort_values("adjusted_rank").reset_index(drop=True)

    carrier_adjusted_delays = carriers[
        [
            "reporting_airline",
            "operated_flights",
            "delayed_departure_15_flights",
            "delay_rate",
            "expected_delayed_flights",
            "observed_to_expected_ratio",
            "crude_rank",
            "adjusted_rank",
        ]
    ]

    hourly_delay_rates = hourly[
        [
            "scheduled_departure_hour",
            "operated_flights",
            "delayed_departure_15_flights",
            "delay_rate",
        ]
    ]

    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    hourly_delay_rates.to_csv(
        SUBMISSION_DIR / "hourly_delay_rates.csv",
        index=False,
    )
    carrier_adjusted_delays.to_csv(
        SUBMISSION_DIR / "carrier_adjusted_delays.csv",
        index=False,
    )

    return hourly_delay_rates, carrier_adjusted_delays