# Do agreeing LLMs actually know more?

**Working title.** *Measuring the overconfidence of multi-agent LLM
committees under three diversity regimes across science, medicine, and law.*

---

## Abstract (draft)

> Multi-agent LLM committees are ubiquitous in production systems, and
> they use inter-agent agreement as a proxy for confidence — an
> assumption that only holds if agent errors are independent. We measure
> the pairwise error correlation ρ across 11,250 model responses on 750
> multiple-choice factual items in three domains (science, medicine,
> law) and three agent-diversity regimes (same-model N seeds; cross-
> family within Chinese labs; cross-culture Chinese + Western labs). We
> find that (a) same-model committees collapse to 1.5–1.9 effective
> independent agents from a nominal 5, (b) cross-culture diversity does
> not uniformly reduce ρ — in law and medicine an all-Chinese-lab
> committee is more independent than a mixed Chinese-Western one, and
> (c) even the best-corrected posterior overestimates observed accuracy
> by 19–37 percentage points at k=2 agreement. We publish the 750-item
> dataset, the 11,250 raw completions, and the ρ-measurement protocol
> as an open benchmark.

## Contributions

1. **A design-effect correction for LLM consensus posteriors.** We port
   the survey-statistics design effect (Kish, 1965) to multi-agent LLM
   committees and give practitioners a plug-in overconfidence discount.
2. **A cross-domain ρ benchmark.** 750 items, three domains, three
   diversity regimes, three temperature settings, 11,250 completions
   across 8 frontier models — released publicly.
3. **A counter-intuitive empirical finding on cross-cultural diversity.**
   In law and medicine, an all-Chinese committee has lower ρ than a
   cross-culture one — the opposite of the prior expectation.
4. **A methodological note on agent-competence confounds in ρ
   measurement.** Adding a low-competence agent artificially lowers ρ
   without adding genuine diversification.

## Paper outline

### 1. Introduction

- Multi-agent LLM committees are everywhere (Devin, Cursor, Elicit,
  Harvey, Glass Health, WISE/MERL, dozens more)
- They all rest on agreement-as-confidence
- Agreement-as-confidence rests on independence
- Nobody has measured whether independence holds
- We measure it and give a correction

### 2. Related work

- Condorcet's Jury Theorem
- Design effect in survey statistics (Kish 1965; Kalton 1979)
- Ensemble diversity in classical ML (Kuncheva 2003; LLM-TOPLA 2024)
- Multi-agent LLM frameworks (AutoGen, CrewAI, LangGraph)
- WISE (Cherian et al., MERL ICML SCALE 2026) — assumes conditional
  independence in its Dawid-Skene aggregator, which our correction plugs into
- Boston University "LLMs Cannot Reliably Identify…" (S&P 2024) —
  evaluation methodology precedent
- LLMxCPG (USENIX Security 2025) — CPG-guided LLM detection precedent
- Wisdom and Delusion of LLM Ensembles for Code Generation (Simula 2025)
  — measures ρ on code only
- SecureAgentBench (arXiv 2509.22097) — agent benchmark using Semgrep
  for detection

### 3. Method

- **3.1 The design-effect correction.** Derivation from independence
  failure to effective committee size.
- **3.2 Bayesian Condorcet posterior.** P(correct | k agents agree) under
  independence and under N_eff correction.
- **3.3 Cluster analysis.** Bin items by largest same-answer cluster size k;
  measure observed correctness at each k.

### 4. Experimental setup

- **4.1 Dataset.** 750 factual MCQ items sourced from MMLU-Pro (250 each
  of STEM, Health, Law). Uniform C ≈ 10.
- **4.2 Committees.** N = 5 in every cell.
  - D1 same-model: 5 seeds of DeepSeek V4 at T = 0.7
  - D2 cross-family Chinese: DeepSeek V4 + Kimi K2 + Qwen 3 + GLM 4.6 +
    ByteDance Seed 1.6 at T = 0
  - D3 cross-culture: DeepSeek V4 + Kimi K2 + Claude Sonnet 4.6 +
    GPT-5-mini + Gemini 2.5 Pro at T = 0
- **4.3 Rate limiting.** Per-model concurrency (2-4) and requests/sec
  (3-5), routed through OpenRouter.
- **4.4 Reproducibility.** Every response record carries the temperature
  it was called at; D2 and D3 are bit-reproducible at T=0.
- **4.5 Analysis.** ρ per (domain × condition) with 500-iteration
  bootstrap CIs. Cluster analysis in the standard rho.py.

### 5. Results

- **5.1 Finding 1: D1 collapse.** Same-model committees deliver 1.55–1.88
  effective agents. (see analysis/01)
- **5.2 Finding 2: Cross-family diversity substantially reduces ρ but
  not to zero.** D2 and D3 land in 0.28–0.61 range; committees deliver
  1.85–2.38 effective agents. (see analysis/01)
- **5.3 Finding 3: Cross-culture is not a real diversifier.** In law and
  medicine, all-Chinese has lower ρ than cross-culture. Novel result.
  (see analysis/04)
- **5.4 Finding 4: The overconfidence gap.** At k=2, naive Condorcet
  overestimates observed correctness by 19–37 percentage points.
  (see analysis/03)
- **5.5 Ablation: agent-competence confound.** Excluding Kimi K2 raises
  D2/D3 ρ by 0.09–0.18. (see analysis/02)

### 6. Discussion

- The competence confound and its methodological implications
- Why cross-culture may fail in domain-shifted reasoning (Explanation A
  vs B in analysis/04)
- The corrected posterior's tendency to overshoot at low k — future
  work needs a more sophisticated correction than k · N_eff / N
- Threats to validity — MMLU-Pro contamination, Kimi truncation,
  3-domain scope (see LIMITATIONS.md)

### 7. Conclusion

- Multi-agent LLM committees are systematically overconfident
- The correction is small, portable, and empirically calibrated
- Cross-culture diversity is not automatically superior to same-culture
  diversity

### Data & code release

- Dataset: CC-BY-4.0 derivative of MMLU-Pro
- Code: MIT, GitHub repo `AbhiK24/agreeing-llms`
- 11,250 raw completions: released alongside paper

---

## Target venues

- **NeurIPS main track** — methodology contribution
- **ICLR** — reproducibility framing
- **ICML** — statistical connection to design effect
- **FAccT** — epistemic-trust framing
- **NeurIPS Datasets & Benchmarks** — if the released benchmark is the
  primary contribution

## Writing status

- [ ] Introduction
- [ ] Related work
- [ ] Method
- [ ] Experimental setup
- [ ] Results (each section pulls from `../analysis/`)
- [ ] Discussion
- [ ] Conclusion
- [ ] Figures (deferred to v2 with matplotlib plots)
- [ ] Bibliography

## v2 experiments needed to strengthen this

- Re-run Kimi K2 at max_tokens=4096 (see LIMITATIONS L2)
- Add a D4 "all Western" cell to distinguish Explanation A vs B
- Add a truly held-out benchmark (GPQA-Diamond or private test set) to
  address contamination
- N-agent ablation (N ∈ {3, 5, 7}) on one domain
- Multi-language variant to test cross-cultural diversity in a
  non-English setting
