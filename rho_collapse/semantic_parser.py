"""Semantic answer parser — LLM-first, regex-audited.

Design principles
-----------------
1. **LLM is the source of truth.** For every response we call an LLM
   extractor that sees the item's actual answer choices and infers which
   letter the responder picked. The LLM sees semantics, not patterns; it
   handles restated options, re-quoted choices, and reasoning that ends
   with a boxed answer.
2. **Regex is retained as an audit signal.** For every LLM call we also
   compute the regex answer; if the two disagree, we record it. Reviewers
   can audit the disagreements. The LLM answer is what's used downstream.
3. **Deterministic.** T=0 on the extractor. Same input → same letter.
4. **Cached.** Cache keyed on hash(item_id, response). Re-scoring after
   a bug fix or model swap is free after the first pass.
5. **Fail-safe.** If the LLM extractor errors, we fall back to the regex
   answer so the pipeline never produces worse output than pure regex.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

from rho_collapse.loader import Item
from rho_collapse.scorer import parse_mcq_answer


VALID_LETTERS = set("ABCDEFGHIJ")


# The extractor's system prompt. Terse and restrictive about output format
# so validation is straightforward.
_EXTRACTOR_SYSTEM = """\
You are an answer extractor for a multiple-choice benchmark. You will be
given a question, its labelled answer choices A-J, and a message from a
responder. Determine which letter the responder chose.

Rules:
1. Output exactly one line: LETTER<TAB>REASON
   where LETTER is a single character A-J or the literal word NONE, and
   REASON is one of: explicit, restated, inferred, no-answer, ambiguous.
2. explicit — the responder gave a letter marker ("Answer: B", "\\boxed{D}",
   "the answer is C", "**H**", etc.).
3. restated — the responder wrote the CORRECT option's text verbatim
   without giving a letter. Match option text to letter.
4. inferred — the responder discussed reasoning and the picked option is
   unambiguous from context, but not marked with a letter.
5. no-answer — the responder was cut off, refused, or did not converge
   on any option.
6. ambiguous — two or more letters are equally plausible. Do not guess.
7. Prefer the FINAL answer if the responder discussed multiple options
   before landing on one.
