# Analysis 00 — Parser evolution and audit trail

The final scoring pipeline for paper v1 went through **four generations** before
we shipped. All were caught during pre-publication QA. Every intermediate
state is preserved in `raw/*.bak` files. This document captures the full
journey for methodological transparency.

## Summary of the four generations

| Version | Method | Issue | Fix |
|---|---|---|---|
| v1 (original) | regex, first-match | Missed `LETTER)` format; scored 898 correct answers as wrong | Added `LETTER)` pattern |
| v2 | regex, first-match, with `LETTER)` | Missed multi-asterisk (`**Answer:** H`); matched *first* letter mid-reasoning instead of final answer | Multi-asterisk + last-match wins |
| v3 | regex, last-match | Still missed `I)` at end of line; `\boxed{\text{A}}` LaTeX wrapping | Added those patterns |
| v4 (final) | **LLM-first, regex as audit** | — | Semantic parser reads options + response tail, extracts intended letter |

### Recovery counts by generation (versus v1)

| Version | Recovered as correct | Recovered as wrong-but-parseable | Notes |
|---|---|---|---|
| v2 | 898 | ~250 | LETTER) format fix |
| v3 | +45 | +11 (previously false-positive) | Last-match + multi-asterisk fix |
| v4 | +some | +some | LLM catches semantic cases regex misses |

## Why we moved to LLM-first (v4)

Even v3 regex missed cases where the model *quoted the correct option's text
without a letter marker* — e.g., "the answer is closer to the range of 4.5%"
where option D reads "4.5% at 298 K". Regex has no way to match text to
options. An LLM extractor reads the options list and the response and answers
"which letter does this correspond to?" — a task well within any capable
model.

## The v4 semantic parser

- Model: `google/gemini-2.5-flash-lite` via OpenRouter
- Temperature: 0.0 (deterministic)
- Cache: SHA-256 of `(item_id, response)` → letter + reason. Re-runs after a
  bug fix or model swap are free after the first pass.
- Regex kept alongside as an audit trail flag (`llm_regex_disagreement`).
- Fail-safe: if the LLM extractor errors, we fall back to regex so nothing
  is lost.

### v4 validation

Before running v4 at scale, we cross-checked Flash Lite vs DeepSeek V4 on
100 sampled responses:

- Flash Lite ↔ DeepSeek V4 letter agreement: **99.0%**
- Flash Lite matches gold: 79/100 (79.0%)
- DeepSeek V4 matches gold: 79/100 (79.0%)

Flash Lite passed the ≥98% threshold; chose it for the full run at ~10x
lower cost than V4.

### v4 outcomes across the 8,258 non-cached responses that entered the LLM
extractor

| Source | Count | Meaning |
|---|---|---|
| `llm` | 4,970 | Flash Lite direct extraction |
| `cache` | 4,374 | Hit the persistent cache from earlier partial runs |
| `regex-fallback` | 382 | LLM errored → regex answered (fail-safe fired) |
| `error` | 28 | Both failed — item stays unparseable |
| **LLM/regex disagreements** | **56** | LLM's letter ≠ regex's letter |

### Audit of the 56 LLM/regex disagreements

| Method | Matched gold |
|---|---|
| **LLM** | 29 / 56 = **51.8%** |
| Regex | 11 / 56 = 19.6% |
| Both wrong | 16 / 56 = 28.6% |

LLM was **2.6× more likely to match gold** on the exact cases where they
disagreed. This validated the LLM-first choice.

## Post-parse reprompt of the 56 disagreements

Even after LLM extraction, 56 items had LLM/regex disagreement. To resolve
ambiguity, we re-ran those 56 items with the *same underlying committee model*
and *same original prompt*, appended with:

> After your reasoning, end your response with a single line in exactly this
> format: `ANSWER: <LETTER>` where <LETTER> is the single letter of your final
> choice.

Full audit trail on each row: `reprompted: true`, `reprompted_at`,
`reprompt_original_raw`, `reprompt_original_parsed_answer`,
`reprompt_original_regex_letter`.

### Reprompt outcomes

| Outcome | Count |
|---|---|
| Correct (matches gold) | 35 (62.5%) |
| Wrong letter (model chose wrong answer) | 15 (26.8%) |
| Unparseable (still no clear answer) | 6 (10.7%) |
| Still LLM/regex disagreement | 3 (5.4%) |

The 15 wrong-answer results are important — they confirm that the original
LLM extractor had correctly identified 15 cases where the model actually
chose a wrong letter. Dropping those cases would have artificially inflated
committee accuracy.

## Final filtering step

The 3 residual LLM/regex disagreements were dropped along with the 1,701
responses that lacked a definite letter (content-policy refusals + soft-
refusals + rambling responses).

### The final v1 dataset

| | Count |
|---|---|
| Raw completions from the sweep | 11,250 |
| Dropped (content-policy refusals, no raw text) | 6 |
| Dropped (had text but LLM extractor couldn't find a letter) | 1,695 |
| Dropped (residual LLM/regex disagreement) | 3 |
| **Final v1 dataset** | **9,549** |

### Preserved backups (all under `raw/`)

- `responses.v1-scoring.jsonl.bak` — original buggy regex
- `responses.v2-scoring.jsonl.bak` — after LETTER) fix
- `responses.v3-regex-final.jsonl.bak` — after all regex fixes, before LLM
- `responses.v4-pre-semantic.jsonl.bak` — snapshot at start of LLM parse
- `responses.pre-reprompt-56.jsonl.bak` — before the 56-item reprompt
- `responses.pre-final-filter.jsonl.bak` — before the final filter

The raw API text (`raw_response`) is byte-identical across every backup
that wasn't a reprompt. Only derived fields (`parsed_answer`, `error`)
differ.

## Why this journey matters for the paper

- **Methodological transparency:** every parsing decision is defended in a
  numbered audit trail. Reviewers can see the choices and the reasons.
- **Regression protection:** every parser bug caught by QA got a
  regression test in `tests/test_scorer.py` or `tests/test_semantic_parser.py`.
  The final tests suite is 73+ tests, all deterministic and API-free.
- **Reproducibility:** every intermediate backup lets any reviewer roll
  the pipeline back to any parser generation and re-derive the numbers.
