# ρ-collapse

**Measure inter-agent error correlation in multi-agent LLM committees.**

The claim: when N LLM agents agree on a factual answer, the common
justification treats that agreement like N independent votes (Condorcet's
Jury Theorem). But LLMs share pretraining and instruction-tuning, so their
errors are correlated. This package measures the correlation `ρ` across
three domains, computes the effective committee size
`N_eff = N / (1 + (N-1)ρ)`, and produces a report that shows how much
overconfidence multi-agent systems carry today.

See `../independence_collapse_proposal.pdf` for the full research
proposal.

---

## What ships

```
rho-collapse/
├── data/
│   └── combined.jsonl              750 items, 3 domains (see DATASET_README.md)
├── configs/
│   └── experiment.yaml             models × seeds × conditions
├── rho_collapse/                   the package
│   ├── loader.py                   reads combined.jsonl
│   ├── agents.py                   Anthropic / OpenAI / Google / Together
│   ├── scorer.py                   MCQ + code scoring
│   ├── runner.py                   items × committee → responses/errors
│   ├── rho.py                      ρ, N_eff, overconfidence gap
│   ├── report.py                   Markdown summary
│   └── cli.py                      `rho-collapse run` / `rho-collapse report`
├── tests/                          pytest suite
└── pyproject.toml
```

---

## Install

```bash
cd rho-collapse
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

## Set your API keys

The shipped config uses **OpenRouter** for everything (one key reaches Kimi,
DeepSeek, Qwen, Doubao, GLM, Claude, GPT-5, Gemini). Total budget for a
full 750-item sweep: **~$3–10**.

```bash
export OPENROUTER_API_KEY=...
```

If you'd rather hit providers natively (Anthropic, OpenAI, Google, Together
AI), swap `provider:` in `configs/experiment.yaml` and set the corresponding
key:

```bash
export ANTHROPIC_API_KEY=...
export OPENAI_API_KEY=...
export GOOGLE_API_KEY=...          # or GEMINI_API_KEY
export TOGETHER_API_KEY=...
```

**No web search, no tools, no function calling.** Every call is a raw
completion. Adding retrieval or code execution would confound the ρ
measurement by giving agents a shared external source of truth.

### Why Chinese models

Cheaper (10-50x) *and* scientifically sharper. The paper's new headline
condition, **D3 cross-culture**, mixes Chinese and Western models. If
pretraining-corpus divergence across cultures materially reduces ρ, that's
a novel publishable finding on its own. If it doesn't — that's the "AI
diversity is not real diversifier" result, which is also publishable.

## Run the tests first

```bash
pytest tests/ -q
```

All tests are deterministic and API-free (they use synthetic error matrices).
Passing this suite is the gate before spending money on API calls.

## Dry-run (10 items × 1 condition, ~$1)

```bash
rho-collapse run --config configs/experiment.yaml --dry-run
```

Writes to `runs/rho-v1/{responses.jsonl, errors.parquet, rho_by_domain.json, report.md}`.

## Full sweep (750 items × 3 conditions × 5 agents = 11,250 calls, ~$40-80)

```bash
rho-collapse run --config configs/experiment.yaml
```

The runner is **idempotent**: if it dies mid-sweep, re-running skips every
`(item, condition, agent, seed)` tuple already in `responses.jsonl`.

## Recompute a report from an existing run

```bash
rho-collapse report --run runs/rho-v1
```

Useful for tweaking the ρ math without re-hitting the APIs.

---

## What the report says

`runs/<run_id>/report.md` has two sections:

1. **Headline table** — one row per (domain × condition) cell. Reports ρ,
   its 95% bootstrap CI, and N_eff / N.

2. **Per-cell breakdown** — for each cell: per-agent accuracy, and the
   overconfidence gap by k-of-N agreement (observed accuracy vs. naive
   Condorcet posterior vs. our corrected posterior).

Whatever ρ turns out to be, the report will surface it. The paper's
punchline is: **on same-family committees, ρ is high enough that "5 agents
agree" carries the epistemic weight of ~1.4 agents.**

---

## Scope note (read this before pitching a finding)

- We measure **factual** consensus calibration only. Every task has a single
  correct answer that machines can check.
- MCQ probably **understates** real-world ρ: free-form generation has vastly
  more ways to fail together than 4-choice MCQ. Our numbers are a **lower
  bound** on the overconfidence carried by production free-form systems.
- We are not measuring debate quality, planning, or open-ended synthesis.
- We are not making a claim about which model is best.

---

## Licenses

- Code: MIT.
- Combined dataset: CC-BY-4.0 (derivative), MIT notices preserved per-row
  where applicable. See `data/DATASET_README.md`.
