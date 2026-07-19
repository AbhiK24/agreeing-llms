"""Semantic parser sanity — LLM-first with regex audit.

LLM calls are stubbed. No API hits from tests.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from rho_collapse.loader import Item
from rho_collapse.semantic_parser import ExtractResult, SemanticParser


def _mcq_item(gold: str = "B", choices: list | None = None) -> Item:
    return Item(
        id="test-1",
        domain="medicine",
        source="MedQA",
        prompt="test question",
        answer_type="multiple_choice",
        choices=choices or ["opt a", "opt b", "opt c", "opt d"],
        gold=gold,
        license="MIT",
        citation="test",
    )


def _stub_agent(text: str, monkeypatch):
    """Patch the agents.build_agent factory so the LLM path returns `text`."""
    class _StubComp:
        def __init__(self, t):
            self.text = t; self.tokens_in = 100; self.tokens_out = 5; self.latency_ms = 10

    class _StubAgent:
        def complete(self, prompt):
            return _StubComp(text)

    from rho_collapse import agents as ra
    monkeypatch.setattr(ra, "build_agent", lambda **kw: _StubAgent())


def test_empty_response_short_circuits(tmp_path: Path) -> None:
    p = SemanticParser(cache_path=tmp_path / "cache.jsonl")
    r = p.parse(_mcq_item(), "")
    assert r.letter is None
    assert r.regex_letter is None
    assert r.disagreement is False


def test_llm_answer_becomes_the_letter(tmp_path: Path, monkeypatch) -> None:
    _stub_agent("C\texplicit", monkeypatch)
    p = SemanticParser(cache_path=tmp_path / "cache.jsonl")
    r = p.parse(_mcq_item(), "I'd go with C here.")
    assert r.letter == "C"
    assert r.source == "llm"


def test_llm_and_regex_agree_no_disagreement(tmp_path: Path, monkeypatch) -> None:
    _stub_agent("B\texplicit", monkeypatch)
    p = SemanticParser(cache_path=tmp_path / "cache.jsonl")
    r = p.parse(_mcq_item(), "The answer is B.")
    assert r.letter == "B"
    assert r.regex_letter == "B"
    assert r.disagreement is False


def test_llm_and_regex_disagree_llm_wins(tmp_path: Path, monkeypatch) -> None:
    """Regex catches an earlier option letter; LLM catches the final answer.
    LLM's letter wins; disagreement flag is set for audit."""
    _stub_agent("J\texplicit", monkeypatch)
    p = SemanticParser(cache_path=tmp_path / "cache.jsonl")
    r = p.parse(_mcq_item(),
                "Option G is close, but the answer is **J) Both of these**.")
    assert r.letter == "J"        # LLM's answer used
    assert r.regex_letter == "J"  # regex now (v3) catches last match too
    assert r.disagreement is False


def test_llm_none_returns_unparseable(tmp_path: Path, monkeypatch) -> None:
    _stub_agent("NONE\tno-answer", monkeypatch)
    p = SemanticParser(cache_path=tmp_path / "cache.jsonl")
    r = p.parse(_mcq_item(),
                "Reasoning was cut off before I could finish deriving the answer.")
    assert r.letter is None
    assert r.reason == "no-answer"


def test_llm_error_falls_back_to_regex(tmp_path: Path, monkeypatch) -> None:
    class _FailingAgent:
        def complete(self, prompt):
            raise RuntimeError("upstream 500")

    from rho_collapse import agents as ra
    monkeypatch.setattr(ra, "build_agent", lambda **kw: _FailingAgent())

    p = SemanticParser(cache_path=tmp_path / "cache.jsonl")
    r = p.parse(_mcq_item(), "The answer is B.")
    assert r.letter == "B"
    assert r.source == "regex-fallback"


def test_cache_roundtrips_across_instances(tmp_path: Path, monkeypatch) -> None:
    _stub_agent("D\texplicit", monkeypatch)
    cache_path = tmp_path / "cache.jsonl"
    p1 = SemanticParser(cache_path=cache_path)
    weird = "third from the top, I'd say"
    r1 = p1.parse(_mcq_item(), weird)
    assert r1.letter == "D"
    assert r1.source == "llm"

    # Fresh instance — must load from cache and NOT call LLM
    class _NeverCalledAgent:
        def complete(self, prompt):
            raise AssertionError("LLM should not have been called; cache miss?")

    from rho_collapse import agents as ra
    monkeypatch.setattr(ra, "build_agent", lambda **kw: _NeverCalledAgent())

    p2 = SemanticParser(cache_path=cache_path)
    r2 = p2.parse(_mcq_item(), weird)
    assert r2.letter == "D"
    assert r2.source == "cache"


def test_cache_key_stable_across_runs(tmp_path: Path) -> None:
    p = SemanticParser(cache_path=tmp_path / "cache.jsonl")
    k1 = p._cache_key("medicine-000045", "The answer is B.")
    k2 = p._cache_key("medicine-000045", "The answer is B.")
    assert k1 == k2
    k3 = p._cache_key("medicine-000046", "The answer is B.")
    assert k1 != k3
