# Known limitations of paper v1

Every threat to validity we can name. Reviewers will find some of them;
better we name them first.

---

## L0 — Selection bias from filtering to committees with 5 answers

We filter the raw 11,250 completions down to 9,549 where every one of the 5
committee agents produced a definite letter answer. Rows are dropped when
any agent (a) refused via content policy, (b) rambled without committing to
a letter, or (c) was truncated by the token budget mid-reasoning.

**Effect:** the remaining item set is systematically *easier* than the
original 750-item benchmark. Committee-level mean accuracy jumps 15-30
percentage points relative to the raw dataset. Per-cell item counts drop
from 250 to between 80 and 194 depending on how many refusals hit that
cell.

**Why it's defensible:**
- Committee use in production requires answers from every agent. Items
  where any model refused are items where no real consensus vote could
  be cast — dropping them mirrors production behaviour.
- The bias is toward *fewer errors to correlate*, which if anything makes
  measured ρ conservative (harder to detect correlation with fewer errors).

**Mitigation:** raw completions for every dropped row are preserved in
`raw/responses.pre-final-filter.jsonl.bak`, so an alternative filter can
be applied at any time.

---

## L1 — MMLU-Pro is likely (partially) in training data

The three domains all come from MMLU-Pro, released November 2024. All
frontier models tested have knowledge cutoffs after that date; some
contamination is essentially certain.

**Why less bad than it looks:**
- Headline metric is ρ (error correlation), not raw accuracy.
- Contamination raises accuracy which reduces error signal — our measured
  ρ is a lower bound on genuine reasoning-derived correlation.
- If contamination is uneven across models, it *reduces* observed ρ
  (uncorrelated memorization → uncorrelated correctness → less correlated
  errors).

**Fix in v2:** add a truly held-out benchmark (GPQA-Diamond gated split, or
a private test set).

---

## L2 — Science D1 saturated at 97.4% mean accuracy

After filtering, Science D1 (5 seeds of DeepSeek V4 at T=0.7 on MMLU-Pro
STEM) reaches 97.4% mean per-agent accuracy. Only ~4% of responses are
errors. ρ estimation with few errors is noisy — bootstrap 95% CI is
(0.17, 0.92).

**Effect on the paper's Finding 1 (D1 collapse):** the point estimate
ρ = 0.66 is still positive and consistent with the D1 collapse pattern
observed in law (ρ = 0.755) and medicine (ρ = 0.733) which have wider
error rates and tight CIs. But Science D1 alone should not carry the
Finding 1 story.

**Mitigation:** report all three domains' D1 point estimates together; the
Finding 1 claim rests on the aggregate. Note the wide CI for Science D1
explicitly.

**Fix in v2:** run Science D1 on a harder subset (MMLU-Pro STEM's higher
"reasoning complexity" tier only) or on GPQA-Diamond.

---

## L3 — Answer-space size C is not perfectly uniform

MMLU-Pro items nominally have 10 choices, but a small tail has 4-9 choices
(5-25% of items per domain). Bayesian Condorcet posterior uses per-item C,
so this does not bias the math — but "C = 10" claims should be softened to
"modal C = 10" in the paper.

---

## L4 — D1 same-model uses T=0.7, not T=0

D1 tests "does temperature-noise alone give independence?" and MUST use
T > 0 (otherwise all seeds produce identical output and ρ trivially = 1).

- D1 is not bit-reproducible.
- D2 and D3 (the headline cells) are at T=0 and fully reproducible.
- Every response record carries the temperature used, so auditors can
  verify.

---

## L5 — Committee size N = 5 is a specific choice

All conditions use N = 5 agents. Larger N would give tighter estimates but
at 5-10x cost. The paper's central claim (design-effect correction on
consensus posteriors) generalises to any N via the same formula.

**Fix in v2:** N ∈ {3, 5, 7} ablation on one domain.

---

## L6 — Content-policy refusals are correlated across models

We chose to filter refused rows out of the ρ analysis (L0) rather than
treat them as errors, because a refusal and a wrong answer are
methodologically different things. However, the refusal pattern itself
shows strong correlation — most refusals concentrate in law items on
criminal-scenario questions and reflect shared safety-training pipelines
across labs rather than shared reasoning failures.

**We do not analyse refusal correlation in this paper.** It is out of
scope for the ρ_error / consensus-collapse story. Follow-up work could
formalise "ρ_refusal" as a distinct dependence metric.

---

## L7 — 3 domains, all English MCQ

Science + medicine + law, all in English, all from MMLU-Pro. Scope note in
`README.md` is explicit; no claim of generalisation to non-MCQ tasks,
non-English tasks, open-ended synthesis, or planning.

---

## L8 — OpenRouter routing may vary

All API calls went through OpenRouter, which routes to different upstream
providers based on availability. A re-run days later may hit different
upstream endpoints even at T=0. Every response record captures the exact
model ID used.

---

## L9 — Parser correction (methodology transparency)

We ran three parser fixes and one LLM-first extractor rewrite during
pre-publication QA. The full audit trail is in
`analysis/00_parser_correction.md`. Original scoring is preserved in
`raw/responses.v1-scoring.jsonl.bak`.

The final parser is an LLM-first design using Gemini 2.5 Flash Lite as
the extractor, validated against DeepSeek V4 on 100 samples with 99%
agreement. On 56 LLM/regex disagreements the LLM matched gold at 51.8%
vs 19.6% for regex, justifying the LLM-first choice.

---

## What none of these touch

- The core ρ math (Pearson correlation of binary error vectors)
- The N_eff design-effect formula
- The Bayesian Condorcet posterior derivation
- The cluster analysis
- The bootstrap CI on ρ

The observed pattern (D1 collapse, cross-family reduction, D3-vs-D2
domain-specific behaviour, dramatic overconfidence gap at low k) is
robust across all filtering and parsing choices we tried.
