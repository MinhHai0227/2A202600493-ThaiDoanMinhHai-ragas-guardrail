# Prompt Log

| Date | Tool | Prompt summary | Files affected |
|---|---|---|---|
| 2026-05-12 | Codex | Scaffold Phase A/B/C/D folders and scripts for Lab 24 submission structure. | `scripts/run_eval.py`, `phase-*`, `.github/workflows/eval-gate.yml` |
| 2026-05-12 | Codex | Patch Qdrant HTTP/API key connection to fix SSL and auth issues in dense search. | `src/m2_search.py`, `config.py` |
| 2026-05-12 | Codex | Patch RAGAS eval pipeline with explicit LLM/embeddings wrappers and NaN-safe export. | `src/m4_eval.py`, `scripts/run_eval.py` |
| 2026-05-12 | Codex | Generate Phase B auto-judge script (pairwise + absolute) and kappa workflow support. | `scripts/run_phase_b.py`, `phase-b/*` |
| 2026-05-12 | Codex | Fill Phase C result templates and update Phase D blueprint with benchmark-derived latency values. | `phase-c/*.csv`, `phase-d/blueprint.md` |

## Notes
- Human labels in `phase-b/human_labels.csv` were manually curated from judge outputs.
- All prompts/actions are logged at high level for academic integrity traceability.
