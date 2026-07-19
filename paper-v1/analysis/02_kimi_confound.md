# Analysis 02 — What the "Kimi confound" actually was (parser bug, not capability)

## Summary

The v0.1 sweep reported Kimi K2 at 20.4% accuracy, well below the 55-70%
cluster of every other frontier model. This looked like a competence
outlier that would confound ρ measurement.

**It was a parser bug.** Kimi K2 predominantly emits its answer in the
`LETTER) description` format that the v0.1 parser did not recognise.
Under the corrected parser, Kimi's accuracy is **55.4%** — right in the
middle of the cluster with everyone else. There is no capability outlier.

See [`00_parser_correction.md`](./00_parser_correction.md) for the full
mechanics of the bug and the recovery counts.

## What v0.1 got wrong (kept for the paper's transparency section)

The v0.1 analysis interpreted Kimi's low apparent accuracy as evidence
of a genuine competence gap and concluded that a low-accuracy agent
"artificially reduces measured ρ because its errors look uncorrelated by
luck of near-random guessing." That reasoning is technically sound *if*
the low accuracy is real — but here it wasn't.

With the corrected parser:

- Kimi K2 accuracy: 20.4% → **55.4%**
- Kimi K2 is not an outlier
- Excluding Kimi still slightly raises ρ in D2 (by 0.02-0.08) but the
  effect is minor and can be reported as a routine sensitivity check
  rather than a headline analytical choice

## Sensitivity check — ρ with Kimi excluded (corrected scoring)

| Cell | ρ with Kimi | ρ without Kimi | Δ |
|---|---|---|---|
| Science D2 Chinese | 0.408 | 0.428 | +0.020 |
| Science D3 cross-culture | 0.395 | 0.435 | +0.040 |
| Medicine D2 Chinese | 0.413 | 0.484 | +0.071 |
| Medicine D3 cross-culture | 0.473 | 0.549 | +0.076 |
| Law D2 Chinese | 0.498 | 0.461 | **−0.037** |
| Law D3 cross-culture | 0.660 | 0.643 | −0.017 |

Note that in **law D2**, removing Kimi actually *lowers* ρ (Kimi is
genuinely useful there). This confirms Kimi's errors are now correlated
with the other agents' errors — Kimi is producing meaningful, correlated
signal, not near-random guessing.

**The paper's D2 vs D3 comparison holds without Kimi exclusion:**

| Domain | D2 (with Kimi) | D3 (with Kimi) | D2 winner? |
|---|---|---|---|
| Science | 0.408 | 0.395 | tie |
| Medicine | 0.413 | 0.473 | yes (D3 higher = D2 more independent) |
| Law | 0.498 | 0.660 | yes, by 0.162 (non-overlapping CIs) |

Kimi exclusion is now a robustness check rather than a required
methodological choice.

## What this means for the paper

- **Drop the "excluded low-competence agent" section** from the primary
  analysis; report Kimi included as the primary result.
- **Keep a brief sensitivity-check appendix** showing Kimi-excluded
  numbers so reviewers can see the direction is preserved.
- **Report the parser correction transparently** in the methods section
  and in the pre-registered analysis log. This is a strength: the QA
  process found the bug before publication.

## GLM 4.6 is the new outlier — but it's real

GLM 4.6 sits at 38.1% accuracy — the true low end. GLM's `LETTER)` format
recovery was 0%, suggesting its unparseable rate is not driven by that
format bug. GLM likely IS being truncated at `max_tokens=1024` because
it's a reasoning model that emits chain-of-thought before the answer.

**v2 recommendation:** rerun GLM 4.6 at `max_tokens=4096` on all 750
items × 2 conditions (D2, D3) = 1500 calls. Expected cost: <$1.
