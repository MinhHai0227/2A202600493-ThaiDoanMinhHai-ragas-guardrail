"""Compute Cohen's kappa from phase-b/human_labels.csv and pairwise_results.csv.

Primary matching key: question text.
Fallback: row-order alignment (useful when encoding issues break exact text matches).
"""

from __future__ import annotations

import csv
from pathlib import Path

from sklearn.metrics import cohen_kappa_score


ROOT = Path(__file__).resolve().parents[1]
HUMAN_FILE = ROOT / "phase-b" / "human_labels.csv"
JUDGE_FILE = ROOT / "phase-b" / "pairwise_results.csv"


def load_labels(path: Path, question_key: str, label_key: str) -> tuple[dict[str, str], list[str]]:
    labels: dict[str, str] = {}
    ordered: list[str] = []

    def pick(row: dict, key: str) -> str:
        if key in row:
            return row.get(key) or ""
        key_norm = key.strip().lower()
        for k, v in row.items():
            if (k or "").strip().lower().lstrip("\ufeff") == key_norm:
                return v or ""
        return ""

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            q = pick(row, question_key).strip()
            label = pick(row, label_key).strip().lower()
            if q and label:
                labels[q] = label
                ordered.append(label)
    return labels, ordered


def normalize(label: str) -> str:
    if label in {"a", "answer_a"}:
        return "a"
    if label in {"b", "answer_b"}:
        return "b"
    return "tie"


def main() -> None:
    human, human_ordered = load_labels(HUMAN_FILE, "question", "human_winner")
    judge, judge_ordered = load_labels(JUDGE_FILE, "question", "winner_final")

    overlap = sorted(set(human) & set(judge))
    if overlap:
        y_human = [normalize(human[q]) for q in overlap]
        y_judge = [normalize(judge[q]) for q in overlap]
        compare_mode = "question_text"
    else:
        n = min(len(human_ordered), len(judge_ordered))
        if n == 0:
            print("No overlapping labels between human and judge files.")
            return
        y_human = [normalize(x) for x in human_ordered[:n]]
        y_judge = [normalize(x) for x in judge_ordered[:n]]
        compare_mode = "row_order_fallback"

    kappa = cohen_kappa_score(y_human, y_judge)
    print(f"Compare mode: {compare_mode}")
    print(f"Questions compared: {len(y_human)}")
    print(f"Cohen's kappa: {kappa:.4f}")


if __name__ == "__main__":
    main()
