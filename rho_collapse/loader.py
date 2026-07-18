"""Load items from the combined 750-item JSONL under a unified schema.

Every line is one item; see data/DATASET_README.md for the schema.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterator


@dataclass(frozen=True)
class Item:
    id: str
    domain: str              # "science" | "medicine" | "code"
    source: str              # "MMLU-Pro-STEM" | "MedQA" | "HumanEval+" | "MBPP+"
    prompt: str
    answer_type: str         # "multiple_choice" | "code"
    choices: list | None
    gold: str | dict         # letter for MCQ, dict with tests/entry_point for code
    license: str
    citation: str


class Loader:
    """Streaming reader for `combined.jsonl`."""

    def __init__(self, path: str | Path = "data/combined.jsonl") -> None:
        self.path = Path(path)
        if not self.path.exists():
            raise FileNotFoundError(f"dataset not found: {self.path}")

    def load(self, domain: str | None = None, limit: int | None = None) -> Iterator[Item]:
        """Yield `Item`s. Optionally filter by domain, cap by limit."""
        n = 0
        with self.path.open() as f:
            for line in f:
                row = json.loads(line)
                if domain and row["domain"] != domain:
                    continue
                yield Item(**row)
                n += 1
                if limit and n >= limit:
                    return

    def counts_by_domain(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        for item in self.load():
            counts[item.domain] = counts.get(item.domain, 0) + 1
        return counts
