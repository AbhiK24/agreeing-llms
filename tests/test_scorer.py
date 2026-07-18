"""Scorer must correctly parse letters and execute code.

These tests exercise the exact code paths the runner will hit — MCQ letter
parsing across varied response styles, and subprocess-based code execution
for HumanEval+ / MBPP+ tasks (both passing and failing).
"""
from __future__ import annotations

import pytest

from rho_collapse.loader import Item
from rho_collapse.scorer import Scorer, parse_mcq_answer


# ── MCQ parsing ────────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "text, expected",
    [
        ("The answer is B.", "B"),
        ("Final answer: (C)", "C"),
        ("**D**", "D"),
        ("\\boxed{A}", "A"),
        ("I'll go with A because ...", "A"),
        ("After reasoning, the correct answer is E.", "E"),
        # Real Sonnet-style meandering answer
        ("Looking at this carefully:\nOption A doesn't fit.\nOption B is closer.\nAnswer: B",
         "B"),
        # Lone letter at the start
        ("D\n\nExplanation follows.", "D"),
    ],
)
def test_parse_mcq_extracts_letter(text: str, expected: str) -> None:
    assert parse_mcq_answer(text) == expected


def test_parse_mcq_returns_none_when_absent() -> None:
    assert parse_mcq_answer("I don't know.") is None


# ── Scorer facade — MCQ ────────────────────────────────────────────────────

def _mcq_item(gold: str) -> Item:
    return Item(
        id="test-1",
        domain="medicine",
        source="MedQA",
        prompt="q?",
        answer_type="multiple_choice",
        choices=["a", "b", "c", "d"],
        gold=gold,
        license="MIT",
        citation="test",
    )


def test_scorer_mcq_correct() -> None:
    out = Scorer().score(_mcq_item("B"), "Answer: B")
    assert out == {"error": 0, "parsed_answer": "B"}


def test_scorer_mcq_wrong() -> None:
    out = Scorer().score(_mcq_item("B"), "Answer: C")
    assert out == {"error": 1, "parsed_answer": "C"}


def test_scorer_mcq_unparseable_is_error() -> None:
    out = Scorer().score(_mcq_item("B"), "hmm")
    assert out["error"] == 1
    assert out["parsed_answer"] is None


# ── Scorer facade — code ────────────────────────────────────────────────────

def _code_item(tests: str, entry_point: str) -> Item:
    return Item(
        id="test-code-1",
        domain="code",
        source="HumanEval+",
        prompt="write add(a,b)",
        answer_type="code",
        choices=None,
        gold={"tests": tests, "entry_point": entry_point, "canonical_solution": ""},
        license="MIT",
        citation="test",
    )


PASSING_CODE = """
def add(a, b):
    return a + b
"""

FAILING_CODE = """
def add(a, b):
    return a - b
"""

HANGING_CODE = """
def add(a, b):
    while True:
        pass
"""

TESTS = """
def check(add):
    assert add(1, 2) == 3
    assert add(-1, 1) == 0
check(add)
"""


def test_scorer_code_pass() -> None:
    item = _code_item(TESTS, "add")
    out = Scorer().score(item, "```python\n" + PASSING_CODE + "\n```")
    assert out["error"] == 0


def test_scorer_code_fail() -> None:
    item = _code_item(TESTS, "add")
    out = Scorer().score(item, FAILING_CODE)
    assert out["error"] == 1


def test_scorer_code_hang_is_error() -> None:
    """Timeout must not raise; it must record an error."""
    item = _code_item(TESTS, "add")
    # override the default long timeout for a quick failure
    from rho_collapse.scorer import check_code
    assert check_code(HANGING_CODE, item.gold, timeout_s=1.0) is False
