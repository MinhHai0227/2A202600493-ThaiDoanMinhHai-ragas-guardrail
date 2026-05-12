"""Phase C full guardrail stack integration benchmark."""

from __future__ import annotations

import csv
import time
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
PHASE_C_DIR = ROOT / "phase-c"
if str(PHASE_C_DIR) not in sys.path:
    sys.path.insert(0, str(PHASE_C_DIR))

from input_guard import InputGuard  # type: ignore # noqa: E402
from output_guard import OutputGuard  # type: ignore # noqa: E402
from src.pipeline import build_pipeline, run_query  # noqa: E402
from src.m4_eval import load_test_set  # noqa: E402


def benchmark(output_file: Path, num_queries: int = 20) -> None:
    search, reranker = build_pipeline()
    input_guard = InputGuard()
    output_guard = OutputGuard()
    dataset = load_test_set()[:num_queries]

    rows = []
    for item in dataset:
        user_q = item["question"]

        t0 = time.perf_counter()
        input_result = input_guard.check(user_q)
        l1_ms = (time.perf_counter() - t0) * 1000
        if not input_result.ok:
            rows.append(
                {
                    "question": user_q,
                    "allowed": False,
                    "output_safe": False,
                    "l1_ms": round(l1_ms, 2),
                    "l2_ms": 0.0,
                    "l3_ms": 0.0,
                    "total_ms": round(l1_ms, 2),
                }
            )
            continue

        t0 = time.perf_counter()
        answer, _ = run_query(input_result.sanitized_text, search, reranker)
        l2_ms = (time.perf_counter() - t0) * 1000

        t0 = time.perf_counter()
        out_result = output_guard.check(user_q, answer)
        l3_ms = (time.perf_counter() - t0) * 1000

        total_ms = l1_ms + l2_ms + l3_ms
        rows.append(
            {
                "question": user_q,
                "allowed": True,
                "output_safe": out_result.safe,
                "l1_ms": round(l1_ms, 2),
                "l2_ms": round(l2_ms, 2),
                "l3_ms": round(l3_ms, 2),
                "total_ms": round(total_ms, 2),
            }
        )

    output_file.parent.mkdir(parents=True, exist_ok=True)
    with output_file.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["question", "allowed", "output_safe", "l1_ms", "l2_ms", "l3_ms", "total_ms"],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"Saved benchmark rows: {len(rows)} -> {output_file}")


if __name__ == "__main__":
    benchmark(ROOT / "phase-c" / "latency_benchmark.csv", num_queries=20)
