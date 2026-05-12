"""Run RAG evaluation and export Phase A artifacts.

Usage:
  python scripts/run_eval.py
  python scripts/run_eval.py --output-dir phase-a
  python scripts/run_eval.py --threshold faithfulness=0.75 --threshold answer_relevancy=0.70
"""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from statistics import mean
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.pipeline import build_pipeline, run_query  # noqa: E402
from src.m4_eval import evaluate_ragas, failure_analysis, load_test_set  # noqa: E402


METRICS = [
    "faithfulness",
    "answer_relevancy",
    "context_precision",
    "context_recall",
]


def clean_score(value: object) -> float:
    try:
        v = float(value)
    except (TypeError, ValueError):
        return 0.0
    if math.isnan(v) or math.isinf(v):
        return 0.0
    return v


def parse_threshold(items: list[str]) -> dict[str, float]:
    thresholds: dict[str, float] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"Invalid threshold format: {item}. Use metric=value.")
        metric, value = item.split("=", 1)
        metric = metric.strip()
        if metric not in METRICS:
            raise ValueError(f"Unknown metric for threshold: {metric}")
        thresholds[metric] = float(value.strip())
    return thresholds


def export_results(
    output_dir: Path,
    eval_results: dict,
    raw_rows: list[dict],
) -> tuple[Path, Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)

    per_question = eval_results.get("per_question", [])

    results_csv = output_dir / "ragas_results.csv"
    with results_csv.open("w", encoding="utf-8", newline="") as f:
        f.write(
            "question,answer,ground_truth,contexts,faithfulness,answer_relevancy,context_precision,context_recall,avg_score\n"
        )
        for row, score in zip(raw_rows, per_question):
            f_score = clean_score(score.faithfulness)
            ar_score = clean_score(score.answer_relevancy)
            cp_score = clean_score(score.context_precision)
            cr_score = clean_score(score.context_recall)
            avg_score = mean(
                [
                    f_score,
                    ar_score,
                    cp_score,
                    cr_score,
                ]
            )
            line = [
                json.dumps(row["question"], ensure_ascii=False),
                json.dumps(row["answer"], ensure_ascii=False),
                json.dumps(row["ground_truth"], ensure_ascii=False),
                json.dumps(row["contexts"], ensure_ascii=False),
                f"{f_score:.6f}",
                f"{ar_score:.6f}",
                f"{cp_score:.6f}",
                f"{cr_score:.6f}",
                f"{avg_score:.6f}",
            ]
            f.write(",".join(line) + "\n")

    summary_json = output_dir / "ragas_summary.json"
    with summary_json.open("w", encoding="utf-8") as f:
        json.dump(
            {metric: clean_score(eval_results.get(metric, 0.0)) for metric in METRICS},
            f,
            ensure_ascii=False,
            indent=2,
        )

    for score in per_question:
        score.faithfulness = clean_score(score.faithfulness)
        score.answer_relevancy = clean_score(score.answer_relevancy)
        score.context_precision = clean_score(score.context_precision)
        score.context_recall = clean_score(score.context_recall)

    failures = failure_analysis(per_question, bottom_n=10)
    scored_rows = []
    for row, score in zip(raw_rows, per_question):
        avg_score = mean(
            [
                clean_score(score.faithfulness),
                clean_score(score.answer_relevancy),
                clean_score(score.context_precision),
                clean_score(score.context_recall),
            ]
        )
        scored_rows.append((avg_score, row.get("question", "")))
    scored_rows.sort(key=lambda x: x[0])
    failure_md = output_dir / "failure_analysis.md"
    with failure_md.open("w", encoding="utf-8") as f:
        f.write("# Failure Cluster Analysis\n\n")
        f.write("## Bottom 10 Questions\n\n")
        f.write("| # | Question | Worst Metric | Score | Avg | Diagnosis | Suggested Fix |\n")
        f.write("|---|---|---|---:|---:|---|---|\n")
        for idx, item in enumerate(failures, start=1):
            question = scored_rows[idx - 1][1] if idx - 1 < len(scored_rows) else item.get("question", "")
            question = question.replace("\n", " ").strip()
            if len(question) > 120:
                question = question[:117] + "..."
            f.write(
                f"| {idx} | {question} | {item['worst_metric']} | {item['score']:.4f} | "
                f"{item['avg_score']:.4f} | {item['diagnosis']} | {item['suggested_fix']} |\n"
            )

    return results_csv, summary_json, failure_md


def run_eval(output_dir: Path, thresholds: dict[str, float]) -> int:
    print("Building RAG pipeline...")
    search, reranker = build_pipeline()

    print("\nRunning eval set queries...")
    test_set = load_test_set()
    rows: list[dict] = []
    questions: list[str] = []
    answers: list[str] = []
    contexts: list[list[str]] = []
    ground_truths: list[str] = []

    for idx, item in enumerate(test_set, start=1):
        answer, ctx = run_query(item["question"], search, reranker)
        questions.append(item["question"])
        answers.append(answer)
        contexts.append(ctx)
        ground_truths.append(item["ground_truth"])
        rows.append(
            {
                "question": item["question"],
                "answer": answer,
                "ground_truth": item["ground_truth"],
                "contexts": ctx,
            }
        )
        print(f"[{idx}/{len(test_set)}] {item['question'][:80]}")

    print("\nComputing RAGAS metrics...")
    results = evaluate_ragas(questions, answers, contexts, ground_truths)
    results_csv, summary_json, failure_md = export_results(output_dir, results, rows)

    print("\nAggregate metrics:")
    for metric in METRICS:
        print(f"- {metric}: {results.get(metric, 0):.4f}")
    print(f"\nArtifacts:\n- {results_csv}\n- {summary_json}\n- {failure_md}")

    failed = []
    for metric, threshold in thresholds.items():
        actual = float(results.get(metric, 0.0))
        if actual < threshold:
            failed.append((metric, actual, threshold))

    if failed:
        print("\nThreshold check FAILED:")
        for metric, actual, threshold in failed:
            print(f"- {metric}: actual={actual:.4f} < threshold={threshold:.4f}")
        return 1

    if thresholds:
        print("\nThreshold check PASSED.")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="phase-a")
    parser.add_argument(
        "--threshold",
        action="append",
        default=[],
        help="Repeatable metric threshold, e.g. --threshold faithfulness=0.75",
    )
    args = parser.parse_args()

    thresholds = parse_threshold(args.threshold)
    return run_eval(Path(args.output_dir), thresholds)


if __name__ == "__main__":
    raise SystemExit(main())
