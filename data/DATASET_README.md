# Combined ρ-collapse Dataset (v0.2 — all MCQ)

**750 items** to measure inter-agent error correlation (ρ) across three
domains where multi-agent LLM committees are actually deployed in production.

| Domain | Source | Items | Answer type | License | Committees in the wild |
|---|---|---|---|---|---|
| Science | MMLU-Pro STEM (biology, physics, chemistry) | 250 | 10-way MCQ | CC-BY-4.0 | Elicit, Consensus, Scite |
| Medicine | MedQA-USMLE-4-options | 250 | 4-way MCQ | MIT | Ada, Glass Health, K Health |
| Law | MMLU-Pro Law (bar-exam-style) | 250 | 10-way MCQ | CC-BY-4.0 | Harvey, Ironclad, ContractPod |
| **Total** | | **750** | | **CC-BY-4.0 (derivative)** | |

## Why all MCQ now (v0.1 → v0.2)

v0.1 shipped 250 code items (HumanEval+ / MBPP+). Code answers created a
problem: two agents can write syntactically different but semantically
equivalent code, so "5 agents agree" has no clean definition without
behavioural-equivalence instrumentation. That's a whole subproject.

v0.2 replaces code with **MMLU-Pro Law**. Consensus is now trivially defined
across all 750 items (same letter) and the k-of-N overconfidence gap is
symmetric across domains. Behavioural-consensus code items may return in
v0.3 as a supplementary study.

## Schema

Each JSONL line:

```json
{
  "id":          "science-003653" | "medicine-000045" | "law-006201",
  "domain":      "science" | "medicine" | "law",
  "source":      "MMLU-Pro" | "MedQA",
  "prompt":      "<question + labelled options + 'Answer with just the letter.'>",
  "answer_type": "multiple_choice",
  "choices":     ["...", "...", ...],
  "gold":        "A" | "B" | ... | "J",
  "license":     "CC-BY-4.0" | "MIT",
  "citation":    "<how to cite>"
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

## Attribution

- Wang et al., *MMLU-Pro: A More Robust and Challenging Multi-Task Language
  Understanding Benchmark*, NeurIPS 2024
- Jin et al., *MedQA: A Large-scale Open Domain Question Answering Dataset
  from Medical Exams*, 2020
