"""Loader must yield well-formed Items and honour the domain filter."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from rho_collapse.loader import Item, Loader


@pytest.fixture
def mini_jsonl(tmp_path: Path) -> Path:
    p = tmp_path / "mini.jsonl"
    p.write_text(
        "\n".join(
            json.dumps({
                "id": f"x-{i}",
                "domain": ("science" if i < 2 else "code"),
                "source": "test",
                "prompt": f"prompt {i}",
                "answer_type": ("multiple_choice" if i < 2 else "code"),
                "choices": ["a", "b"] if i < 2 else None,
                "gold": "A" if i < 2 else {"tests": "assert True", "entry_point": "f"},
                "license": "MIT",
                "citation": "test",
            })
            for i in range(4)
        )
        + "\n"
    )
    return p


def test_loader_yields_items(mini_jsonl: Path) -> None:
    items = list(Loader(mini_jsonl).load())
    assert len(items) == 4
    assert all(isinstance(x, Item) for x in items)


def test_loader_filters_by_domain(mini_jsonl: Path) -> None:
    items = list(Loader(mini_jsonl).load(domain="code"))
    assert len(items) == 2
    assert all(x.domain == "code" for x in items)


def test_loader_respects_limit(mini_jsonl: Path) -> None:
    items = list(Loader(mini_jsonl).load(limit=1))
    assert len(items) == 1


def test_counts_by_domain_matches_real_dataset() -> None:
    """Sanity: the shipped 750-item dataset is balanced across three domains."""
    p = Path(__file__).resolve().parents[1] / "data" / "combined.jsonl"
    if not p.exists():
        pytest.skip("full dataset not shipped in this checkout")
    counts = Loader(p).counts_by_domain()
    assert counts == {"science": 250, "medicine": 250, "law": 250}
