from pathlib import Path

import numpy as np
import pandas as pd


ACTIVITY_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ACTIVITY_DIR / "data"
SUBMISSION_DIR = ACTIVITY_DIR / "submission"

DAY_ORDER = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
]


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    # Lee cada canal y elimina solamente las filas idénticas dentro de ese canal.
    web = pd.read_csv(
        DATA_DIR / "historical_requests_web.csv.gz",
        compression="gzip",
    ).drop_duplicates()
    web["channel"] = "web"

    letter = pd.read_csv(
        DATA_DIR / "historical_requests_letter.csv.gz",
        compression="gzip",
    ).drop_duplicates()
    letter["channel"] = "letter"

    data = pd.concat([letter, web], ignore_index=True)

    data["in_date"] = pd.to_datetime(data["in_date"], errors="coerce").dt.normalize()
    data["out_date"] = pd.to_datetime(data["out_date"], errors="coerce").dt.normalize()

    # El día de la semana se obtiene de la fecha de entrada para asegurar el orden.
    data["day_name"] = data["in_date"].dt.day_name()
    data["year"] = data["in_date"].dt.year

    answered_mask = data["out_date"].notna()

    data["calendar_days"] = np.nan
    data.loc[answered_mask, "calendar_days"] = (
        data.loc[answered_mask, "out_date"]
        - data.loc[answered_mask, "in_date"]
    ).dt.days

    # Cuenta los días hábiles posteriores a la entrada, incluyendo la respuesta.
    data["business_days"] = np.nan
    start_dates = data.loc[answered_mask, "in_date"].to_numpy(
        dtype="datetime64[D]"
    )
    end_dates = data.loc[answered_mask, "out_date"].to_numpy(
        dtype="datetime64[D]"
    )
    data.loc[answered_mask, "business_days"] = np.busday_count(
        start_dates + np.timedelta64(1, "D"),
        end_dates + np.timedelta64(1, "D"),
    )

    data["pending"] = ~answered_mask
    data["on_time"] = (
        answered_mask & data["business_days"].le(15)
    )

    # Resumen por canal.
    channel_rows = []
    for channel, group in data.groupby("channel", sort=True):
        answered = group.loc[group["out_date"].notna()]

        channel_rows.append(
            {
                "channel": channel,
                "requests": len(group),
                "answered": len(answered),
                "pending": int(group["pending"].sum()),
                "median_business_days": answered["business_days"].median(),
                "on_time_rate": group["on_time"].mean(),
            }
        )

    channel_summary = pd.DataFrame(
        channel_rows,
        columns=[
            "channel",
            "requests",
            "answered",
            "pending",
            "median_business_days",
            "on_time_rate",
        ],
    )

    # Resumen por año de entrada y canal.
    yearly_summary = (
        data.groupby(["year", "channel"], as_index=False, sort=True)
        .agg(
            requests=("channel", "size"),
            pending=("pending", "sum"),
            on_time_rate=("on_time", "mean"),
        )
        .sort_values(["year", "channel"])
        .reset_index(drop=True)
    )
    yearly_summary["pending"] = yearly_summary["pending"].astype(int)

    # Resumen por día de entrada, combinando los dos canales.
    entry_day_summary = (
        data.groupby("day_name", sort=False)
        .agg(
            requests=("channel", "size"),
            median_calendar_days=("calendar_days", "median"),
            median_business_days=("business_days", "median"),
        )
        .reindex(DAY_ORDER)
        .rename_axis("day_name")
        .reset_index()
    )
    entry_day_summary["requests"] = (
        entry_day_summary["requests"].fillna(0).astype(int)
    )

    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)

    channel_summary.to_csv(
        SUBMISSION_DIR / "channel_summary.csv",
        index=False,
    )
    yearly_summary.to_csv(
        SUBMISSION_DIR / "yearly_summary.csv",
        index=False,
    )
    entry_day_summary.to_csv(
        SUBMISSION_DIR / "entry_day_summary.csv",
        index=False,
    )

    return channel_summary, yearly_summary, entry_day_summary