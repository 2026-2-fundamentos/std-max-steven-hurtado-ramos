from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.ticker import PercentFormatter


ACTIVITY_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = ACTIVITY_DIR / "data" / "sales.csv.gz"
SUBMISSION_DIR = ACTIVITY_DIR / "submission"


def build_cohort_analysis() -> pd.DataFrame:
    data = pd.read_csv(DATA_FILE, compression="gzip")

    # Sin cliente o fecha no se puede asignar una cohorte.
    data["OrderDate"] = pd.to_datetime(data["OrderDate"], errors="coerce")
    data = data.dropna(subset=["CustomerID", "OrderDate"]).copy()

    data["order_month"] = data["OrderDate"].dt.to_period("M")
    first_month = data.groupby("CustomerID")["order_month"].transform("min")

    data["cohort_month"] = first_month.astype(str)
    data["period_index"] = (
        (data["order_month"].dt.year - first_month.dt.year) * 12
        + data["order_month"].dt.month
        - first_month.dt.month
    ).astype(int)

    active_customers = (
        data.groupby(["cohort_month", "period_index"])["CustomerID"]
        .nunique()
        .rename("active_customers")
        .reset_index()
    )

    cohort_sizes = (
        data.groupby("cohort_month")["CustomerID"]
        .nunique()
        .rename("cohort_size")
        .reset_index()
    )

    retention = active_customers.merge(cohort_sizes, on="cohort_month")
    retention["retention_rate"] = (
        retention["active_customers"] / retention["cohort_size"]
    )

    retention = retention[
        [
            "cohort_month",
            "period_index",
            "active_customers",
            "cohort_size",
            "retention_rate",
        ]
    ].sort_values(["cohort_month", "period_index"]).reset_index(drop=True)

    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    retention.to_csv(
        SUBMISSION_DIR / "cohort_retention.csv",
        index=False,
    )

    # Las combinaciones futuras quedan como NaN y aparecen vacías en el mapa.
    heatmap_data = retention.pivot(
        index="cohort_month",
        columns="period_index",
        values="retention_rate",
    )

    values = np.ma.masked_invalid(heatmap_data.to_numpy(dtype=float))
    cmap = plt.get_cmap("Blues").copy()
    cmap.set_bad("white")

    fig_width = max(8, heatmap_data.shape[1] * 0.65)
    fig_height = max(4, heatmap_data.shape[0] * 0.45)
    fig, ax = plt.subplots(figsize=(fig_width, fig_height))

    image = ax.imshow(
        values,
        aspect="auto",
        interpolation="nearest",
        cmap=cmap,
        vmin=0,
        vmax=1,
    )

    ax.set_xticks(np.arange(len(heatmap_data.columns)))
    ax.set_xticklabels(heatmap_data.columns)
    ax.set_yticks(np.arange(len(heatmap_data.index)))
    ax.set_yticklabels(heatmap_data.index)
    ax.set_xlabel("Meses desde la primera compra")
    ax.set_ylabel("Cohorte")
    ax.set_title("Retención de clientes por cohorte")

    colorbar = fig.colorbar(image, ax=ax)
    colorbar.ax.yaxis.set_major_formatter(PercentFormatter(xmax=1))

    # Anota solo los períodos observados; las celdas futuras quedan vacías.
    for row in range(heatmap_data.shape[0]):
        for column in range(heatmap_data.shape[1]):
            value = heatmap_data.iloc[row, column]
            if pd.notna(value):
                text_color = "white" if value >= 0.6 else "black"
                ax.text(
                    column,
                    row,
                    f"{value:.0%}",
                    ha="center",
                    va="center",
                    color=text_color,
                )

    fig.tight_layout()
    fig.savefig(
        SUBMISSION_DIR / "cohort_retention_heatmap.png",
        dpi=150,
        bbox_inches="tight",
    )
    plt.close(fig)

    return retention