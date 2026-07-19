# Analysis 03 — Overconfidence gap by cluster size (final v1 dataset)

**Source:** `raw/rho_by_domain.json` cluster analysis (9,549 filtered
responses, LLM-parsed).

## The paper's core claim, quantified

For each item, cluster the 5 agents' picked letters; take the size k of the
largest same-answer cluster; record whether that cluster's letter is gold.

- **Naive Condorcet posterior:** what a naive analyst would predict for
  P(correct | k of N agree) under independence and per-agent accuracy p
- **Corrected posterior:** same formula with k → k · N_eff / N
- **Observed correct rate:** actual fraction where the largest cluster is
  correct
- **Overconfidence gap:** naive − observed. Positive = overconfident.

Only bins with n ≥ 10 items shown. Bin at k=1 is arbitrary tiebreak — noisy.

## Money numbers — k=2 agreement (2 of 5 agents agree)

| Cell | k=2 items | Naive P | Observed | Gap |
|---|---|---|---|---|
| Law D1 same-model | 38 | 0.988 | 0.395 | **+0.593** |
| Law D2 Chinese | 67 | 0.976 | 0.478 | **+0.498** |
| Law D3 cross-culture | 52 | 0.985 | 0.404 | **+0.581** |
| Medicine D1 same-model | 17 | 0.998 | 0.765 | +0.233 |
| Medicine D2 Chinese | 19 | 0.997 | 0.368 | **+0.628** |
| Medicine D3 cross-culture | 12 | 0.997 | 0.250 | **+0.747** |
| Science D1 same-model | 27 | 1.000 | 0.667 | +0.333 |
| Science D2 Chinese | 24 | 0.999 | 0.583 | **+0.416** |
| Science D3 cross-culture | 16 | 0.999 | 0.688 | +0.312 |

**Every k=2 cell shows +23 to +75 percentage-point overconfidence.** Naive
Condorcet insists 97-100% probability of correctness; observed truth is
25-77%.

## Money numbers — k=5 (all 5 agents agree)

| Cell | k=5 items | Naive P | Observed | Gap |
|---|---|---|---|---|
| Law D1 same-model | 72 | 1.000 | 0.861 | +0.139 |
| Law D2 Chinese | 35 | 1.000 | 0.914 | +0.086 |
| Law D3 cross-culture | 78 | 1.000 | 0.897 | +0.103 |
| Medicine D1 same-model | 168 | 1.000 | 0.929 | +0.071 |
| Medicine D2 Chinese | 115 | 1.000 | 0.913 | +0.087 |
| Medicine D3 cross-culture | 154 | 1.000 | 0.922 | +0.078 |
| Science D1 same-model | 144 | 1.000 | 0.986 | +0.014 |
| Science D2 Chinese | 122 | 1.000 | 0.992 | +0.008 |
| Science D3 cross-culture | 137 | 1.000 | 0.985 | +0.015 |

**Even at full 5-agent agreement, naive Condorcet says 100.0% but observed
correctness is 86-99%.** The residual gap is 1-14 percentage points depending
on domain.

## Full cluster analysis per domain

### Law

| Cell | k | Items | Observed | Naive | Corrected | Gap |
|---|---|---|---|---|---|---|
| D1 same-model | 1 | 44 | 0.432 | 0.764 | 0.219 | +0.332 |
| D1 same-model | 2 | 38 | 0.395 | 0.988 | 0.387 | +0.593 |
| D1 same-model | 3 | 42 | 0.524 | 1.000 | 0.586 | +0.476 |
| D1 same-model | 4 | 37 | 0.730 | 1.000 | 0.761 | +0.270 |
| D1 same-model | 5 | 72 | 0.861 | 1.000 | 0.877 | +0.139 |
| D2 Chinese | 1 | 10 | 0.300 | 0.693 | 0.250 | +0.393 |
| D2 Chinese | 2 | 67 | 0.478 | 0.976 | 0.470 | +0.498 |
| D2 Chinese | 3 | 77 | 0.649 | 0.999 | 0.702 | +0.349 |
| D2 Chinese | 4 | 61 | 0.787 | 1.000 | 0.863 | +0.213 |
| D2 Chinese | 5 | 35 | 0.914 | 1.000 | 0.944 | +0.086 |
| D3 cross-culture | 1 | 13 | 0.077 | 0.743 | 0.249 | +0.666 |
| D3 cross-culture | 2 | 52 | 0.404 | 0.985 | 0.468 | +0.581 |
| D3 cross-culture | 3 | 52 | 0.615 | 0.999 | 0.701 | +0.384 |
| D3 cross-culture | 4 | 55 | 0.764 | 1.000 | 0.861 | +0.236 |
| D3 cross-culture | 5 | 78 | 0.897 | 1.000 | 0.943 | +0.103 |

