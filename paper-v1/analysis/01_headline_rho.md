# Analysis 01 — Headline ρ, N_eff, and bootstrap CIs (final v1 dataset)

**Source:** `raw/rho_by_domain.json` (9,549 responses, LLM-parsed, post-
reprompt, post-filter).

## Full matrix

| Domain | Condition | N | Items | Mean acc | ρ (95% CI) | N_eff | Saturated? |
|---|---|---|---|---|---|---|---|
| Science | D1 same-model (T=0.7) | 5 | 149 | 0.974 | 0.660 (0.167, 0.921) | 1.37 | ⚠ yes |
| Science | D2 cross-family Chinese (T=0) | 5 | 139 | 0.937 | 0.613 (0.356, 0.797) | 1.45 | no |
| Science | D3 cross-culture (T=0) | 5 | 168 | 0.929 | 0.458 (0.261, 0.606) | 1.77 | no |
| Medicine | D1 same-model (T=0.7) | 5 | 194 | 0.882 | 0.733 (0.625, 0.825) | 1.27 | no |
| Medicine | D2 cross-family Chinese (T=0) | 5 | 140 | 0.861 | 0.693 (0.552, 0.799) | 1.33 | no |
| Medicine | D3 cross-culture (T=0) | 5 | 192 | 0.863 | 0.630 (0.509, 0.733) | 1.42 | no |
| Law | D1 same-model (T=0.7) | 5 | 94 | 0.764 | 0.755 (0.635, 0.860) | 1.24 | no |
| Law | D2 cross-family Chinese (T=0) | 5 | 80 | 0.693 | 0.488 (0.350, 0.600) | 1.69 | no |
| Law | D3 cross-culture (T=0) | 5 | 129 | 0.743 | 0.554 (0.448, 0.654) | 1.56 | no |

## Observations

- **8 of 9 CIs exclude 0.** Science D1's lower bound is 0.167 — technically
  above zero, but the wide CI (0.17, 0.92) is a saturation artifact. See L2.
- **D1 same-model committees collapse to N_eff ≈ 1.3** across all three
  domains — 5 seeds deliver the epistemic weight of about 1.3 agents.
- **D2 and D3 achieve N_eff between 1.3 and 1.8** — cross-family diversity
  helps but does not restore anything close to nominal N.
- **One saturation warning** — Science D1 mean accuracy is 0.974; not enough
  errors to estimate ρ tightly. Point estimate 0.66 is consistent with the
  D1 collapse pattern but should be caveated.

## Per-agent accuracy (across full 9,549 filtered dataset)

| Model | Calls | Accuracy |
|---|---|---|
| DeepSeek V4 | 4,414 | 87.9% |
| Kimi K2 | 1,102 | 90.7% |
| ByteDance Seed 1.6 | 618 | 92.4% |
| Claude Sonnet 4.6 | 648 | 87.7% |
| Gemini 2.5 Pro | 623 | 87.3% |
| GLM 4.6 | 543 | 66.5% |
| GPT-5-mini | 626 | 86.3% |
| Qwen 3 235B | 630 | 88.1% |

Under the filter, each agent's accuracy is higher than on the raw sweep
because we only kept items where every committee member produced a
definite letter — biased toward items each model could handle.

**GLM 4.6 remains the lowest-accuracy agent** at 66.5%, consistent with
its reasoning-model overhead and occasional truncation. All other models
cluster tightly in 86-92%.

## Interpretation

The paper's central quantitative claim — **N_eff ≈ 1.3 for same-model
committees** — is confirmed across all three domains. Even the saturated
Science D1 point estimate lands at N_eff = 1.37, consistent with the
tight law (1.24) and medicine (1.27) estimates.

Practitioners running N seeds of a single model receive roughly one-quarter
of the epistemic evidence Condorcet-style analysis would predict.
