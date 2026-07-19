# Analysis 01 — Headline ρ, N_eff, and bootstrap CIs (all 9 cells)

**Source:** `raw/rho_by_domain.json`, derived from `raw/errors.parquet`.

## Full matrix (5 agents per cell, 250 items per cell)

| Domain | Condition | Mean acc | ρ (95% CI) | N_eff | Saturated? |
|---|---|---|---|---|---|
| Science | D1 same-model (T=0.7) | 0.678 | 0.488 (0.417, 0.556) | 1.69 | no |
| Science | D2 cross-family Chinese (T=0) | 0.677 | 0.320 (0.251, 0.383) | 2.19 | no |
| Science | D3 cross-culture (T=0) | 0.697 | 0.279 (0.210, 0.349) | 2.36 | no |
| Medicine | D1 same-model (T=0.7) | 0.602 | 0.415 (0.333, 0.486) | 1.88 | no |
| Medicine | D2 cross-family Chinese (T=0) | 0.566 | 0.276 (0.216, 0.334) | 2.38 | no |
| Medicine | D3 cross-culture (T=0) | 0.630 | 0.320 (0.250, 0.380) | 2.19 | no |
| Law | D1 same-model (T=0.7) | 0.230 | 0.557 (0.486, 0.624) | 1.55 | no |
| Law | D2 cross-family Chinese (T=0) | 0.206 | 0.302 (0.250, 0.351) | 2.27 | no |
| Law | D3 cross-culture (T=0) | 0.259 | 0.427 (0.368, 0.486) | 1.85 | no |

## Observations

- **All 9 CIs exclude 0.** Every ρ is statistically significantly positive.
- **D1 has the highest ρ in every domain** — same-model committees collapse
  to 1.5–1.9 effective agents from a nominal 5.
- **D2 has the lowest ρ in every domain** — but this is confounded by Kimi
  (see analysis 02).
- **No saturation warnings** — every cell has mean per-agent accuracy well
  in the measurement-friendly 0.2–0.7 band.
- **Law's per-agent accuracy (~23-26%) is well above 10% random baseline
  for 10-way MCQ**, so ρ is meaningful there.

## Per-agent accuracy (across all 11,250 completions)

| Model | Calls | Accuracy |
|---|---|---|
| DeepSeek V4 | 5,043 | 52.7% |
| Kimi K2 | 1,500 | 20.4% |
| GLM 4.6 | 750 | 39.7% |
| ByteDance Seed 1.6 | 750 | 72.1% |
| Qwen 3 235B | 750 | 65.3% |
| Claude Sonnet 4.6 | 750 | 69.9% |
| Gemini 2.5 Pro | 750 | 69.0% |
| GPT-5-mini | 750 | 60.8% |

DeepSeek's low overall accuracy (52.7%) is a mix effect: it's the only
model in D1 (T=0.7 stochastic decoding on hard MCQ), and its D2/D3 numbers
are much higher (~65-70%).

## Interpretation

The paper's central quantitative claim rests on the row for **D1 in any
domain**. Five same-model agents deliver about 1.5-1.9 effective independent
votes — down from a nominal 5. Practitioners using N seeds of a single
model expecting Condorcet compounding get about one-third of the epistemic
weight they think they are.
