"""Deterministic scoring: MCQ letter parsing and code test execution.

Both return a binary error indicator (0 = correct, 1 = wrong) so downstream
correlation math treats every domain uniformly.
"""
from __future__ import annotations

import re
import subprocess
import sys
import tempfile
from pathlib import Path

from rho_collapse.loader import Item


# ── MCQ ─────────────────────────────────────────────────────────────────────

# Matches the intended answer letter. We're strict about lone A/I because
# they appear as English words ("A", "I'll", "I don't"). We refuse to fire
# a fallback on unadorned letters — if the model didn't follow instructions,
# we prefer to record "unparseable" (which counts as an error).
_ANSWER_PATTERNS = [
    # "The final answer is B", "answer: B", "correct answer B"
    r"(?:final\s+answer|correct\s+answer|answer)\s*(?:is|=|:)?\s*[\*\(\[]?\s*([A-J])\b",
    # "\boxed{B}"
    r"\\boxed\{\s*([A-J])\s*\}",
    # "go with B", "choose B", "pick B", "select B", "option B"
    r"(?:go\s+with|choose|pick|select|option)\s+[\*\(\[]?\s*([A-J])\b",
    # Bold or bracketed lone letter
    r"\*\*\s*([A-J])\s*\*\*",
    r"\(([A-J])\)",
    r"\[([A-J])\]",
]

_ISOLATED_LETTER = re.compile(r"^\s*([A-J])\s*$", flags=re.MULTILINE)

# "B) description" — very common LLM output where the response IS the answer
# in labelled-option form. We match only when the final non-empty line
# contains EXACTLY ONE `LETTER)` pattern; if it contains multiple, the line
# is an ambiguous listing (e.g. "Options: A) foo B) bar C) baz") rather
# than an answer, and we refuse to guess.
_LETTER_PAREN = re.compile(r"([A-J])\)\s+\S")


def _final_nonempty_line(text: str) -> str | None:
    for line in reversed(text.split("\n")):
        line = line.strip()
        if line:
            return line
    return None


def parse_mcq_answer(text: str) -> str | None:
    """Return the parsed letter (A-J) or None if not recoverable.

    Order of preference:
      1. Explicit answer markers ("answer is B", "\\boxed{B}", "go with B", etc.).
      2. A letter alone on any line (e.g., a lone "B").
      3. A single-character response.
      4. "B) description" — accept only if the final non-empty line has
         exactly one `LETTER)` pattern (otherwise it is an ambiguous
         listing of options, not an answer).
    """
    text = (text or "").strip()
    if not text:
        return None
    for pat in _ANSWER_PATTERNS:
        m = re.search(pat, text, flags=re.IGNORECASE)
        if m:
            return m.group(1).upper()
    m = _ISOLATED_LETTER.search(text)
    if m:
        return m.group(1).upper()
    if len(text) == 1 and text in "ABCDEFGHIJ":
        return text
    final = _final_nonempty_line(text)
    if final:
        matches = _LETTER_PAREN.findall(final)
        if len(matches) == 1:
            return matches[0].upper()
    return None


# ── Code ────────────────────────────────────────────────────────────────────

_CODE_HEADER = """
import sys, io
sys.stdout = io.StringIO()
sys.stderr = io.StringIO()
"""


def _extract_python_code(response: str) -> str:
    """Strip Markdown fences and inline commentary; keep just the code."""
    fence = re.search(r"```(?:python)?\n(.*?)```", response, flags=re.DOTALL)
    if fence:
        return fence.group(1)
    return response


def _run_python(program: str, timeout_s: float = 10.0) -> tuple[bool, str]:
    """Run `program` in a subprocess with a timeout. Return (passed, stderr)."""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False, encoding="utf-8"
    ) as f:
        f.write(program)
        path = f.name
    try:
        proc = subprocess.run(
            [sys.executable, path],
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
        return proc.returncode == 0, proc.stderr[-2000:]
    except subprocess.TimeoutExpired:
        return False, "TIMEOUT"
    finally:
        Path(path).unlink(missing_ok=True)


def check_code(response: str, gold: dict, timeout_s: float = 10.0) -> bool:
    """Assemble code + tests, run, return True if all tests pass."""
    code = _extract_python_code(response)
    tests = gold.get("tests", "")
    entry_point = gold.get("entry_point", "")
    program = _CODE_HEADER + code + "\n\n" + tests
    # HumanEval+ tests usually end with `check(<entry_point>)`; add if missing.
    if entry_point and f"check({entry_point}" not in program and "check(" in program:
        program += f"\ncheck({entry_point})\n"
    passed, _ = _run_python(program, timeout_s=timeout_s)
    return passed


# ── Unified scorer ──────────────────────────────────────────────────────────

class Scorer:
    """Domain-agnostic scoring facade.

    `score(item, response)` returns a dict:
        {"error": 0 | 1, "parsed_answer": str | None}
    """

    def score(self, item: Item, response: str) -> dict:
        if item.answer_type == "multiple_choice":
            parsed = parse_mcq_answer(response or "")
            error = 0 if parsed == item.gold else 1
            return {"error": error, "parsed_answer": parsed}
        if item.answer_type == "code":
            gold = item.gold if isinstance(item.gold, dict) else {}
            passed = check_code(response or "", gold)
            return {"error": 0 if passed else 1, "parsed_answer": None}
        raise ValueError(f"unknown answer_type: {item.answer_type}")
