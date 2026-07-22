# Paper v1 — frozen artifact

Everything under this directory is a **frozen snapshot** of the v1 experiment.
Nothing here changes across future paper iterations. When we run v2 (more
experiments, corrections, extensions), we snapshot again into `paper-v2/`
without touching this folder.

## Contents

```
paper-v1/
├── README.md               ← you are here
├── FINDINGS.md             top-level executive summary of every finding
├── LIMITATIONS.md          contamination, Kimi truncation, and other honest caveats
├── dataset/                the exact 750-item dataset used
│   ├── combined.jsonl
│   ├── combined.jsonl.md5
│   └── DATASET_README.md
├── config/
│   └── experiment.yaml     the exact model list + rate limits + temperatures
├── raw/                                the 9,549 responses used in the final analysis
│   ├── responses.jsonl                              ← final: 9,549 rows, LLM-parsed, reprompted, filtered
│   ├── responses.pre-final-filter.jsonl.bak         ← 11,250 rows before the filter
│   ├── responses.pre-reprompt-56.jsonl.bak          ← state before reprompting the 56 disagreements
│   ├── responses.v1-scoring.jsonl.bak               ← original scoring (v0.1 parser bug, audit)
│   ├── errors.parquet                               ← M × N binary error matrix (final)
│   ├── rho_by_domain.json                           ← ρ, N_eff, cluster analysis per cell (final)
│   ├── report.md                                    ← human-readable full report (final)
│   └── progress.json                                ← end-of-run counters
│
│   The `raw_response` field is byte-identical across every backup that
│   didn't involve a reprompt. Only derived fields (`parsed_answer`,
│   `error`) differ across parser generations.
├── analysis/               ← the five analyses that produced the paper's findings
│   ├── 00_parser_correction.md      the QA-caught parser bug + full recovery
│   ├── 01_headline_rho.md
│   ├── 02_kimi_confound.md          v0.1 story dissolved by parser fix
│   ├── 03_overconfidence_gap.md
│   ├── 04_crossculture_finding.md
│   └── 05_committee_selection.md    post-freeze: enumeration, transfer
│                                    failure, and the DEFT algorithm
│                                    (reads frozen raw/ only)
├── committee-selection/    post-freeze DEFT result tables (report.md,
│                           committees.csv, selection_eval.json,
│                           calibration_by_committee.csv)
├── figures/                (empty in v1 — figures ship with v2)
└── paper/
    └── draft.md            paper skeleton grown out of the FINDINGS.md
```

## Reproduce v1 from scratch

```bash
# 1. Verify frozen dataset checksum
md5 -c paper-v1/dataset/combined.jsonl.md5

# 2. Point the runner at the frozen config
rho-collapse run --config paper-v1/config/experiment.yaml --data paper-v1/dataset/combined.jsonl

# The paper-v1/raw/ files are the exact outputs of that run.
```

The run took 7 hours 20 minutes wall-clock on OpenRouter with the rate
limits in `config/experiment.yaml`. Cost: ~$12.

## Sweep summary

| | Value |
|---|---|
| Started | 2026-07-18T19:18:12Z |
| Completed | 2026-07-19T02:22 UTC (7h 4m) |
| Total completions | 11,250 |
| Runner failures | 0 |
| Domains | science (250) + medicine (250) + law (250) = 750 items |
| Conditions | D1 same-model (T=0.7) + D2 cross-family Chinese (T=0) + D3 cross-culture (T=0) |
| Committee | 5 agents per condition |
| Models | DeepSeek V4, Kimi K2, Qwen 3 235B, GLM 4.6, ByteDance Seed 1.6, Claude Sonnet 4.6, GPT-5-mini, Gemini 2.5 Pro |

## Start here

- **[`FINDINGS.md`](./FINDINGS.md)** — every finding worth writing a paper about
- **[`LIMITATIONS.md`](./LIMITATIONS.md)** — every threat to validity we know about
- **[`raw/report.md`](./raw/report.md)** — the automatic full report

## Version control

This entire folder is tracked in the `agreeing-llms` GitHub repo. The
commit tagged `paper-v1-data` corresponds to exactly this state. Later
paper versions get their own folders (`paper-v2/`, `paper-v3/`) and their
own git tags so cross-version diffing is trivial.
