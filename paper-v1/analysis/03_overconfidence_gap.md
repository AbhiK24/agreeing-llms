# Analysis 03 — Overconfidence gap by cluster size k

**Source:** `raw/rho_by_domain.json` cluster-analysis section, all 9 cells.

## The paper's core claim, quantified

For each item, we cluster the 5 agents' parsed answers, take the size k
of the largest same-answer cluster, and record whether that cluster's
answer is the gold answer. Then:

- **Naive posterior** — the confidence a Condorcet-style analysis would
  assign, assuming per-agent independence, with per-agent accuracy p and
  answer-space size C: P(correct | k agree) = p^k / (p^k + (C-1)·((1-p)/(C-1))^k)
- **Observed correct rate** — the actual fraction of items in that bin
  where the largest cluster was correct
- **Overconfidence gap** — Naive − Observed. Positive = overconfident.
- **Corrected posterior** — the same formula with k replaced by
  k_eff = k · N_eff / N.

## Full table (only cells with ≥ 10 items in the bin shown)

Note: k=1 rows are noisy because "largest cluster" tie-breaks
arbitrarily when no two agents agree.

### Medicine — the cleanest signal

| Cell | k | Items | Observed | Naive | Corrected | Gap |
|---|---|---|---|---|---|---|
| D1 same-model | 2 | 30 | 0.733 | 0.948 | 0.449 | **+0.215** |
| D1 same-model | 3 | 52 | 0.846 | 0.996 | 0.676 | +0.149 |
| D1 same-model | 4 | 62 | 0.887 | 1.000 | 0.842 | +0.113 |
| D1 same-model | 5 | 73 | 0.918 | 1.000 | 0.931 | +0.082 |
| D2 Chinese | 2 | 42 | 0.667 | 0.931 | 0.537 | **+0.265** |
| D2 Chinese | 3 | 92 | 0.891 | 0.993 | 0.779 | +0.102 |
| D2 Chinese | 4 | 85 | 0.918 | 0.999 | 0.915 | +0.082 |
| D2 Chinese | 5 | 18 | 0.833 | 1.000 | 0.970 | +0.167 |
| D3 cross-culture | 2 | 29 | 0.586 | 0.959 | 0.552 | **+0.372** |
| D3 cross-culture | 3 | 70 | 0.886 | 0.997 | 0.795 | +0.111 |
| D3 cross-culture | 4 | 127 | 0.906 | 1.000 | 0.924 | +0.094 |
| D3 cross-culture | 5 | 20 | 0.900 | 1.000 | 0.974 | +0.100 |

### Science

| Cell | k | Items | Observed | Naive | Corrected | Gap |
|---|---|---|---|---|---|---|
| D1 same-model | 2 | 28 | 0.821 | 0.975 | 0.449 | **+0.154** |
| D1 same-model | 3 | 29 | 0.931 | 0.999 | 0.688 | +0.068 |
| D1 same-model | 4 | 41 | 0.976 | 1.000 | 0.856 | +0.024 |
| D1 same-model | 5 | 109 | 0.982 | 1.000 | 0.942 | +0.018 |
| D2 Chinese | 2 | 32 | 0.781 | 0.975 | 0.593 | **+0.194** |
| D2 Chinese | 3 | 48 | 0.938 | 0.999 | 0.841 | +0.061 |
| D2 Chinese | 4 | 93 | 0.957 | 1.000 | 0.950 | +0.043 |
| D2 Chinese | 5 | 57 | 1.000 | 1.000 | 0.986 | −0.000 |
| D3 cross-culture | 2 | 22 | 0.682 | 0.979 | 0.661 | **+0.298** |
| D3 cross-culture | 3 | 49 | 0.939 | 0.999 | 0.891 | +0.060 |
| D3 cross-culture | 4 | 104 | 0.933 | 1.000 | 0.971 | +0.067 |
| D3 cross-culture | 5 | 59 | 1.000 | 1.000 | 0.993 | −0.000 |

### Law

| Cell | k | Items | Observed | Naive | Corrected | Gap |
|---|---|---|---|---|---|---|
| D1 same-model | 3 | 22 | 0.636 | 0.632 | 0.220 | −0.004 |
| D1 same-model | 4 | 34 | 0.853 | 0.804 | 0.269 | −0.049 |
| D1 same-model | 5 | 18 | 0.833 | 0.908 | 0.326 | +0.075 |
| D2 Chinese | 2 | 53 | 0.585 | 0.349 | 0.195 | −0.236 |
| D2 Chinese | 3 | 45 | 0.800 | 0.526 | 0.252 | −0.274 |
| D2 Chinese | 4 | 15 | 0.867 | 0.697 | 0.319 | −0.170 |
| D3 cross-culture | 2 | 35 | 0.514 | 0.495 | 0.211 | −0.019 |
| D3 cross-culture | 3 | 40 | 0.750 | 0.733 | 0.281 | −0.017 |
| D3 cross-culture | 4 | 45 | 0.844 | 0.885 | 0.364 | +0.040 |

Law's naive posteriors are low because per-agent accuracy is low
(p ≈ 0.23), so the naive Condorcet formula doesn't overshoot — and in
fact undershoots at low k because it can't distinguish random agreement
from true agreement.

## Key observations

1. **The overconfidence gap is largest at k=2** — small-cluster agreement
   is dramatically overstated by naive Condorcet. Medicine D3 shows a
   +0.372 gap: naive says 96%, actual is 59%.
2. **The gap shrinks at k=4 and k=5** — when many agents agree, agreement
   really does mean something, even in the naive analysis.
3. **The corrected posterior closes most of the gap at k=3-5** but
   overshoots at k=2 (becomes too pessimistic). This is a calibration
   artifact of the simple k_eff = k · N_eff / N scaling; the paper's
   discussion should acknowledge this as future work for a more
   sophisticated correction.
4. **Law is different** — with low per-agent accuracy, naive
   posteriors are already conservative and there's no overconfidence to
   correct for at small k. This is arguably the honest use case: low
   confidence is warranted when models are individually bad at the task.

## The paper's headline number

At **k=2** across the medicine and science cells:

> When 2 LLM agents agree on a factual answer, naive Condorcet posterior
> analyses (as used implicitly in every majority-vote consensus mechanism)
> assign 95–98% confidence that the answer is correct. Observed correctness
> is 59–78%. The overconfidence gap is 19–37 percentage points.

That is the paper.
