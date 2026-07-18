"""Build the combined 750-item ρ-measurement dataset — v0.3 (uniform C).

All three domains now sourced from MMLU-Pro (CC-BY-4.0). Uniform C ≈ 10
removes the "why is medicine's ρ smaller?" confound and gives us apples-to-
apples cross-domain ρ comparisons.

Sources (all public / permissive):
  * MMLU-Pro STEM   (biology / physics / chemistry) — 250 items  (science)
  * MMLU-Pro Health (anatomy / physiology / pharmacology / general medical)
                                                    — 250 items  (medicine)
  * MMLU-Pro Law    (bar-exam-style)                — 250 items  (law)

Why the swap from MedQA to MMLU-Pro Health (v0.2 → v0.3)
--------------------------------------------------------
MedQA is 4-way MC; MMLU-Pro is 10-way. Mixing the two made cross-domain
ρ comparisons confounded — reviewers can't tell whether "medicine ρ is
smaller" reflects genuine independence in medical reasoning or the
narrower answer space. Uniform C fixes this.

We lose the "USMLE clinical vignette" flavor. Reviewers who care can be
pointed at v0.3+ where MedQA can return as a sensitivity check.

Output: data/combined.jsonl (one row per item, unified schema)

Unified schema (all rows MCQ):
  {
    "id":            "<domain>-<idx>",
    "domain":        "science" | "medicine" | "law",
    "source":        "MMLU-Pro-STEM" | "MMLU-Pro-Health" | "MMLU-Pro-Law",
    "prompt":        "<question + labelled options + 'Answer with just the letter.'>",
    "answer_type":   "multiple_choice",
    "choices":       [<str>, ...],
    "gold":          "A".."J",
    "license":       "CC-BY-4.0",
    "citation":      "Wang et al., MMLU-Pro, NeurIPS 2024"
  }
"""
from __future__ import annotations

import json
import random
from pathlib import Path

from datasets import load_dataset

OUT = Path(__file__).with_name("combined.jsonl")
random.seed(42)

TARGET_PER_DOMAIN = 250
TARGET_TOTAL = 3 * TARGET_PER_DOMAIN

CITATION = "Wang et al., MMLU-Pro, NeurIPS 2024"


def _mmlu_pro_slice(
    categories: set[str],
    n: int,
    id_prefix: str,
    domain: str,
    source_tag: str,
) -> list[dict]:
    """Sample n items from MMLU-Pro categories."""
    ds = load_dataset("TIGER-Lab/MMLU-Pro", split="test")
    pool = [r for r in ds if r["category"].lower() in categories]
    random.shuffle(pool)
    pool = pool[:n]

    out = []
    for r in pool:
        choices = r["options"]
        letters = [chr(ord("A") + i) for i in range(len(choices))]
        prompt = (
            f"{r['question']}\n\n"
            + "\n".join(f"{ltr}) {c}" for ltr, c in zip(letters, choices))
            + "\n\nAnswer with just the letter."
        )
        out.append({
            "id": f"{id_prefix}-{r['question_id']:06d}",
            "domain": domain,
            "source": source_tag,
            "prompt": prompt,
            "answer_type": "multiple_choice",
            "choices": choices,
            "gold": letters[r["answer_index"]],
            "license": "CC-BY-4.0",
            "citation": CITATION,
        })
    return out


def take_science(n: int) -> list[dict]:
    return _mmlu_pro_slice(
        categories={"biology", "physics", "chemistry"},
        n=n,
        id_prefix="science",
        domain="science",
        source_tag="MMLU-Pro-STEM",
    )


def take_medicine(n: int) -> list[dict]:
    return _mmlu_pro_slice(
        categories={"health"},
        n=n,
        id_prefix="medicine",
        domain="medicine",
        source_tag="MMLU-Pro-Health",
    )


def take_law(n: int) -> list[dict]:
    return _mmlu_pro_slice(
        categories={"law"},
        n=n,
        id_prefix="law",
        domain="law",
        source_tag="MMLU-Pro-Law",
    )


def main() -> None:
    print("→ Science (MMLU-Pro STEM)")
    sci = take_science(TARGET_PER_DOMAIN)
    print(f"   {len(sci)} items")

    print("→ Medicine (MMLU-Pro Health)")
    med = take_medicine(TARGET_PER_DOMAIN)
    print(f"   {len(med)} items")

    print("→ Law (MMLU-Pro Law)")
    law = take_law(TARGET_PER_DOMAIN)
    print(f"   {len(law)} items")

    items = sci + med + law
    assert len(items) == TARGET_TOTAL, f"got {len(items)}, expected {TARGET_TOTAL}"

    with OUT.open("w") as f:
        for it in items:
            f.write(json.dumps(it, ensure_ascii=False) + "\n")

    size_kb = OUT.stat().st_size / 1024
    print(f"\nWrote {OUT} ({size_kb:.1f} KB, {len(items)} items)")
    by_domain: dict[str, int] = {}
    for it in items:
        by_domain[it["domain"]] = by_domain.get(it["domain"], 0) + 1
    print(f"By domain: {by_domain}")


if __name__ == "__main__":
    main()
