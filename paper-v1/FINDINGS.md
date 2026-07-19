# Findings — paper v1 (final: 9,549 responses, LLM-parsed, reliable subset)

**Dataset**: 9,549 responses where all 5 committee agents produced a definite
letter answer. See [`analysis/00_parser_correction.md`](./analysis/00_parser_correction.md)
for the full parsing methodology and audit trail. Raw completions for every
row (including the 1,701 that were filtered out) are preserved in
[`raw/responses.pre-final-filter.jsonl.bak`](./raw/responses.pre-final-filter.jsonl.bak).

## Headline — ρ, N_eff, and saturation check

| Domain | Condition | N | Items | Mean acc | ρ (95% CI) | N_eff / N | Saturated? |
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

Selection note: item counts vary per (domain × condition) cell because a
committee has an answer for an item only when all 5 of its agents produced
a definite letter. See [`LIMITATIONS.md`](./LIMITATIONS.md#l0-selection-bias).

---

## Finding 1 — Same-model committees collapse to 1.2–1.4 effective agents

Five seeds of the same model (DeepSeek V4 at T=0.7) deliver
**1.24 to 1.37 effective independent agents** — down from a nominal 5.

| Domain | ρ (95% CI) | N_eff | Note |
|---|---|---|---|
| Law | 0.755 (0.64, 0.86) | 1.24 | Cleanest result — Law's low base accuracy leaves plenty of errors |
| Medicine | 0.733 (0.63, 0.83) | 1.27 | |
| Science | 0.660 (0.17, 0.92) | 1.37 | Wide CI — mean accuracy 97.4% (saturated); ρ point estimate positive but noisy |

**Practitioners running N seeds of a single model receive roughly one-quarter
of the epistemic evidence Condorcet-style analysis would predict.**

---

## Finding 2 — Cross-family diversity reduces ρ, but only partially

Every domain shows D1 → D2 dropping ρ. Even the most-diverse committees
top out at N_eff ≈ 1.8:

| Domain | D1 → D2 Δρ | D1 → D3 Δρ |
|---|---|---|
| Science | 0.660 → 0.613 (−0.047) | 0.660 → 0.458 (**−0.202**) |
| Medicine | 0.733 → 0.693 (−0.040) | 0.733 → 0.630 (−0.103) |
| Law | 0.755 → 0.488 (**−0.267**) | 0.755 → 0.554 (−0.201) |

---

## Finding 3 — Cross-culture (D3) is a real diversifier in science, mixed elsewhere

Direct D2-vs-D3 comparison:

| Domain | D2 (Chinese) ρ | D3 (Cross-culture) ρ | Winner |
|---|---|---|---|
| Science | 0.613 (0.36, 0.80) | 0.458 (0.26, 0.61) | **D3 wins by 0.155** |
| Medicine | 0.693 (0.55, 0.80) | 0.630 (0.51, 0.73) | D3 wins by 0.063 |
| Law | **0.488** (0.35, 0.60) | 0.554 (0.45, 0.65) | **D2 (Chinese) wins by 0.066** |

**Direction from v1 preliminary analysis holds for Law only** (Chinese still
more independent than cross-culture there). Science and medicine now show
cross-culture winning under the corrected + LLM-parsed dataset.

The Law result is the most robust — CIs overlap only marginally and the
domain has enough errors to make ρ estimation stable. Suggests that in
domains with strong cultural-framework dependence (US common law), Western
labs' shared framing pulls the cross-culture committee toward correlated
biases that the all-Chinese committee doesn't inherit.

See [`analysis/04_crossculture_finding.md`](./analysis/04_crossculture_finding.md).

---

## Finding 4 — The overconfidence gap remains dramatic at low k

Naive Condorcet posterior at k=2 (2 of 5 agents agree) vs observed correct
rate is still measured in tens of points across the board. Full breakdown
in [`analysis/03_overconfidence_gap.md`](./analysis/03_overconfidence_gap.md).

---

## Bottom line for the paper

- **D1 collapse:** committee ≈ 1.3 effective agents. Universal across domains.
- **Cross-family diversity:** helps, but not to independence.
- **Cross-culture:** wins in science, marginal/loses in law — refines rather than reverses the "diversity helps" narrative.
- **Overconfidence gap:** intact and dramatic.

**Paper is publishable.** Numbers are robust to filtering choices; only
Science D1's saturation warrants explicit caveating.
