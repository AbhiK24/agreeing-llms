# Analysis 04 — The cross-culture finding

**Prior prediction:** D3 (cross-culture, Chinese + Western labs) should show
strictly lower ρ than D2 (all-Chinese) because cross-cultural pretraining
diversity is expected to add real independence.

**Result:** the prediction holds only in science, and reverses substantially
in medicine and law.

## The D2 vs D3 comparison (Kimi excluded, since Kimi's truncation confounds both)

| Domain | D2 Chinese ρ (without Kimi) | D3 cross-culture ρ (without Kimi) | Difference (D3 − D2) |
|---|---|---|---|
| Science | 0.407 | 0.398 | −0.009 (near-tie) |
| Medicine | 0.389 | 0.463 | **+0.074** |
| Law | 0.413 | 0.609 | **+0.196** |

- Science shows a *slight* D3 win (−0.009), consistent with the prior
  prediction but well within noise.
- Medicine and law show D2 winning — the all-Chinese committee is more
  independent (lower ρ) than the cross-culture one.
- The law effect is particularly large: cross-culture ρ is nearly 50%
  higher than same-culture Chinese ρ.

## Two candidate explanations, both publishable

### Explanation A — Chinese labs are more genuinely diverse than Western labs

- DeepSeek, Kimi, Qwen, GLM, ByteDance train on somewhat different
  Chinese-web corpora, different English-web slices, and different
  fine-tuning philosophies.
- Anthropic, OpenAI, Google reportedly converge on very similar data
  distributions (Common Crawl + arXiv + curated instruction-following)
  and their RLHF preferences are strongly homogenized (constitutional AI
  approaches, similar red-teaming pipelines).
- Under this reading, "cross-culture" is not the diversifier — Chinese
  labs mixed among themselves are.

### Explanation B — Cross-culture mixing amplifies domain-specific shared biases

- Medicine has genuine cross-cultural framework differences (traditional
  Chinese medicine vs. Western clinical reasoning; different guideline
  bodies).
- Law is entirely a cross-cultural difference — Chinese labs' law
  training is jurisdictionally different from Western labs' English
  common-law focus.
- If Western models pull each other toward correlated Western-normed
  wrong answers on ambiguous items, cross-culture mixing (adding 2
  Western models to 2 Chinese ones) reintroduces shared bias.

### How to distinguish A from B in v2

- Add a D4 cell: **all-Western committee** (Claude + GPT + Gemini + a
  Western open-weights model like Llama or Mistral). If Western labs
  have low internal diversity, D4's ρ will be higher than D2's.
- Add a D5 cell: same Chinese-Western mix, but on a translated Chinese
  legal-reasoning benchmark. If the direction flips, cultural-framework
  differences dominate.

## Statistical significance

D3 − D2 differences (Kimi excluded):

| Domain | Δ | Both CIs |
|---|---|---|
| Science | −0.009 | D2 (0.33, 0.49), D3 (0.31, 0.49) — heavy overlap |
| Medicine | +0.074 | D2 (0.31, 0.46), D3 (0.37, 0.55) — light overlap |
| Law | +0.196 | D2 (0.34, 0.48), D3 (0.54, 0.68) — **non-overlapping CIs** |

The **law finding is statistically significant** (non-overlapping 95% CIs).
Medicine is directionally clear but not fully separated at the 95% level.
Science is a tie.

## The paper's real headline

Not "cross-culture reduces ρ" (that was the prediction; it did not hold).

Instead: **"Cross-culture LLM committees are not more diverse than
same-culture Chinese-lab committees on domain-shifted reasoning tasks
(medicine, law). This is the opposite of the prior expectation and
suggests that intra-culture diversity is competitive with cross-culture
diversity for practical committee composition."**

Nobody has published this. It's the novel contribution.
