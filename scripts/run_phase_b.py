"""Generate Phase B artifacts: pairwise judge + absolute scoring.

Usage:
  python scripts/run_phase_b.py
  python scripts/run_phase_b.py --num-questions 30
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from openai import OpenAI  # noqa: E402

from config import OPENAI_API_KEY, OPENAI_CHAT_MODEL, RERANK_TOP_K  # noqa: E402
from src.m4_eval import load_test_set  # noqa: E402
from src.pipeline import build_pipeline, generate_answer, run_query  # noqa: E402


PAIRWISE_PROMPT = """You are an impartial evaluator. Compare two answers to the same question.

Question:
{question}

Answer A:
{answer_a}

Answer B:
{answer_b}

Rate based on:
1) factual accuracy
2) relevance to question
3) conciseness

Return JSON only:
{{
  "winner": "A" | "B" | "tie",
  "reason": "short reason"
}}
"""


ABSOLUTE_PROMPT = """You are an evaluator scoring one answer to a question.

Question:
{question}

Answer:
{answer}

Score each dimension from 0.0 to 1.0:
- accuracy
- relevance
- groundedness
- conciseness

Return JSON only:
{{
  "accuracy": 0.0,
  "relevance": 0.0,
  "groundedness": 0.0,
  "conciseness": 0.0
}}
"""


def parse_json_safe(text: str, fallback: dict) -> dict:
    cleaned = text.strip().replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return fallback


def normalize_winner(v: str) -> str:
    v = (v or "").strip().lower()
    if v in {"a", "answer_a"}:
        return "a"
    if v in {"b", "answer_b"}:
        return "b"
    return "tie"


def judge_pairwise(client: OpenAI, model: str, question: str, ans_a: str, ans_b: str) -> tuple[str, str, str, str]:
    # run 1
    out1 = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[{"role": "user", "content": PAIRWISE_PROMPT.format(question=question, answer_a=ans_a, answer_b=ans_b)}],
    )
    r1 = parse_json_safe(out1.choices[0].message.content or "", {"winner": "tie", "reason": "parse_error"})
    w1 = normalize_winner(str(r1.get("winner", "tie")))
    reason1 = str(r1.get("reason", ""))

    # run 2 (swap)
    out2 = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[{"role": "user", "content": PAIRWISE_PROMPT.format(question=question, answer_a=ans_b, answer_b=ans_a)}],
    )
    r2 = parse_json_safe(out2.choices[0].message.content or "", {"winner": "tie", "reason": "parse_error"})
    w2_raw = normalize_winner(str(r2.get("winner", "tie")))
    reason2 = str(r2.get("reason", ""))
    if w2_raw == "a":
        w2 = "b"
    elif w2_raw == "b":
        w2 = "a"
    else:
        w2 = "tie"

    winner_final = w1 if w1 == w2 else "tie"
    return w1, w2, winner_final, (reason1 or reason2 or "no_reason")


def score_absolute(client: OpenAI, model: str, question: str, answer: str) -> dict:
    out = client.chat.completions.create(
        model=model,
        temperature=0,
        messages=[{"role": "user", "content": ABSOLUTE_PROMPT.format(question=question, answer=answer)}],
    )
    parsed = parse_json_safe(
        out.choices[0].message.content or "",
        {"accuracy": 0.0, "relevance": 0.0, "groundedness": 0.0, "conciseness": 0.0},
    )

    def f(key: str) -> float:
        try:
            v = float(parsed.get(key, 0.0))
        except (TypeError, ValueError):
            return 0.0
        return max(0.0, min(1.0, v))

    return {
        "accuracy": f("accuracy"),
        "relevance": f("relevance"),
        "groundedness": f("groundedness"),
        "conciseness": f("conciseness"),
    }


def answer_without_rerank(question: str, search) -> tuple[str, list[str]]:
    results = search.search(question)
    contexts = [r.text for r in results[:RERANK_TOP_K]]
    return generate_answer(question, contexts), contexts


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--num-questions", type=int, default=30)
    args = parser.parse_args()

    if not OPENAI_API_KEY:
        raise RuntimeError("OPENAI_API_KEY is missing in environment.")

    client = OpenAI(api_key=OPENAI_API_KEY)
    model = OPENAI_CHAT_MODEL

    phase_b_dir = ROOT / "phase-b"
    phase_b_dir.mkdir(parents=True, exist_ok=True)

    print("Building pipeline for Phase B...")
    search, reranker = build_pipeline()
    test_set = load_test_set()[: args.num_questions]

    pairwise_path = phase_b_dir / "pairwise_results.csv"
    absolute_path = phase_b_dir / "absolute_scores.csv"
    human_path = phase_b_dir / "human_labels.csv"

    with pairwise_path.open("w", encoding="utf-8", newline="") as pf, absolute_path.open(
        "w", encoding="utf-8", newline=""
    ) as af:
        p_writer = csv.DictWriter(
            pf,
            fieldnames=["question", "winner_run1", "winner_run2", "winner_final", "reason"],
        )
        a_writer = csv.DictWriter(
            af,
            fieldnames=["question", "accuracy", "relevance", "groundedness", "conciseness", "overall"],
        )
        p_writer.writeheader()
        a_writer.writeheader()

        for idx, item in enumerate(test_set, start=1):
            q = item["question"]

            ans_a, _ = run_query(q, search, reranker)
            ans_b, _ = answer_without_rerank(q, search)

            w1, w2, wf, reason = judge_pairwise(client, model, q, ans_a, ans_b)
            p_writer.writerow(
                {
                    "question": q,
                    "winner_run1": w1,
                    "winner_run2": w2,
                    "winner_final": wf,
                    "reason": reason.replace("\n", " "),
                }
            )

            abs_scores = score_absolute(client, model, q, ans_a)
            overall = (
                abs_scores["accuracy"]
                + abs_scores["relevance"]
                + abs_scores["groundedness"]
                + abs_scores["conciseness"]
            ) / 4
            a_writer.writerow(
                {
                    "question": q,
                    "accuracy": f"{abs_scores['accuracy']:.4f}",
                    "relevance": f"{abs_scores['relevance']:.4f}",
                    "groundedness": f"{abs_scores['groundedness']:.4f}",
                    "conciseness": f"{abs_scores['conciseness']:.4f}",
                    "overall": f"{overall:.4f}",
                }
            )
            print(f"[{idx}/{len(test_set)}] done")

    # Seed human label file with first 10 questions for manual calibration.
    with human_path.open("w", encoding="utf-8", newline="") as hf:
        writer = csv.DictWriter(hf, fieldnames=["question", "human_winner", "confidence", "notes"])
        writer.writeheader()
        for item in test_set[:10]:
            writer.writerow(
                {
                    "question": item["question"],
                    "human_winner": "",
                    "confidence": "",
                    "notes": "",
                }
            )

    print(f"\nSaved:\n- {pairwise_path}\n- {absolute_path}\n- {human_path}")
    print("Next: fill phase-b/human_labels.csv then run: python phase-b/kappa_analysis.py")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
