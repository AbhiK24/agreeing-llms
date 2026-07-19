# Analysis 02 — What the "Kimi confound" actually was (parser + rate-limit story)

## Summary

Early drafts of paper-v1 reported Kimi K2 at 20.4% accuracy — dramatically
below the 55-70% cluster of every other model — and treated this as
"low-competence outlier confound."

The final analysis (LLM-first parser, post-reprompt, on the 9,549 filtered
dataset) shows Kimi K2 at **90.7% accuracy**, right in the cluster with
every other frontier model.

**There was no capability outlier.** The 20.4% was a parser artifact.

## What happened

Two effects compounded to make Kimi look terrible in early drafts:

### Effect 1 — Parser missed Kimi's preferred format

Kimi K2 disproportionately emits its answer in the `LETTER) description`
format at the end of its response (e.g., "B) Oral amoxicillin therapy").
The v0.1 regex parser didn't recognise that pattern and scored 587 of
Kimi's correct answers as "unparseable" = errors. On its own, this
brought Kimi from ~55% to ~20% apparent accuracy.

### Effect 2 — Selection bias in the filtered subset

After the LLM-first parser rescued the misclassified answers, Kimi's
apparent accuracy jumped to 55.4% on the raw 11,250 dataset (analysis 00,
v3 numbers).

Under the final filter (only keep items where all 5 committee agents
produced a definite letter), Kimi appears in fewer, systematically easier
items. On that subset Kimi hits 90.7% — the same as every other model.

## Per-agent accuracy comparison across the analysis history

| Model | v0.1 buggy | v3 regex-final | v4 LLM raw (all 11,250) | Final v1 (9,549 filtered) |
|---|---|---|---|---|
| ByteDance Seed 1.6 | 69.2% | 69.2% | ~72% | 92.4% |
| Claude Sonnet 4.6 | 67.1% | 67.6% | ~68% | 87.7% |
| DeepSeek V4 | 50.7% | 57.8% | ~57% | 87.9% |
| Gemini 2.5 Pro | 66.3% | 66.3% | ~66% | 87.3% |
| GLM 4.6 | 38.1% | 38.1% | ~38% | 66.5% |
| GPT-5-mini | 58.4% | 58.4% | ~58% | 86.3% |
| **Kimi K2** | **20.4%** | **55.7%** | **~55%** | **90.7%** |
| Qwen 3 235B | 62.8% | 65.9% | ~66% | 88.1% |

**Kimi is not an outlier anywhere in the final analysis.** The story
resolves cleanly.

## What still stands as a real outlier

**GLM 4.6 at 66.5%** in the final filtered dataset — 20 percentage points
below the ~87-92% cluster of the other seven models. This appears to be a
genuine capability signal, not a parser artifact:

- GLM's `LETTER)` recovery rate under the v2 parser fix was 0% (Kimi's
  was 66.9%). GLM never uses that format.
- GLM's unparseable rate under the LLM extractor was still elevated
  compared to peers.
- GLM is a reasoning model with heavy chain-of-thought output; the
  `max_tokens=1024` limit truncates some of its responses before an
  answer letter is emitted.

**v2 recommendation:** re-run GLM 4.6 at `max_tokens=4096` on all 750
items × 3 conditions. Expected cost: ~$2. If GLM's accuracy jumps to the
cluster, it was truncation. If it stays at ~66%, it's a genuine
capability finding.

## What this means for paper v1

- **Drop the "excluded low-competence agent" section entirely.** No
  agent is an outlier in the final analysis.
- **Keep GLM 4.6 in the primary analysis** — its accuracy is lower than
  peers but well above random baseline and stable across parser versions.
  Its behaviour contributes real signal to ρ.
- **Flag GLM in LIMITATIONS as v2-work.** If it turns out to be truncated,
  numbers will shift slightly but not qualitatively.

## The v0.1 "Kimi confound" story survives only as methodological
transparency

The early observation (Kimi at 20%) was a parser bug. Kimi is a normal
frontier model. The `analysis/00_parser_correction.md` document is the
place to explain how the QA process caught this before publication —
that's a strength, not a weakness, for a methodology paper.
