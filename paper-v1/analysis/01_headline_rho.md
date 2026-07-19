# Analysis 01 — Headline ρ, N_eff, and bootstrap CIs (corrected scoring)

**Source:** `raw/rho_by_domain.json` (post parser fix, see
[`00_parser_correction.md`](./00_parser_correction.md)).

## Full matrix (5 agents per cell, 250 items per cell)

| Domain | Condition | Mean acc | ρ (95% CI) | N_eff | Saturated? |
|---|---|---|---|---|---|
| Science | D1 same-model (T=0.7) | 0.713 | 0.586 (0.520, 0.655) | 1.49 | no |
| Science | D2 cross-family Chinese (T=0) | 0.746 | 0.408 (0.330, 0.479) | 1.90 | no |
| Science | D3 cross-culture (T=0) | 0.778 | 0.395 (0.312, 0.476) | 1.94 | no |
| Medicine | D1 same-model (T=0.7) | 0.738 | 0.659 (0.576, 0.728) | 1.37 | no |
| Medicine | D2 cross-family Chinese (T=0) | 0.690 | 0.413 (0.337, 0.479) | 1.89 | no |
| Medicine | D3 cross-culture (T=0) | 0.755 | 0.473 (0.383, 0.548) | 1.73 | no |
| Law | D1 same-model (T=0.7) | 0.258 | 0.638 (0.566, 0.700) | 1.41 | no |
| Law | D2 cross-family Chinese (T=0) | 0.266 | 0.498 (0.434, 0.557) | 1.67 | no |
| Law | D3 cross-culture (T=0) | 0.316 | 0.660 (0.600, 0.719) | 1.37 | no |

## Observations

- **All 9 CIs exclude 0.** Every ρ is statistically significantly positive.
- **D1 same-model committees collapse to N_eff ≈ 1.4** in every domain —
  5 seeds give the epistemic weight of about 1.4 independent agents.
- **Even the most diverse committees (D2, D3) only reach N_eff ≈ 1.7–1.9** —
  the maximum measurable independence in this experiment falls well
  short of the nominal 5.
- **No saturation warnings** — mean per-agent accuracy sits in 0.25–0.78
  across cells.

## Per-agent accuracy (across all 11,250 completions)

| Model | Calls | Accuracy |
|---|---|---|
| DeepSeek V4 | 5,250 | 57.4% |
| Kimi K2 | 1,500 | 55.4% |
| ByteDance Seed 1.6 | 750 | 69.2% |
| Claude Sonnet 4.6 | 750 | 67.7% |
| Gemini 2.5 Pro | 750 | 66.3% |
| Qwen 3 235B | 750 | 64.7% |
| GPT-5-mini | 750 | 58.4% |
| GLM 4.6 | 750 | 38.1% |

**Kimi K2 is now in the same accuracy cluster as the other models** (55-70%).
The v0.1 "Kimi outlier at 20%" story was almost entirely a parser bug
(see `00_parser_correction.md`).

**GLM 4.6 at 38%** is now the outlier — this is likely a truncation issue
because GLM is a reasoning model that emits many reasoning tokens before
the answer. `max_tokens=1024` may still be insufficient for GLM in a
non-trivial fraction of items. This is a v2 investigation.

## Interpretation

The paper's central quantitative claim rests on the D1 rows: **5 same-model
agents deliver 1.37-1.49 effective independent votes, down from a nominal 5.**
That is a design-effect reduction of ~72% — practitioners running N seeds
of a single model receive roughly one-quarter of the epistemic evidence
Condorcet-style analysis would predict.
