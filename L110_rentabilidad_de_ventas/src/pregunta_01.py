from pathlib import Path

import pandas as pd


ACTIVITY_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = ACTIVITY_DIR / "data" / "superstore_orders.csv.gz"
SUBMISSION_DIR = ACTIVITY_DIR / "submission"

DISCOUNT_BANDS = ["0%", "1%-5%", "6%-10%", "más de 10%"]


def pregunta_01() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    data = pd.read_csv(
    DATA_FILE,
    sep=";",
    decimal=",",
    compression="gzip",
)

    loss_mask = data["Profit"] < 0
    total_sales = data["Sales"].sum()

    profitability_summary = pd.DataFrame(
        [
            {
                "lines": len(data),
                "orders": data["Order ID"].nunique(),
                "sales": total_sales,
                "profit": data["Profit"].sum(),
                "profit_margin": data["Profit"].sum() / total_sales,
                "loss_lines": int(loss_mask.sum()),
                "loss_line_rate": float(loss_mask.mean()),
                "lost_profit": -data.loc[loss_mask, "Profit"].sum(),
            }
        ]
    )

    def get_discount_band(discount):
        if discount == 0:
            return "0%"
        if 0 < discount <= 0.05:
            return "1%-5%"
        if 0.05 < discount <= 0.10:
            return "6%-10%"
        return "más de 10%"

    data["discount_band"] = pd.Categorical(
        data["Discount"].map(get_discount_band),
        categories=DISCOUNT_BANDS,
        ordered=True,
    )

    discount_summary = (
        data.groupby("discount_band", observed=True)
        .agg(
            lines=("Profit", "size"),
            sales=("Sales", "sum"),
            profit=("Profit", "sum"),
            loss_line_rate=("Profit", lambda values: (values < 0).mean()),
            lost_profit=(
                "Profit",
                lambda values: -values[values < 0].sum(),
            ),
        )
        .reindex(DISCOUNT_BANDS)
    )
    discount_summary["profit_margin"] = (
        discount_summary["profit"] / discount_summary["sales"]
    )
    discount_summary = discount_summary.reset_index()
    discount_summary = discount_summary[
        [
            "discount_band",
            "lines",
            "sales",
            "profit",
            "profit_margin",
            "loss_line_rate",
            "lost_profit",
        ]
    ]

    priority_segments = (
        data.groupby(
            ["Customer Segment", "Product Category"],
            observed=True,
            as_index=False,
        )
        .agg(
            lines=("Profit", "size"),
            sales=("Sales", "sum"),
            profit=("Profit", "sum"),
            lost_profit=(
                "Profit",
                lambda values: -values[values < 0].sum(),
            ),
        )
    )
    priority_segments = priority_segments[
        priority_segments["lines"] >= 100
    ].copy()
    priority_segments["profit_margin"] = (
        priority_segments["profit"] / priority_segments["sales"]
    )
    priority_segments = (
        priority_segments
        .sort_values("lost_profit", ascending=False)
        .head(5)
        .reset_index(drop=True)
    )
    priority_segments = priority_segments[
        [
            "Customer Segment",
            "Product Category",
            "lines",
            "sales",
            "profit",
            "profit_margin",
            "lost_profit",
        ]
    ]

    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)
    profitability_summary.to_csv(
        SUBMISSION_DIR / "profitability_summary.csv", index=False
    )
    discount_summary.to_csv(
        SUBMISSION_DIR / "discount_summary.csv", index=False
    )
    priority_segments.to_csv(
        SUBMISSION_DIR / "priority_segments.csv", index=False
    )

    return profitability_summary, discount_summary, priority_segments