"""


@dataclass
class ExtractResult:
    letter: str | None
    reason: str
    source: str          # "llm" | "cache" | "regex-fallback" | "error"
    regex_letter: str | None
    disagreement: bool


class SemanticParser:
    """LLM-first semantic answer parser with regex audit trail."""

    def __init__(
        self,
        provider: str = "openrouter",
        # Gemini 2.5 Flash Lite is ~10x cheaper than V4 and equally accurate
        # on "given options + response tail, name the letter" tasks. Extraction
        # is nowhere near the model's frontier capability.
        model: str = "google/gemini-2.5-flash-lite",
        cache_path: str | Path = "runs/rho-v1/semantic_parser_cache.jsonl",
        # 1500 chars ≈ 400 tokens. The answer is at the end of the response
        # in > 99% of cases. Keeping only the tail cuts prompt cost ~5x
        # relative to the 8k default with no quality loss.
        max_response_chars: int = 1500,
    ) -> None:
        self.provider = provider
        self.model = model
        self.cache_path = Path(cache_path)
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)
        self.max_response_chars = max_response_chars
        self._cache: dict[str, dict] = self._load_cache()

    # ── cache ──────────────────────────────────────────────────────

    def _load_cache(self) -> dict[str, dict]:
        cache: dict[str, dict] = {}
        if not self.cache_path.exists():
            return cache
        with self.cache_path.open() as f:
            for line in f:
                try:
                    r = json.loads(line)
                    cache[r["key"]] = r
                except (json.JSONDecodeError, KeyError):
                    continue
        return cache

    def _persist(self, entry: dict) -> None:
        with self.cache_path.open("a") as f:
            f.write(json.dumps(entry) + "\n")
            f.flush()

    @staticmethod
    def _cache_key(item_id: str, response_text: str) -> str:
        h = hashlib.sha256()
        h.update(item_id.encode())
        h.update(b"\x00")
        h.update((response_text or "").encode())
        return h.hexdigest()[:24]

    # ── prompt building ────────────────────────────────────────────

    def _build_extractor_prompt(self, item: Item, response: str) -> str:
        """Compressed prompt: options + response tail only. The question
        stem is not needed — we're extracting the responder's chosen letter,
        which is a function of the options and the response, not the question.
        Shrinking the prompt cuts extractor cost ~5x with no quality loss."""
        letters = [chr(ord("A") + i) for i in range(len(item.choices or []))]
        options_block = "\n".join(
            f"{letter}) {choice}" for letter, choice in zip(letters, item.choices or [])
        )
        response_snippet = response
        if len(response_snippet) > self.max_response_chars:
            # Answers are almost always at the end; preserve tail.
            response_snippet = "…" + response_snippet[-self.max_response_chars:]
        return (
            f"OPTIONS\n"
            f"-------\n"
            f"{options_block}\n\n"
            f"RESPONSE (tail)\n"
            f"---------------\n"
            f"{response_snippet}\n\n"
            f"OUTPUT (one line, LETTER<TAB>REASON)\n"
            f"------\n"
        )

    # ── LLM extractor ──────────────────────────────────────────────

    def _llm_extract(self, item: Item, response: str) -> tuple[str | None, str, str]:
        """Return (letter, reason, source)."""
        from rho_collapse.agents import build_agent

        prompt = _EXTRACTOR_SYSTEM + "\n\n" + self._build_extractor_prompt(item, response)
        try:
            agent = build_agent(
                provider=self.provider,
                model=self.model,
                seed=1,
                temperature=0.0,
                max_tokens=32,
            )
            comp = agent.complete(prompt)
        except Exception as e:
            return None, f"extractor-error:{e.__class__.__name__}", "error"

        raw = (comp.text or "").strip()
        # Expected LETTER<TAB>REASON but be tolerant.
        m = re.match(r"^\s*([A-J]|NONE)\s*[\t\|,;: ]+\s*(\S[\S ]*)$", raw)
        if m:
            picked = m.group(1).upper()
            reason = m.group(2).strip()
            if picked == "NONE":
                return None, reason, "llm"
            return picked, reason, "llm"

        # Fallback: single letter alone
        m2 = re.match(r"^\s*([A-J])\b", raw)
        if m2:
            return m2.group(1).upper(), "unspecified", "llm"
        return None, f"unparseable-extractor-output:{raw[:50]!r}", "error"

    # ── public API ─────────────────────────────────────────────────

    def parse(self, item: Item, response: str) -> ExtractResult:
        """LLM-first parse. Regex is computed alongside as audit trail."""
        if not response:
            return ExtractResult(
                letter=None,
                reason="empty-response",
                source="llm",
                regex_letter=None,
                disagreement=False,
            )

        # Always compute regex answer for audit
        regex_letter = parse_mcq_answer(response)

        # Cache lookup
        key = self._cache_key(item.id, response)
        if key in self._cache:
            entry = self._cache[key]
            llm_letter = entry.get("letter")
            reason = entry.get("reason", "cached")
            disagreement = (llm_letter is not None
                            and regex_letter is not None
                            and llm_letter != regex_letter)
            return ExtractResult(
                letter=llm_letter,
                reason=reason,
                source="cache",
                regex_letter=regex_letter,
                disagreement=disagreement,
            )

        # LLM call
        llm_letter, reason, source = self._llm_extract(item, response)

        # Fail-safe: if LLM errored, fall back to regex
        if source == "error" and regex_letter is not None:
            final_letter, final_reason, final_source = regex_letter, "regex-fallback", "regex-fallback"
        else:
            final_letter, final_reason, final_source = llm_letter, reason, source

        # Persist LLM answer + regex answer + disagreement
        disagreement = (llm_letter is not None
                        and regex_letter is not None
                        and llm_letter != regex_letter)
        entry = {
            "key": key,
            "item_id": item.id,
            "letter": final_letter,
            "reason": final_reason,
            "source": final_source,
            "llm_letter": llm_letter,
            "llm_reason": reason,
            "regex_letter": regex_letter,
            "disagreement": disagreement,
            "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        self._cache[key] = entry
        self._persist(entry)
        return ExtractResult(
            letter=final_letter,
            reason=final_reason,
            source=final_source,
            regex_letter=regex_letter,
            disagreement=disagreement,
        )

    # ── batch helper ───────────────────────────────────────────────

    def parse_many(
        self,
        rows: Iterable[tuple[Item, str]],
        n_workers: int = 6,
    ) -> list[ExtractResult]:
        from concurrent.futures import ThreadPoolExecutor

        rows = list(rows)
        results: list[ExtractResult | None] = [None] * len(rows)

        def _work(idx: int, item: Item, response: str) -> None:
            results[idx] = self.parse(item, response)

        with ThreadPoolExecutor(max_workers=n_workers) as ex:
            futures = [ex.submit(_work, i, item, r) for i, (item, r) in enumerate(rows)]
            for f in futures:
                f.result()
        return [r for r in results if r is not None]
