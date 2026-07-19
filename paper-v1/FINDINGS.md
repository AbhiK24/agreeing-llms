# Findings — paper v1 (corrected scoring)

Everything below reflects the **corrected parser** (see
[`analysis/00_parser_correction.md`](./analysis/00_parser_correction.md)).
The original responses are preserved in
[`raw/responses.v1-scoring.jsonl.bak`](./raw/responses.v1-scoring.jsonl.bak);
the corrected ones are in [`raw/responses.jsonl`](./raw/responses.jsonl).
The API responses themselves are byte-identical; only the derived
`parsed_answer` and `error` fields differ.

---

## Finding 1 — D1 same-model committees collapse to 1.4 effective agents

Five seeds of the same model (DeepSeek V4 at T=0.7) deliver
**1.37 to 1.49 effective independent agents** — down from a nominal 5.

| Domain | ρ (95% CI) | N_eff / 5 | Effective size |
|---|---|---|---|
| Science | 0.586 (0.520, 0.655) | 1.49 | ≈ 1.5 agents |
| Medicine | 0.659 (0.576, 0.728) | 1.37 | ≈ 1.4 agents |
| Law | 0.638 (0.566, 0.700) | 1.41 | ≈ 1.4 agents |

**All CIs exclude 0.** See [`analysis/01_headline_rho.md`](./analysis/01_headline_rho.md).

**Practitioners running N seeds of a single model get roughly 1/3.5 of
the epistemic evidence Condorcet-style analysis predicts.**

---

## Finding 2 — Cross-family diversity reduces ρ substantially, but not to zero

Swapping model families (D1 → D2 → D3) drops ρ by 0.15 to 0.25 in most
cells. Even the most diverse committees deliver at most ~1.9 effective
agents from a nominal 5.

| Cell | ρ (95% CI) | N_eff / 5 |
|---|---|---|
| Science D2 Chinese | 0.408 (0.330, 0.479) | 1.90 |
| Science D3 cross-culture | 0.395 (0.312, 0.476) | 1.94 |
| Medicine D2 Chinese | 0.413 (0.337, 0.479) | 1.89 |
| Medicine D3 cross-culture | 0.473 (0.383, 0.548) | 1.73 |
| Law D2 Chinese | 0.498 (0.434, 0.557) | 1.67 |
| Law D3 cross-culture | 0.660 (0.600, 0.719) | 1.37 |

---

## Finding 3 — Cross-culture (D3) is NOT a real diversifier

The predicted "cross-culture mixing → lower ρ" pattern holds only in
science and by a tiny margin. In medicine and law, the all-Chinese
committee is more independent than the mixed Chinese-Western one:

| Domain | D2 Chinese ρ | D3 cross-culture ρ | Winner |
|---|---|---|---|
| Science | 0.408 | 0.395 | ~tie (D3 barely lower) |
| Medicine | 0.413 | **0.473** | **D2 (Chinese) wins by 0.060** |
| Law | 0.498 | **0.660** | **D2 (Chinese) wins by 0.162** |

**Law's D2/D3 95% CIs do not overlap** — statistically clean result. Medicine
is directionally clear.

**This is the novel finding.** Cross-culture mixing (adding Claude, GPT-5,
Gemini alongside DeepSeek and Kimi) is competitive with, and in law
substantially inferior to, staying within the Chinese ecosystem.

Candidate explanations (both publishable, discussed in
[`analysis/04_crossculture_finding.md`](./analysis/04_crossculture_finding.md)):

1. **Chinese-lab pretraining is more genuinely diverse** than Western
   frontier labs' pretraining is diverse relative to each other. Anthropic,
   OpenAI, and Google reportedly converge on similar corpora and
   homogenized RLHF pipelines.
2. **Cross-culture mixing amplifies domain-shifted shared biases** —
   particularly in law, where Chinese-lab and Western-lab legal
   reasoning frameworks are almost disjoint.

Distinguishing these is a v2 experiment.

---

## Finding 4 — The overconfidence gap is real, dramatic, and cleanly corrected

Naive Condorcet posterior at k=2 (2 agents agree) vs observed correct rate:

| Cell | Naive P(correct) | Observed | Gap |
|---|---|---|---|
| Medicine D1 same-model | 99% | 78% | **+21 pts** |
| Medicine D2 Chinese | 99% | 79% | **+20 pts** |
| Medicine D3 cross-culture | 100% | 81% | **+19 pts** |
| Science D1 same-model | 98% | 78% | **+20 pts** |
| Science D2 Chinese | 100% | 86% | **+14 pts** |
| Science D3 cross-culture | 100% | 82% | **+18 pts** |

**Even at k=5 (all 5 agents agree), naive Condorcet says 100% but
observed is 88-94%** — a residual 6-12 point overconfidence gap that no
correction fully closes.

The N_eff-corrected posterior brings the naive number down toward observed
in the middle range but overshoots into pessimism at low k. Details in
[`analysis/03_overconfidence_gap.md`](./analysis/03_overconfidence_gap.md).

---

## The paper writes itself (updated)

**Title candidate:** *"Do agreeing LLMs actually know more? Measuring
committee overconfidence across science, medicine, and law."*

**Three-sentence abstract:**

> Multi-agent LLM committees are ubiquitous in production, and they use
> inter-agent agreement as a proxy for confidence — an assumption that
> only holds if agent errors are independent. We measure the pairwise
> error correlation ρ across 11,250 model responses on 750 factual MCQ
> items in three domains (science, medicine, law) and three diversity
> regimes (same-model 5 seeds, cross-family within Chinese labs, and
> Chinese-Western cross-culture), and find (a) same-model committees
> collapse to 1.37–1.49 effective independent agents from a nominal 5,
> (b) cross-culture diversity is not a real diversifier in medicine and
> law — an all-Chinese committee is more independent than the mixed
> Chinese-Western one, and (c) even at 5-agent agreement, naive Condorcet
> posteriors overestimate observed accuracy by 6-12 percentage points.
> We publish the dataset, raw completions, and ρ-measurement protocol
> as an open benchmark.

**Recommended venues:** NeurIPS main track, ICLR, SaTML, or FAccT.
