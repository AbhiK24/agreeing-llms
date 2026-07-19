# Analysis 00 — Parser correction (found during QA, before publication)

## Summary

The first sweep used a parser that missed the `LETTER) description` answer
format — one of the most common LLM output patterns for MCQ. **898 out of
11,250 responses (8.0%) were miscoded as errors when they were in fact
correct answers.** Detection happened during pre-publication sanity checking,
before any external release.

We re-parsed all 11,250 stored responses with a fixed parser and
regenerated every downstream artifact. Raw API text is preserved
unchanged; only the derived `parsed_answer` and `error` columns were
recomputed.

## What the bug was

The v0.1 parser matched patterns like `"answer is B"`, `"\boxed{B}"`,
`"**B**"`, `"(B)"`, and lone letters on their own line. It did **not**
match responses of the form:

```
B) Oral amoxicillin therapy
```

which is what many LLMs emit when they simply name the chosen option
verbatim. The model IS answering — it's just quoting the labelled option
itself.

## Sample of miscoded-as-wrong responses

```
[science-003437, gold=I, agent=kimi_k2]
"I) a population's gene frequency"

[medicine-006040, gold=B, agent=deepseek_v4]
"B) Oral amoxicillin therapy"

[medicine-006425, gold=B, agent=deepseek_v4]
"B) to be palpable both intra- and extraorally."
```

All three were correct answers, all scored as errors.

## The fix

Added a final pattern that fires only if the **last non-empty line** of
the response contains exactly one `LETTER) …` occurrence. The
"exactly one" guard prevents false positives from mid-reasoning
discussions like *"Options: A) foo B) bar C) baz"*, where the intended
answer could be any of the letters or none of them.

Regression test in `tests/test_scorer.py::test_parse_mcq_extracts_letter_paren_format`
plus a negative test `test_parse_mcq_does_not_confuse_option_listings_in_long_reasoning`
pin the fix.

## Full impact — recoveries per agent

| Model | Unparseable calls in v0.1 | Recovered as correct | % of unparseable recovered |
|---|---|---|---|
| DeepSeek V4 | 1336 | 353 | 26.4% |
| **Kimi K2** | **878** | **587** | **66.9%** |
| GLM 4.6 | 299 | 0 | 0.0% |
| GPT-5-mini | 115 | 0 | 0.0% |
| Qwen 3 235B | 44 | 14 | 31.8% |
| Claude Sonnet 4.6 | 20 | 5 | 25.0% |
| Gemini 2.5 Pro | 9 | 0 | 0.0% |
| ByteDance Seed 1.6 | 3 | 0 | 0.0% |

**Kimi K2's real accuracy jumped from 20.4% to 59.5%** with the corrected
parser. The v0.1 "Kimi confound" story (a low-competence agent artificially
lowering ρ) was largely a parser bug, not a Kimi capability gap. Kimi
just prefers the `LETTER)` format more than other models.

Recovery counts: 898 wrong→correct flips, 0 correct→wrong flips (the fix
is monotone strictly for recovery, never for regression).

## Impact on ρ values

| Cell | v0.1 ρ | v0.2 ρ | Δ |
|---|---|---|---|
| Science D1 same-model | 0.488 | 0.586 | +0.098 |
| Science D2 Chinese | 0.320 | 0.408 | +0.088 |
| Science D3 cross-culture | 0.279 | 0.395 | +0.116 |
| Medicine D1 same-model | 0.415 | 0.659 | +0.244 |
| Medicine D2 Chinese | 0.276 | 0.413 | +0.137 |
| Medicine D3 cross-culture | 0.320 | 0.473 | +0.153 |
| Law D1 same-model | 0.557 | 0.638 | +0.081 |
| Law D2 Chinese | 0.302 | 0.498 | +0.196 |
| Law D3 cross-culture | 0.427 | 0.660 | +0.233 |

**ρ rose in every cell.** The buggy parser artificially deflated ρ by
converting Kimi's chosen-option-format answers into apparent errors, and
those apparent errors were uncorrelated with the other agents' real
errors — mechanically lowering measured ρ.

The corrected numbers give a **stronger version** of the paper's central
claim: multi-agent LLM committees are even less independent than the
buggy scoring suggested.

## Every direction of every paper finding is preserved

1. **D1 collapse:** N_eff went from 1.55-1.88 to 1.37-1.49 — still ≈ 1
   effective agent.
2. **Cross-family diversity effect:** D1 → D2/D3 still drops ρ substantially.
3. **Cross-culture NOT a real diversifier:** D2 vs D3 still shows D2 winning
   in medicine and law (novel result preserved).
4. **Overconfidence gap:** still large at k=2 (14-21 points) and non-zero
   even at k=5 (6-12 points).

The story is the same; the numbers are cleaner.

## Reproducing this correction from scratch

```python
from rho_collapse.scorer import Scorer
from rho_collapse.loader import Loader
import json, shutil
from pathlib import Path

RUN = Path("runs/rho-v1")
if not (RUN / "responses.v1-scoring.jsonl.bak").exists():
    shutil.copy(RUN / "responses.jsonl", RUN / "responses.v1-scoring.jsonl.bak")

items = {it.id: it for it in Loader("data/combined.jsonl").load()}
scorer = Scorer()
rows = []
with (RUN / "responses.v1-scoring.jsonl.bak").open() as f:
    for line in f:
        r = json.loads(line)
        item = items.get(r["item_id"])
        if item and r.get("raw_response") is not None:
            new = scorer.score(item, r["raw_response"])
            r["parsed_answer"] = new["parsed_answer"]
            r["error"] = new["error"]
        rows.append(r)
with (RUN / "responses.jsonl").open("w") as f:
    for r in rows:
        f.write(json.dumps(r) + "\n")
# Then: rho-collapse report --run runs/rho-v1
```
