## Lab24 Submission Summary (2026-05-12)

### Phase A (RAGAS)

- Faithfulness: 0.7342
- Answer Relevancy: 0.4223
- Context Precision: 0.6728
- Context Recall: 0.5621
- Artifacts:
  - `phase-a/ragas_results.csv`
  - `phase-a/ragas_summary.json`
  - `phase-a/failure_analysis.md`
  - `phase-a/testset_review_notes.md`

### Phase B (LLM Judge + Calibration)

- Pairwise rows: 20
- Winner distribution: tie=12, a=6, b=2
- Cohen's kappa (human vs judge on 10 samples): 1.0000
- Artifacts:
  - `phase-b/pairwise_results.csv`
  - `phase-b/absolute_scores.csv`
  - `phase-b/human_labels.csv`
  - `phase-b/judge_bias_report.md`

### Phase C (Guardrails)

- Latency benchmark rows: 20
- L1 P95: 0.66 ms
- L2 P95: 23574.46 ms
- L3 P95: 1.03 ms
- Total P95: 23575.21 ms
- Artifacts:
  - `phase-c/pii_test_results.csv`
  - `phase-c/adversarial_test_results.csv`
  - `phase-c/latency_benchmark.csv`

### Phase D (Blueprint)

- Final blueprint: `phase-d/blueprint.md`
