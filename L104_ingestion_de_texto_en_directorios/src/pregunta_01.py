from pathlib import Path

import pandas as pd


ACTIVITY_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ACTIVITY_DIR / "data"
SUBMISSION_DIR = ACTIVITY_DIR / "submission"


def pregunta_01():
    SUBMISSION_DIR.mkdir(parents=True, exist_ok=True)

    for split in ("train", "test"):
        rows = []
        split_dir = DATA_DIR / split

        for target_dir in sorted(path for path in split_dir.iterdir() if path.is_dir()):
            for file_path in sorted(target_dir.glob("*.txt")):
                phrase = file_path.read_text(encoding="utf-8").strip()
                rows.append({
                    "phrase": phrase,
                    "target": target_dir.name,
                })

        dataset = pd.DataFrame(rows, columns=["phrase", "target"])
        dataset.to_csv(SUBMISSION_DIR / f"{split}_dataset.csv", index=False)
