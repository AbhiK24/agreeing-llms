# ρ-collapse

**Measure inter-agent error correlation in multi-agent LLM committees.**

The claim: when N LLM agents agree on a factual answer, the common
justification treats that agreement like N independent votes (Condorcet's
Jury Theorem). But LLMs share pretraining and instruction-tuning, so their
errors are correlated. This package measures the correlation `ρ` across
three domains, computes the effective committee size
`N_eff = N / (1 + (N-1)ρ)`, and produces a report that shows how much
overconfidence multi-agent systems carry today.

See `../independence_collapse_proposal.pdf` for the full research proposal.

---

## What ships

```
rho-collapse/
├── data/
│   ├── combined.jsonl                 750 items, 3 domains (see DATASET_README.md)
│   └── build_combined_dataset.py      reproducible builder (seed 42)
├── configs/
│   └── experiment.yaml                models × seeds × conditions
├── rho_collapse/                      the package
│   ├── loader.py                      reads combined.jsonl
│   ├── agents.py                      Anthropic / OpenAI / Google / Together / OpenRouter
│   ├── scorer.py                      MCQ + code scoring
│   ├── runner.py                      items × committee → responses / errors (rate-limited, idempotent)
│   ├── rate_limit.py                  per-model concurrency + token buckets
│   ├── rho.py                         ρ, N_eff, Bayesian Condorcet posterior, cluster analysis
│   ├── report.py                      Markdown summary
│   └── cli.py                         `rho-collapse run` / `rho-collapse report`
├── tests/                             pytest suite (46 tests)
└── pyproject.toml
```

## The dataset (v0.3)

All 750 items sourced from **MMLU-Pro** so answer-space size (C) is
uniform (~10) across every domain, killing the "why is medicine's ρ
smaller?" confound:

| Domain | MMLU-Pro category | Items | Modal C |
|---|---|---|---|
| Science | biology, physics, chemistry | 250 | 10 (94%) |
| Medicine | health (anatomy, physiology, pharmacology) | 250 | 10 (74%) |
| Law | law (bar-exam-style) | 250 | 10 (64%) |

See `data/DATASET_README.md` for licensing and citation.

---

## Install

```bash
cd rho-collapse
python3 -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
```

## Set your API keys

The shipped config uses **OpenRouter** for everything — one key reaches
DeepSeek V4, Kimi K2, Qwen 3, GLM 4.6, ByteDance Seed, Claude Sonnet,
GPT-5-mini, and Gemini 2.5 Pro. Total budget for a full 750-item sweep:
**~$10–15**.

```bash
export OPENROUTER_API_KEY=...
```

If you'd rather hit providers natively, swap `provider:` in
`configs/experiment.yaml` and set the corresponding key:

```bash
export ANTHROPIC_API_KEY=...
export OPENAI_API_KEY=...
export GOOGLE_API_KEY=...
export TOGETHER_API_KEY=...
```

**No web search, no tools, no function calling.** Every call is a raw
completion. Adding retrieval or code execution would confound ρ by giving
agents a shared external source of truth.

### Why Chinese-first

Cheaper (10-50×) *and* scientifically sharper. The paper's headline
condition, **D3 cross-culture**, mixes Chinese and Western models. If
pretraining-corpus divergence across cultures materially reduces ρ,
that's a novel publishable finding. If it doesn't — that's the "AI
diversity is not a real diversifier" result, equally publishable.

## Rate-limit strategy

Safe parallelism is enforced by three layers so **no single provider gets
bursted**:

1. Global `n_workers` cap in `experiment.yaml`
2. Per-model concurrency semaphore (`max_concurrent` per model)
3. Per-model token bucket (`requests_per_second` per model)

Reasoning models like GLM 4.6 get tighter caps because they burn many
output tokens per call. Details in `configs/experiment.yaml`.

## Run the tests first

```bash
pytest tests/ -q
```

All 46 tests are deterministic and API-free (synthetic error matrices).
Passing this suite is the gate before spending money.

## Dry-run (~50 calls, ~$0.20)

```bash
rho-collapse run --config configs/experiment.yaml --dry-run
```

Writes `runs/rho-v1/{responses.jsonl, errors.parquet, rho_by_domain.json, report.md}`.

## Full sweep (750 items × 3 conditions × 5 agents = 11,250 calls, ~$10–15)

```bash
rho-collapse run --config configs/experiment.yaml
```

The runner is **idempotent**: if it dies mid-sweep, re-running skips every
`(item, condition, agent, seed)` tuple already in `responses.jsonl`.
`progress.json` is refreshed every 20 completions.

## Recompute a report from an existing run

```bash
rho-collapse report --run runs/rho-v1
```

Useful for tweaking the ρ math without re-hitting the APIs.

---

## What the report says

`runs/<run_id>/report.md` has:

1. **Headline table** — per (domain × condition): mean per-agent accuracy,
   ρ with 95% bootstrap CI, N_eff / N, and a saturation warning.
2. **Per-cell breakdown** — per-agent accuracy, per-C posterior context,
   and cluster analysis (largest same-answer cluster size k, observed
   correctness, naive vs. corrected Condorcet posterior, overconfidence
   gap).

Whatever ρ turns out to be, the report surfaces it. The paper's punchline:
**on same-family committees, ρ is high enough that "5 agents agree"
carries the epistemic weight of ~1.4 agents.**

---

## Scope note

- We measure **factual** consensus calibration only. Every task has a
  single machine-checkable correct answer.
- MCQ probably **understates** real-world ρ: free-form generation has
  vastly more ways to fail together than 10-choice MCQ. Our numbers are a
  **lower bound** on the overconfidence carried by production free-form
  systems.
- We are not measuring debate quality, planning, or open-ended synthesis.
- We are not making a claim about which model is best.

---

## Licenses

- Code: MIT (see `LICENSE`).
- Combined dataset: CC-BY-4.0 (derivative of MMLU-Pro). See
  `data/DATASET_README.md`.
