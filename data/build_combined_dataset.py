"""Build the combined 750-item ρ-measurement dataset — v0.2 (all MCQ).

Sources (all public / permissive):
  * MMLU-Pro STEM (CC-BY-4.0)     — 250 items (biology / physics / chemistry).
                                    Substitutes for GPQA-Diamond (gated).
  * MedQA-USMLE-4-options (MIT)   — 250 items.
  * MMLU-Pro Law (CC-BY-4.0)      — 250 items (bar-exam-style reasoning).
                                    Replaces the v0.1 code split (HumanEval+ / MBPP+)
                                    because "consensus" is trivially defined for MCQ
                                    (same letter) but not for code (behavioural
                                    equivalence needs its own instrumentation).

Output: data/combined.jsonl (one row per item, unified schema)

Unified schema (all rows now MCQ):
  {
    "id":            "<domain>-<idx>",
    "domain":        "science" | "medicine" | "law",
    "source":        "MMLU-Pro-STEM" | "MedQA" | "MMLU-Pro-Law",
    "prompt":        "<question + labelled options + 'Answer with just the letter.'>",
    "answer_type":   "multiple_choice",
    "choices":       [<str>, ...],
    "gold":          "A".."J",
    "license":       "CC-BY-4.0" | "MIT",
    "citation":      "<how to cite>"
  }
"""
from __future__ import annotations

import json
import random
from pathlib import Path

from datasets import load_dataset

OUT = Path(__file__).with_name("combined.jsonl")
random.seed(42)  # reproducible sampling

TARGET_PER_DOMAIN = 250
TARGET_TOTAL = 3 * TARGET_PER_DOMAIN


# ── helpers ─────────────────────────────────────────────────────────────────

def _mmlu_pro_slice(categories: set[str], n: int, id_prefix: str,
                    domain: str, citation: str) -> list[dict]:
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
            "source": f"MMLU-Pro-{id_prefix.split('-')[-1].upper()}"
            if "-" in id_prefix else "MMLU-Pro",
            "prompt": prompt,
            "answer_type": "multiple_choice",
            "choices": choices,
            "gold": letters[r["answer_index"]],
            "license": "CC-BY-4.0",
            "citation": citation,
        })
    return out


def take_science(n: int) -> list[dict]:
    return _mmlu_pro_slice(
        categories={"biology", "physics", "chemistry"},
        n=n,
        id_prefix="science",
        domain="science",
        citation="Wang et al., MMLU-Pro, NeurIPS 2024 (STEM slice)",
    )


def take_law(n: int) -> list[dict]:
    return _mmlu_pro_slice(
        categories={"law"},
        n=n,
        id_prefix="law",
        domain="law",
        citation="Wang et al., MMLU-Pro, NeurIPS 2024 (law slice)",
    )


def take_medicine(n: int) -> list[dict]:
    ds = load_dataset("GBaker/MedQA-USMLE-4-options", split="test")
    rows = list(ds)
    random.shuffle(rows)
    rows = rows[:n]

    out = []
    for i, r in enumerate(rows):
        opts = r["options"]  # dict {A: "...", B: "...", ...}
        letters = sorted(opts.keys())
        choices = [opts[l] for l in letters]
        prompt = (
            f"{r['question']}\n\n"
            + "\n".join(f"{l}) {opts[l]}" for l in letters)
            + "\n\nAnswer with just the letter."
        )
        gold_letter = r.get("answer_idx") or _resolve_letter(opts, r["answer"])
        out.append({
            "id": f"medicine-{i:06d}",
            "domain": "medicine",
            "source": "MedQA",
            "prompt": prompt,
            "answer_type": "multiple_choice",
            "choices": choices,
            "gold": gold_letter,
            "license": "MIT",
            "citation": "Jin et al., MedQA, 2020",
        })
    return out


def _resolve_letter(opts: dict, answer_text: str) -> str:
    for k, v in opts.items():
        if v.strip() == (answer_text or "").strip():
            return k
    return "A"


# ── main ────────────────────────────────────────────────────────────────────

def main() -> None:
    print("→ Science (MMLU-Pro STEM)")
    sci = take_science(TARGET_PER_DOMAIN)
    print(f"   {len(sci)} items")

    print("→ Medicine (MedQA)")
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
