# Combined ρ-collapse Dataset (v0.3 — uniform C via MMLU-Pro)

**750 items** to measure inter-agent error correlation (ρ) across three
domains where multi-agent LLM committees are actually deployed in production.

| Domain | Source | Items | Answer type | License | Committees in the wild |
|---|---|---|---|---|---|
| Science | MMLU-Pro STEM (biology, physics, chemistry) | 250 | ~10-way MCQ | CC-BY-4.0 | Elicit, Consensus, Scite |
| Medicine | MMLU-Pro Health (anatomy, physiology, pharmacology) | 250 | ~10-way MCQ | CC-BY-4.0 | UpToDate-style tools, MedPaLM evals, Ada |
| Law | MMLU-Pro Law (bar-exam-style) | 250 | ~10-way MCQ | CC-BY-4.0 | Harvey, Ironclad, ContractPod |
| **Total** | | **750** | | **CC-BY-4.0** | |

## Why uniform C now (v0.2 → v0.3)

v0.2 used MedQA (4-way) alongside two MMLU-Pro slices (10-way). Mixing
answer-space sizes made cross-domain ρ comparisons confounded: reviewers
couldn't tell whether "medicine's ρ is smaller" reflected genuine
independence in medical reasoning or the narrower answer space (the
Bayesian Condorcet posterior is C-sensitive).

v0.3 sources all three domains from MMLU-Pro. Modal C = 10 across every
domain (74–94%, small tails down to C=4). Cross-domain ρ is now
apples-to-apples.

**Tradeoff.** We lose the "USMLE clinical vignette" flavor of MedQA.
MMLU-Pro Health is biomedical knowledge (anatomy, pharmacology,
physiology) more than clinical decision-making. Reviewers who care about
canonical clinical benchmarks can be pointed at a follow-up sensitivity
check with MedQA in v0.4.

## Choice-count distribution per domain

| Domain | Modal C | Distribution |
|---|---|---|
| Science | 10 (94%) | 4:5, 6:2, 7:1, 8:2, 9:5, 10:235 |
| Medicine | 10 (74%) | 4:28, 5:5, 6:3, 7:7, 8:9, 9:14, 10:184 |
| Law | 10 (64%) | 4:11, 5:2, 6:1, 7:6, 8:12, 9:59, 10:159 |

The Bayesian Condorcet posterior is computed **per-item using that item's
actual C**, so mixed C within a domain doesn't confound the math.

## Schema

Each JSONL line:

```json
{
  "id":          "science-003653" | "medicine-000123" | "law-006201",
  "domain":      "science" | "medicine" | "law",
  "source":      "MMLU-Pro-STEM" | "MMLU-Pro-Health" | "MMLU-Pro-Law",
  "prompt":      "<question + labelled options + 'Answer with just the letter.'>",
  "answer_type": "multiple_choice",
  "choices":     ["...", "...", ...],
  "gold":        "A" | "B" | ... | "J",
  "license":     "CC-BY-4.0",
  "citation":    "Wang et al., MMLU-Pro, NeurIPS 2024"
}
```

## Analysis discipline

- **Primary analysis:** compute ρ **per-domain**. The whole point is that ρ
  varies by domain, and pooling destroys that signal.
- **Secondary analysis:** pooled ρ across all 750. Useful practitioner
  rule-of-thumb.
- Never collapse the domain axis in the headline result.

## Reproduce

```bash
python3 data/build_combined_dataset.py
# writes data/combined.jsonl (seeded random.seed(42))
```

Checksum: `data/combined.jsonl.md5` — verify with `md5 data/combined.jsonl`.

## Attribution

- Wang et al., *MMLU-Pro: A More Robust and Challenging Multi-Task Language
  Understanding Benchmark*, NeurIPS 2024