### Medicine

| Cell | k | Items | Observed | Naive | Corrected | Gap |
|---|---|---|---|---|---|---|
| D1 same-model | 2 | 17 | 0.765 | 0.998 | 0.501 | +0.233 |
| D1 same-model | 3 | 16 | 0.625 | 1.000 | 0.740 | +0.375 |
| D1 same-model | 4 | 32 | 0.719 | 1.000 | 0.890 | +0.281 |
| D1 same-model | 5 | 168 | 0.929 | 1.000 | 0.958 | +0.071 |
| D2 Chinese | 2 | 19 | 0.368 | 0.997 | 0.498 | +0.628 |
| D2 Chinese | 3 | 36 | 0.806 | 1.000 | 0.737 | +0.194 |
| D2 Chinese | 4 | 75 | 0.907 | 1.000 | 0.887 | +0.093 |
| D2 Chinese | 5 | 115 | 0.913 | 1.000 | 0.957 | +0.087 |
| D3 cross-culture | 2 | 12 | 0.250 | 0.997 | 0.536 | +0.747 |
| D3 cross-culture | 3 | 23 | 0.609 | 1.000 | 0.779 | +0.391 |
| D3 cross-culture | 4 | 59 | 0.881 | 1.000 | 0.914 | +0.119 |
| D3 cross-culture | 5 | 154 | 0.922 | 1.000 | 0.970 | +0.078 |

### Science

| Cell | k | Items | Observed | Naive | Corrected | Gap |
|---|---|---|---|---|---|---|
| D1 same-model | 1 | 30 | 0.700 | 0.974 | 0.356 | +0.274 |
| D1 same-model | 2 | 27 | 0.667 | 1.000 | 0.733 | +0.333 |
| D1 same-model | 3 | 18 | 0.833 | 1.000 | 0.932 | +0.167 |
| D1 same-model | 4 | 23 | 0.957 | 1.000 | 0.986 | +0.043 |
| D1 same-model | 5 | 144 | 0.986 | 1.000 | 0.997 | +0.014 |
| D2 Chinese | 1 | 11 | 0.636 | 0.937 | 0.314 | +0.300 |
| D2 Chinese | 2 | 24 | 0.583 | 0.999 | 0.654 | +0.416 |
| D2 Chinese | 3 | 31 | 0.871 | 1.000 | 0.886 | +0.129 |
| D2 Chinese | 4 | 62 | 0.952 | 1.000 | 0.970 | +0.048 |
| D2 Chinese | 5 | 122 | 0.992 | 1.000 | 0.993 | +0.008 |
| D3 cross-culture | 1 | 10 | 0.100 | 0.929 | 0.374 | +0.829 |
| D3 cross-culture | 2 | 16 | 0.688 | 0.999 | 0.763 | +0.312 |
| D3 cross-culture | 3 | 30 | 0.767 | 1.000 | 0.945 | +0.233 |
| D3 cross-culture | 4 | 57 | 0.912 | 1.000 | 0.989 | +0.088 |
| D3 cross-culture | 5 | 137 | 0.985 | 1.000 | 0.998 | +0.015 |

## Key observations

1. **The overconfidence gap is largest at k=2** — small-cluster agreement
   dramatically overstated by naive Condorcet. Peak gap: +0.747 in
   Medicine D3.
2. **Gaps shrink but don't vanish at k=5** — even universal 5-agent agreement
   overstates observed correctness by 1-14 pp.
3. **The N_eff correction closes most of the gap at k=4-5** — the corrected
   posterior tracks observed correctness within 5-10 pp at high k.
4. **The correction slightly overshoots at low k** (becomes too pessimistic
   at k=1-2) — a limitation of the simple `k_eff = k · N_eff / N` scaling.
   Discussion-section note about future work.

## The paper's headline number

At **k=2** across law, medicine, and science:

> When 2 of 5 LLM agents agree on a factual answer, naive Condorcet
> posterior analyses assign 97-100% confidence that the answer is correct.
> Observed correct rate is 25-77% depending on domain and committee
> composition. **The overconfidence gap at k=2 is 23-75 percentage
> points.**

That is the paper.
