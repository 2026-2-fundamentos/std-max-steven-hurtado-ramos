import json
from pathlib import Path

import pandas as pd


ACTIVITY_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = ACTIVITY_DIR / "data" / "insurance.csv.gz"
SUBMISSION_DIR = ACTIVITY_DIR / "submission"

K = 5


def pregunta_01():
    data = pd.read_csv(DATA_FILE, compression="gzip")

    original_identifiers = ["age", "sex", "bmi", "children", "region"]
    original_sizes = data.groupby(
        original_identifiers, dropna=False
    ).size()

    report = {
        "original_k": int(original_sizes.min()),
        "original_unique_records": int(original_sizes[original_sizes == 1].sum()),
        "schemes": {},
    }

    data["age_group"] = pd.cut(
        data["age"],
        bins=[18, 30, 40, 50, 65],
        labels=["18-29", "30-39", "40-49", "50-64"],
        right=False,
    )

    data["bmi_group"] = pd.cut(
        data["bmi"],
        bins=[float("-inf"), 18.5, 25, 30, float("inf")],
        labels=["bajo peso", "normal", "sobrepeso", "obesidad"],
        right=False,
    )

    def group_children(children):
        if children == 0:
            return "0"
        if children <= 2:
            return "1-2"
        return "3+"

    data["children_group"] = data["children"].map(group_children)

    schemes = {
        "with_children": [
            "age_group",
            "sex",
            "bmi_group",
            "children_group",
            "region",
        ],
        "without_children": [
            "age_group",
            "sex",
            "bmi_group",
            "region",
        ],
    }

    published_by_scheme = {}

    for name, identifiers in schemes.items():
        grouped = data.groupby(identifiers, observed=True, dropna=False)
        group_sizes = grouped.size()
        smoker_counts = grouped["smoker"].nunique()

        publishable_sizes = group_sizes[group_sizes >= K]
        no_diversity = publishable_sizes.index[
            smoker_counts.loc[publishable_sizes.index] == 1
        ]

        row_group_sizes = grouped["smoker"].transform("size")
        published = data.loc[
            row_group_sizes >= K,
            identifiers + ["smoker", "charges"],
        ].copy()

        report["schemes"][name] = {
            "quasi_identifiers": identifiers,
            "equivalence_classes": int(len(group_sizes)),
            "k_before_suppression": int(group_sizes.min()),
            "suppressed_records": int(group_sizes[group_sizes < K].sum()),
            "published_records": int(publishable_sizes.sum()),
            "published_classes": int(len(publishable_sizes)),
            "classes_without_smoker_diversity": int(len(no_diversity)),
            "records_without_smoker_diversity": int(
                publishable_sizes.loc[no_diversity].sum()
            ),
        }
        published_by_scheme[name] = published

    selected_scheme = min(
        schemes,
        key=lambda name: report["schemes"][name]["suppressed_records"],
    )
    published = published_by_scheme[selected_scheme]

    report["selected_scheme"] = selected_scheme
    report["mean_charges_original"] = float(data["charges"].mean())
    report["mean_charges_published"] = float(published["charges"].mean())
    report["smoker_rate_original"] = float((data["smoker"] == "yes").mean())
    report["smoker_rate_published"] = float(
        (published["smoker"] == "yes").mean()
    )

    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)

    with (SUBMISSION_DIR / "privacy_report.json").open(
        "w", encoding="utf-8"
    ) as file:
        json.dump(report, file, indent=2, ensure_ascii=False)

    published.to_csv(
        SUBMISSION_DIR / "insurance_published.csv",
        index=False,
    )

    return report
