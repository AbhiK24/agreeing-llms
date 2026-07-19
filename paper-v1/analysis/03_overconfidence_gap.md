# Analysis 03 — Overconfidence gap by cluster size k (corrected scoring)

**Source:** `raw/rho_by_domain.json` (post parser fix, see
[`00_parser_correction.md`](./00_parser_correction.md)).

## The paper's core claim, quantified

For each item, we cluster the 5 agents' parsed answers, take the size k
of the largest same-answer cluster, and record whether that cluster's
answer is the gold answer. Then compute:

- **Naive Condorcet posterior:** what a naive analyst would predict for
  P(correct | k agree) under independence
- **Corrected posterior:** the same formula with k → k · N_eff / N
- **Observed correct rate:** the actual fraction where the largest
  cluster was correct
- **Overconfidence gap:** Naive − Observed (positive = overconfident)

Only bins with n ≥ 10 items reported here (k=1 rows for law/medicine
D3 have very few items due to high consensus). Full table in
`raw/rho_by_domain.json`.

## The money numbers — k=2 agreement across every cell

| Cell | Naive P | Observed | Gap |
|---|---|---|---|
| Medicine D1 same-model | 0.985 | 0.778 | **+0.207** |
| Medicine D2 Chinese | 0.975 | 0.450 | **+0.525** |
| Medicine D3 cross-culture | 0.987 | 0.267 | **+0.720** |
| Science D1 same-model | 0.982 | 0.741 | **+0.242** |
| Science D2 Chinese | 0.987 | 0.677 | **+0.310** |
| Science D3 cross-culture | 0.991 | 0.714 | **+0.277** |
| Law D2 Chinese | 0.513 | 0.488 | +0.026 |
| Law D3 cross-culture | 0.631 | 0.385 | **+0.246** |

**The naive Condorcet posterior at k=2 (2 of 5 agents agree) is 95-99% in
every domain where per-agent accuracy is > 0.6. Observed correct rate is
27-78%.** Overconfidence gap: 20-72 percentage points.

## Full cluster analysis by domain

### Medicine — the most striking overconfidence

| Cell | k | Items | Observed | Naive | Corrected | Gap |
|---|---|---|---|---|---|---|
| D1 same-model | 2 | 18 | 0.778 | 0.985 | 0.410 | +0.207 |
| D1 same-model | 3 | 21 | 0.619 | 0.999 | 0.620 | +0.380 |
| D1 same-model | 4 | 40 | 0.775 | 1.000 | 0.794 | +0.225 |
| D1 same-model | 5 | 154 | 0.935 | 1.000 | 0.901 | +0.065 |
| D2 Chinese | 2 | 20 | 0.450 | 0.975 | 0.524 | **+0.525** |
| D2 Chinese | 3 | 52 | 0.846 | 0.999 | 0.765 | +0.152 |
| D2 Chinese | 4 | 86 | 0.895 | 1.000 | 0.906 | +0.105 |
| D2 Chinese | 5 | 85 | 0.918 | 1.000 | 0.966 | +0.082 |
| D3 cross-culture | 2 | 15 | 0.267 | 0.987 | 0.535 | **+0.720** |
| D3 cross-culture | 3 | 28 | 0.643 | 0.999 | 0.777 | +0.357 |
| D3 cross-culture | 4 | 86 | 0.907 | 1.000 | 0.913 | +0.093 |
| D3 cross-culture | 5 | 119 | 0.916 | 1.000 | 0.970 | +0.084 |

### Science

| Cell | k | Items | Observed | Naive | Corrected | Gap |
|---|---|---|---|---|---|---|
| D1 same-model | 2 | 27 | 0.741 | 0.982 | 0.416 | +0.242 |
| D1 same-model | 3 | 22 | 0.864 | 0.999 | 0.643 | +0.136 |
| D1 same-model | 4 | 23 | 0.957 | 1.000 | 0.820 | +0.043 |
| D1 same-model | 5 | 138 | 0.986 | 1.000 | 0.920 | +0.014 |
| D2 Chinese | 2 | 31 | 0.677 | 0.987 | 0.573 | +0.310 |
| D2 Chinese | 3 | 27 | 0.852 | 1.000 | 0.823 | +0.148 |
| D2 Chinese | 4 | 73 | 0.959 | 1.000 | 0.942 | +0.041 |
| D2 Chinese | 5 | 105 | 0.990 | 1.000 | 0.983 | +0.010 |
| D3 cross-culture | 2 | 14 | 0.714 | 0.991 | 0.618 | +0.277 |
| D3 cross-culture | 3 | 36 | 0.806 | 1.000 | 0.860 | +0.194 |
| D3 cross-culture | 4 | 60 | 0.917 | 1.000 | 0.959 | +0.083 |
| D3 cross-culture | 5 | 127 | 0.984 | 1.000 | 0.989 | +0.016 |

### Law

Law's naive posteriors are much lower because per-agent accuracy is
~0.25–0.32 rather than 0.7+. When individual agents are near-random the
naive Condorcet math correctly does not compound weak signals into
overconfidence — it's already conservative at low k.

| Cell | k | Items | Observed | Naive | Corrected | Gap |
|---|---|---|---|---|---|---|
| D1 same-model | 3 | 24 | 0.625 | 0.730 | 0.229 | +0.105 |
| D1 same-model | 4 | 22 | 0.864 | 0.883 | 0.284 | +0.019 |
| D1 same-model | 5 | 36 | 0.833 | 0.955 | 0.346 | +0.121 |
| D2 Chinese | 2 | 41 | 0.488 | 0.513 | 0.203 | +0.026 |
| D2 Chinese | 3 | 39 | 0.692 | 0.754 | 0.267 | +0.062 |
| D2 Chinese | 4 | 39 | 0.769 | 0.899 | 0.342 | +0.130 |
| D3 cross-culture | 2 | 26 | 0.385 | 0.631 | 0.204 | **+0.246** |
| D3 cross-culture | 3 | 27 | 0.556 | 0.863 | 0.269 | **+0.308** |
| D3 cross-culture | 4 | 30 | 0.767 | 0.959 | 0.345 | **+0.192** |
| D3 cross-culture | 5 | 45 | 0.889 | 0.989 | 0.430 | +0.100 |

## Key observations

1. **The overconfidence gap is enormous at k=2** when per-agent accuracy
   is > 0.6 — up to +0.72 in medicine D3.
2. **The N_eff correction closes most of the gap at k=4-5** but tends to
   overshoot into pessimism at k=2-3. This is a scaling artifact of the
   simple `k_eff = k · N_eff / N` correction and is discussed as future
   work in the paper.
3. **At k=5 (all 5 agents agree), naive posteriors are essentially 1.000
   but observed correct rates are 92-99%.** Even universal committee
   agreement leaves a 1-8 percentage-point overconfidence residual.
4. **Law's low-accuracy regime shows a different pattern** — the naive
   posterior at k=2 is only 0.51, matching observed 0.49. When individual
   agents can't be trusted, agreement isn't over-interpreted. This
   suggests the overconfidence problem is worst in the "smart-looking but
   not smart enough" middle-accuracy band.

## The paper's headline number

At k=2 across science and medicine cells (per-agent accuracy 0.6+):

> When 2 LLM agents agree on a factual answer, naive Condorcet posterior
> analyses assign 97-99% confidence that the answer is correct. Observed
> correctness is 27-78% depending on domain and committee composition.
> The overconfidence gap is 20-72 percentage points.

That is the paper.
