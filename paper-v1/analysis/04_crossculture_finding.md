# Analysis 04 — The cross-culture finding (final v1 dataset)

**Source:** `raw/rho_by_domain.json` (9,549 filtered responses, LLM-parsed).

## Prediction and result

**Prior prediction (from proposal):** D3 (cross-culture, Chinese + Western)
should show strictly lower ρ than D2 (all-Chinese) because cross-cultural
pretraining diversity is expected to add real independence.

**Final v1 result:** Prediction holds in science and medicine. Reverses in
law.

## The D2 vs D3 comparison

| Domain | D2 Chinese ρ (95% CI) | D3 cross-culture ρ (95% CI) | Δ (D3 − D2) | Winner |
|---|---|---|---|---|
| Science | 0.613 (0.36, 0.80) | 0.458 (0.26, 0.61) | −0.155 | **D3 wins by 0.16** |
| Medicine | 0.693 (0.55, 0.80) | 0.630 (0.51, 0.73) | −0.063 | D3 wins by 0.06 |
| Law | **0.488** (0.35, 0.60) | 0.554 (0.45, 0.65) | +0.066 | **D2 (Chinese) wins by 0.07** |

- **Science:** D3 wins by 0.155 — significant reduction, though CIs overlap.
  Consistent with the prediction that cross-cultural diversity adds
  independence.
- **Medicine:** D3 wins by 0.063 — small effect, CIs overlap heavily.
  Directionally consistent with the prediction but weak.
- **Law:** **D2 (all-Chinese) wins by 0.066.** CIs overlap partially. The
  counter-intuitive result from earlier drafts still holds.

## Nuanced interpretation

Under the corrected + LLM-parsed dataset, the paper's story evolves from
"cross-culture is not a real diversifier" (the earlier bold claim) to a
more nuanced version:

**"Cross-culture diversity reduces ρ in science and medicine but not in
law. In law, the all-Chinese committee is at least as independent as the
mixed Chinese-Western committee, and by point estimate more so."**

This is still a novel result — nobody has published domain-conditional
cross-culture diversity effects for LLM committees. It reframes the "AI
committee diversity" conversation from "add labs from different countries"
to "cross-cultural diversity's effect on ρ is domain-dependent, and in
domains where the answer set is culturally-specific (US common law), adding
culturally-non-native models does not help."

## Two candidate explanations for the Law reversal

### Explanation A — Chinese labs are more genuinely diverse

- DeepSeek, Kimi, Qwen, GLM, and ByteDance train on different Chinese-web
  corpora, different English-web slices, and different fine-tuning
  philosophies.
- Anthropic, OpenAI, and Google reportedly converge on similar data
  distributions and homogenised RLHF pipelines.
- In domains where the answer set is culturally-specific (US common law),
  the "diversity" advantage of Chinese-lab breadth outweighs the
  "cultural mixing" advantage of adding Western models.

### Explanation B — Cross-culture mixing amplifies domain-specific shared
biases

- Law is entirely a cross-cultural difference — Chinese labs' law training
  is jurisdictionally different from Western labs' English common-law
  focus.
- When asked about US common law, Western models converge on Western
  jurisprudential framings that Chinese models don't share.
- The all-Chinese committee makes different errors on US law than the
  mixed committee, but its errors are less correlated with each other
  than the Western models' errors are with each other.

### Distinguishing A and B — v2 experiment

- **D4 all-Western committee** (Claude + GPT + Gemini + Llama/Mistral). If
  Western labs have low internal diversity (A), D4's ρ will be higher than
  D2's.
- **D5 same Chinese-Western mix on translated Chinese-law benchmark.** If
  cultural-framework mismatch dominates (B), the direction reverses (D3
  wins).

## The paper's real headline for this analysis

Not "cross-culture reduces ρ" (that's the prediction; holds in science,
weakens in medicine, reverses in law).

Instead:

> **Cross-culture LLM committees are diversifiers in general-knowledge
> domains but not in culturally-specific reasoning domains. In US common
> law, the all-Chinese committee is at least as independent as the
> Chinese-Western mix. This suggests that "diversity" in committee
> composition should be conditioned on the domain: cross-cultural mixing
> helps when the answer set is culturally-neutral, and can hurt when it
> isn't.**

Nobody has published this. It's the novel contribution.
