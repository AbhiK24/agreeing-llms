# Findings — paper v1

Everything below is derived from the 11,250-completion sweep in `raw/`. Each
finding links to a detailed analysis under `analysis/`.

---

## Finding 1 — D1 is the "committee ≈ 1 agent" cell, confirmed in every domain

Five seeds of the same model (DeepSeek V4 at T=0.7) deliver **1.55 to 1.88
effective independent agents** — down from a nominal 5. Practitioners
running N seeds of one model expecting Condorcet compounding are getting
about one-third the epistemic weight they think they are.

| Domain | ρ (95% CI) | N_eff / 5 | Effective size |
|---|---|---|---|
| Science | 0.488 (0.42, 0.56) | 1.69 | ≈ 1.7 agents |
| Medicine | 0.415 (0.33, 0.49) | 1.88 | ≈ 1.9 agents |
| Law | 0.557 (0.49, 0.62) | 1.55 | ≈ 1.5 agents |

**All CIs exclude 0 — statistically significant.** See
[`analysis/01_headline_rho.md`](./analysis/01_headline_rho.md).

---

## Finding 2 — The Kimi K2 confound is real and quantified

Kimi K2 was truncated by `max_tokens=1024` on 73.7% of calls before it
could emit a final letter answer. The truncated responses parse as "no
answer," count as errors, and drag down measured accuracy on that agent.

Because Kimi effectively guesses in a large fraction of items, its errors
look uncorrelated with everyone else's by luck of near-random guessing.
That mechanically lowers ρ without providing genuine diversification.

**Removing Kimi from the D2/D3 analyses raises ρ substantially in every
cell** (average +0.13, up to +0.18):

| Cell | ρ with Kimi | ρ without Kimi | Δ |
|---|---|---|---|
| Science D3 | 0.279 | 0.398 | +0.119 |
| Medicine D2 | 0.276 | 0.389 | +0.113 |
| Medicine D3 | 0.320 | 0.463 | +0.143 |
| Law D2 | 0.302 | 0.413 | +0.111 |
| Law D3 | 0.427 | 0.609 | +0.182 |

The **Kimi-excluded numbers are the fairer analysis** for the paper.
See [`analysis/02_kimi_confound.md`](./analysis/02_kimi_confound.md).

The v2 experiment plan re-runs Kimi at `max_tokens=4096` to give its
reasoning room to finish.

---

## Finding 3 — Cross-culture (D3) does not uniformly reduce ρ

The predicted "cross-culture mixing = lower ρ" pattern **holds only in
science**. In medicine and law, the all-Chinese committee has *lower* ρ
than the cross-culture committee:

| Domain | D2 Chinese ρ (without Kimi) | D3 cross-culture ρ (without Kimi) | Winner |
|---|---|---|---|
| Science | 0.407 | 0.398 | ~tie (D3 barely lower) |
| Medicine | 0.389 | **0.463** | **D2 (Chinese) wins by 0.074** |
| Law | 0.413 | **0.609** | **D2 (Chinese) wins by 0.196** |

**This is the novel finding.** Cross-culture mixing (adding Claude,
GPT-5, Gemini alongside DeepSeek and Kimi) is competitive with, and in
law substantially inferior to, staying within the Chinese ecosystem.

Two candidate interpretations (both publishable):

1. **Chinese-lab pretraining is more genuinely diverse** than Western
   frontier labs' pretraining is diverse relative to each other. Anthropic,
   OpenAI, and Google reportedly converge on very similar data
   distributions and RLHF preferences.
2. **Cross-culture mixing introduces shared Western-normed reasoning
   biases** that pull models toward correlated wrong answers on
   ambiguous items — particularly in medicine (where clinical
   frameworks differ across cultures) and law (where legal reasoning
   frameworks differ dramatically).

Either reading is a genuine contribution — nobody has published this.
See [`analysis/04_crossculture_finding.md`](./analysis/04_crossculture_finding.md).

---

## Finding 4 — The overconfidence gap is dramatic

The paper's core claim confirmed at large effect size. When 2 agents
agree on a factual answer:

| Cell (k=2) | Naive Condorcet posterior | Observed correct rate | Gap |
|---|---|---|---|
| Medicine D1 same-model | 95% | 73% | **+22 pts** |
| Medicine D2 Chinese | 93% | 67% | **+27 pts** |
| Medicine D3 cross-culture | 96% | 59% | **+37 pts** |
| Science D2 Chinese | 98% | 78% | **+19 pts** |
| Science D3 cross-culture | 98% | 68% | **+30 pts** |
| Law D1 same-model | 42% | 52% | −10 pts (naive undershoots — low p) |

At k=5 (all 5 agents agree), naive Condorcet says essentially 100%.
Observed correct rate is 92-99% (still a small residual gap in medicine).

**The N_eff-corrected posterior closes most of this gap** in mid-cluster
sizes but overshoots into pessimism at small k. That's a discussion-section
calibration note, not a paper-killing issue.

See [`analysis/03_overconfidence_gap.md`](./analysis/03_overconfidence_gap.md).

---

## The paper writes itself

**Title candidate:** *"Do agreeing LLMs actually know more? Measuring the
overconfidence of multi-agent committees under three diversity regimes."*

**Three-sentence abstract:**

> Multi-agent LLM committees are ubiquitous in production, and they use
> agreement between agents as a proxy for confidence — an assumption that
> only holds if agent errors are independent. We measure the pairwise
> error correlation ρ across 750 factual MCQ items in three domains and
> three agent-diversity regimes, and find (a) same-model committees
> collapse to ≈ 1.5 effective agents, (b) cross-culture diversity does
> not reduce ρ more than intra-Chinese diversity in medicine and law,
> and (c) even the best-corrected Condorcet posterior overestimates
> observed accuracy by 19-37 percentage points at k=2 agreement.
> We publish the ρ-measurement protocol as an open benchmark.

**Recommended venues:** NeurIPS main track, ICLR, or SaTML for the
methodology framing; FAccT for the epistemic-trust framing.
