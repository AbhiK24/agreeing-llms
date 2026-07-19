# Analysis 04 — The cross-culture finding (corrected scoring)

**Prior prediction:** D3 (cross-culture, Chinese + Western labs) should show
strictly lower ρ than D2 (all-Chinese) because cross-cultural pretraining
diversity is expected to add real independence.

**Result:** the prediction holds only in science and by a tiny margin.
In medicine and law, all-Chinese has *lower* ρ than cross-culture.

## The D2 vs D3 comparison (with Kimi, corrected scoring)

| Domain | D2 Chinese ρ (95% CI) | D3 cross-culture ρ (95% CI) | Difference (D3 − D2) |
|---|---|---|---|
| Science | 0.408 (0.33, 0.48) | 0.395 (0.31, 0.48) | −0.013 (tie) |
| Medicine | 0.413 (0.34, 0.48) | 0.473 (0.38, 0.55) | **+0.060 (D2 more independent)** |
| Law | 0.498 (0.43, 0.56) | 0.660 (0.60, 0.72) | **+0.161 (D2 more independent, CIs disjoint)** |

- **Science:** near-tie with heavy CI overlap. Cross-culture is not
  materially better than all-Chinese.
- **Medicine:** the all-Chinese committee is more independent than the
  mixed one. CIs overlap partially.
- **Law:** the all-Chinese committee is substantially more independent.
  **The 95% CIs are disjoint** — this is a statistically clean result.

## Kimi-excluded sensitivity check

We showed in `02_kimi_confound.md` that Kimi K2 is not an outlier under
the corrected parser. Nonetheless, an appendix analysis with Kimi removed
still supports the same direction:

| Domain | D2 without Kimi | D3 without Kimi | Δ |
|---|---|---|---|
| Science | 0.428 | 0.435 | +0.007 |
| Medicine | 0.484 | 0.549 | +0.065 |
| Law | 0.461 | 0.643 | +0.182 |

Direction preserved. The all-Chinese committee is at least as independent
as the mixed one in every domain, and materially more independent in law.

## Two candidate explanations

### Explanation A — Chinese labs are more genuinely diverse than Western labs

- DeepSeek, Kimi, Qwen, GLM, and ByteDance train on somewhat different
  Chinese-web corpora, different English-web slices, and different
  fine-tuning philosophies.
- Anthropic, OpenAI, and Google reportedly converge on very similar data
  distributions (Common Crawl + arXiv + curated instruction-following) and
  their RLHF preferences are strongly homogenized (constitutional AI
  approaches, similar red-teaming pipelines).
- Under this reading, "cross-culture" is not the diversifier — Chinese
  labs mixed among themselves are.

### Explanation B — Cross-culture mixing amplifies domain-specific shared biases

- Medicine has cross-cultural framework differences (traditional Chinese
  medicine vs. Western clinical reasoning; different guideline bodies).
- Law is entirely a cross-cultural difference — Chinese labs' law
  training is jurisdictionally different from Western labs' English
  common-law focus. When Chinese and Western models are asked about
  American common law, both groups may converge on shared
  English-Wikipedia framings that don't match the ground-truth answers.
- If Western models pull each other toward correlated Western-normed
  wrong answers on ambiguous items, cross-culture mixing (adding 3
  Western models to 2 Chinese ones) reintroduces shared bias.

### How to distinguish A from B in v2

- Add a D4 cell: **all-Western committee** (Claude + GPT + Gemini + a
  Western open-weights model like Llama or Mistral). If Western labs
  have low internal diversity, D4's ρ will be higher than D2's.
- Add a D5 cell: same Chinese-Western mix on a **translated Chinese
  legal-reasoning benchmark**. If the direction flips (D3 wins), then
  cultural-framework mismatch dominates.

## The paper's real headline

Not "cross-culture reduces ρ" (that was the prediction; it did not hold
outside science, and even in science the effect is negligible).

Instead:

> **Cross-culture LLM committees are not more diverse than same-culture
> Chinese-lab committees on domain-shifted reasoning tasks (medicine,
> law). In law, the all-Chinese committee is measurably more independent
> than the mixed Chinese-Western one.**

This is the opposite of the prior expectation, and — to our knowledge —
has not been published elsewhere. It reframes the "AI committee
diversity" conversation from "add different labs" to "add labs that are
genuinely differently trained."
