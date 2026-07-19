# Known limitations of paper v1

Every threat to validity we can name. Reviewers will find some of them;
better we name them ourselves first.

---

## L1 — MMLU-Pro is likely (partially) in the training data

The three domains all come from MMLU-Pro, released November 2024. All
frontier models tested here have knowledge cutoffs after that date, and
Hugging Face-hosted datasets are routinely scraped into pretraining
corpora. **Some contamination is essentially certain.**

**Why this may be less bad than it looks for ρ measurement:**

- Our headline metric is **ρ**, not raw accuracy.
- Contamination raises accuracy (memorized answers are correct), which
  reduces the number of errors, which reduces the raw *signal* for ρ but
  does not directly bias the correlation structure of the remaining errors.
- If contamination is uneven across models (e.g., DeepSeek scraped
  differently from Claude), it could reduce ρ mechanically (uncorrelated
  memorization → uncorrelated correctness → less correlated errors).
  This means our observed ρ is likely a **lower bound** on true
  reasoning-derived correlation.

**Fix in v2:** add a truly held-out benchmark — either GPQA-Diamond
(gated to prevent scraping) or a private test set the authors construct.
The current design accepts contamination as a caveat and reports what we
have.

---

## L2 — Original "Kimi K2 truncation confound" was actually a parser bug

During pre-publication sanity checks we discovered the v0.1 parser missed
the `LETTER) description` answer format (see
[`analysis/00_parser_correction.md`](./analysis/00_parser_correction.md)).
Kimi K2 uses this format more than any other model — 66.9% of its
apparent "unparseable" responses were in fact recoverable correct answers.

**After the parser fix:** Kimi K2's accuracy is 55.4%, right in the
cluster with every other model (55-70%). It is not a competence outlier,
and no analytical mitigation is needed. `analysis/02_kimi_confound.md`
retains a brief Kimi-excluded sensitivity check for transparency.

**Remaining truncation concern:** GLM 4.6 (a reasoning model) sits at
38.1% accuracy under the corrected parser, well below the 55-70% cluster.
Its `LETTER)` recovery rate was 0%, indicating a genuinely different
issue — likely token-budget truncation on reasoning traces before the
answer letter is emitted.

**Fix in v2:** re-run GLM 4.6 at `max_tokens=4096` on all 750 items × 2
conditions (D2, D3) = 1,500 calls. Expected cost: <$1.

---

## L3 — Answer-space size C is not perfectly uniform

MMLU-Pro items nominally have 10 choices, but a small tail has 4-9
choices (5-25% of items per domain). Our Bayesian Condorcet posterior
uses the per-item C, so this does not bias the math — but it does mean
"C = 10" claims should be softened to "modal C = 10" in the paper.

---

## L4 — D1 same-model uses T = 0.7, not T = 0

D1 tests "does temperature-noise alone give independence?" and MUST use
T > 0 because otherwise all seeds produce identical output and ρ trivially
= 1. This means:

- D1 is **not** bit-reproducible.
- D1 is technically a "stochastic-only baseline," not a headline claim.
- Reviewers can (and should) verify D2 and D3 at T = 0.

Every response record carries the temperature it was called at, so an
auditor can independently verify D2/D3 rows are T = 0.

---

## L5 — 5 agents is a specific choice

All conditions use N = 5 agents. Larger N would give tighter N_eff /
posterior estimates but at 5x-10x more cost. The paper's central
claim (design-effect correction on consensus posteriors) generalizes to
any N via the same formula; we do not empirically ablate N.

**Fix in v2:** add an N = 3 and N = 7 ablation on one domain (probably
medicine) to demonstrate the scaling.

---

## L6 — Cluster tie-breaking at k=1

When all 5 agents disagree (no cluster of size > 1), our "largest
cluster" analysis picks the first-listed answer in `pandas.value_counts()`,
which is a deterministic-but-arbitrary tiebreak. This shows up as noisy
observed correct rates in the k=1 bin (see `analysis/03_overconfidence_gap.md`,
low-k rows).

The k=1 bin is not part of any headline claim, but the numbers in that
row of the report table are less meaningful than k >= 3.

---

## L7 — 3 domains, all Western-language MCQ

We test science + medicine + law, all in English, all sourced from
MMLU-Pro (originally an English benchmark). The paper does not claim
generalization to:

- Non-MCQ tasks (open-ended generation, code, planning)
- Non-English tasks
- Domains not tested (economics, arts, philosophy)
- Real production tasks (customer support, coding agents, research assistance)

The scope note in `README.md` is explicit about this.

---

## L8 — OpenRouter routing may vary

All 11,250 calls went through OpenRouter's gateway. OpenRouter routes to
different upstream providers based on availability, cost, and health.
A re-run days later may hit different upstream endpoints even at
`temperature=0`. Every response record captures the exact model ID that
answered, and OpenRouter documents the upstream provider per call in
its dashboard.

**Bit-level reproducibility at T=0 depends on the upstream provider not
changing.** As long as `openrouter → deepseek/deepseek-v4-pro` routes to
DeepSeek's actual v4-pro endpoint, results are stable.

---

## L9 — Some rate-limit and 5xx-triggered retries

The runner backs off on transient failures (rate limits, 500s, timeouts)
and re-tries up to 5 times. The final `responses.jsonl` contains only
successful calls; retried failures are silently absorbed. This means the
raw sweep did not encounter zero errors — it encountered zero
*unrecoverable* errors. That is the intended behavior.

---

## What none of these limitations touch

- The core ρ math (Pearson correlation of binary error vectors)
- The N_eff design-effect formula (imported from survey statistics)
- The Bayesian Condorcet posterior derivation
- The cluster analysis (bin items by largest same-answer cluster)
- The bootstrap CI on ρ (500 iterations, sampling items with replacement)
- The Kimi-excluded ρ analysis (still uses genuine errors from 7 competent agents)

The observed **pattern** — D1 collapses to ρ ≈ 0.5, D2/D3 land around
0.3-0.5, cross-culture underperforms same-culture Chinese in law and
medicine, and the k=2 overconfidence gap is 20-40 percentage points —
is robust across all analytical choices.
