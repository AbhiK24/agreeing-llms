"""Orchestrates: items × committee → raw responses → error matrix.

Two persistent artifacts under `runs/<run_id>/`:

  * responses.jsonl — every completed (item, condition, agent, seed) tuple
    with the raw text and API metadata. **Append-only**, one JSON object per
    line. This is the checkpoint file. Re-running the CLI on the same
    run_id skips every tuple already present.

  * errors.parquet — materialized M × N binary error matrix, rebuilt from
    responses.jsonl at the end of each run.

Two transient artifacts:

  * progress.json — a snapshot of counts (done / pending / failed) updated
    every 20 completions. Human-readable; safe to `tail` from another shell.

  * .lock — a courtesy lock so two concurrent CLIs don't step on each other.

Resumability guarantees
-----------------------
1. Every response is written as **one full line + flush** before the runner
   considers the tuple done. Interruption at any moment loses at most the
   currently in-flight calls (each thread does one at a time).
2. On restart, `_load_done_keys` re-reads responses.jsonl. Any partial /
   malformed line is silently skipped, so the affected tuple is re-run.
3. SIGINT (Ctrl-C) halts new task submission and lets in-flight calls
   finish; the second SIGINT within 3 s force-kills.
"""
from __future__ import annotations

import json
import signal
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import pandas as pd
from tqdm import tqdm

from rho_collapse.agents import Agent, AgentError, build_agent
from rho_collapse.loader import Item
from rho_collapse.rate_limit import ModelLimits, RateLimiter
from rho_collapse.scorer import Scorer


# ── Config schema ───────────────────────────────────────────────────────────

@dataclass
class ModelSpec:
    name: str
    provider: str
    model: str
    family: str
    # Rate-limit knobs. Defaults are conservative for OpenRouter's standard
    # tier; bump them in `configs/experiment.yaml` if you have higher quota.
    max_concurrent: int = 4
    requests_per_second: float = 5.0


@dataclass
class ConditionSpec:
    name: str
    committee: list[str]
    seeds: list[int]


@dataclass
class ExperimentConfig:
    run_id: str
    models: dict[str, ModelSpec] = field(default_factory=dict)
    conditions: list[ConditionSpec] = field(default_factory=list)
    temperature: float = 0.7
    max_tokens: int = 1024
    n_workers: int = 8

    @classmethod
    def from_yaml(cls, path: str | Path) -> "ExperimentConfig":
        import yaml
        raw = yaml.safe_load(Path(path).read_text())
        models = {
            name: ModelSpec(name=name, **spec) for name, spec in raw["models"].items()
        }
        conditions = [
            ConditionSpec(name=name, **spec)
            for name, spec in raw["conditions"].items()
        ]
        return cls(
            run_id=raw["run_id"],
            models=models,
            conditions=conditions,
            temperature=raw.get("temperature", 0.7),
            max_tokens=raw.get("max_tokens", 1024),
            n_workers=raw.get("n_workers", 8),
        )


# ── Runner ──────────────────────────────────────────────────────────────────

class Runner:
    def __init__(self, config: ExperimentConfig, out_dir: str | Path = "runs") -> None:
        self.config = config
        self.out_root = Path(out_dir) / config.run_id
        self.out_root.mkdir(parents=True, exist_ok=True)
        self.responses_path = self.out_root / "responses.jsonl"
        self.errors_path = self.out_root / "errors.parquet"
        self.progress_path = self.out_root / "progress.json"
        self.lock_path = self.out_root / ".lock"
        self._done_keys = self._load_done_keys()
        self._agents_cache: dict[tuple[str, int], Agent] = {}
        self._write_lock = threading.Lock()
        self._stop_event = threading.Event()
        # Per-model rate limiter — enforces both concurrency and requests/sec.
        self._rate_limiter = RateLimiter(
            limits={
                name: ModelLimits(
                    max_concurrent=spec.max_concurrent,
                    requests_per_second=spec.requests_per_second,
                )
                for name, spec in config.models.items()
            }
        )
        self._counters = {
            "done_at_start": len(self._done_keys),
            "completed_this_session": 0,
            "failed_this_session": 0,
            "started_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

    # ── idempotency ────────────────────────────────────────────────
    def _load_done_keys(self) -> set[tuple[str, str, str, int]]:
        """Load already-completed tuples. Malformed lines are silently
        skipped so the affected tuples are re-run."""
        keys: set[tuple[str, str, str, int]] = set()
        if not self.responses_path.exists():
            return keys
        with self.responses_path.open() as f:
            for line in f:
                try:
                    r = json.loads(line)
                    keys.add((r["item_id"], r["condition"], r["agent_name"], r["seed"]))
                except (json.JSONDecodeError, KeyError):
                    continue
        return keys

    def _agent_for(self, agent_name: str, seed: int) -> Agent:
        key = (agent_name, seed)
        if key not in self._agents_cache:
            spec = self.config.models[agent_name]
            self._agents_cache[key] = build_agent(
                provider=spec.provider,
                model=spec.model,
                seed=seed,
                temperature=self.config.temperature,
                max_tokens=self.config.max_tokens,
            )
        return self._agents_cache[key]

    # ── one call ───────────────────────────────────────────────────
    def _one_call(
        self,
        item: Item,
        condition: ConditionSpec,
        agent_name: str,
        seed: int,
        scorer: Scorer,
    ) -> dict:
        if self._stop_event.is_set():
            return {"skipped": True}
        try:
            agent = self._agent_for(agent_name, seed)
            with self._rate_limiter.slot(agent_name):
                comp = agent.complete(item.prompt)
            scored = scorer.score(item, comp.text)
            spec = self.config.models[agent_name]
            return {
                "item_id": item.id,
                "domain": item.domain,
                "condition": condition.name,
                "agent_name": agent_name,
                "family": spec.family,
                "model": spec.model,
                "seed": seed,
                "raw_response": comp.text,
                "parsed_answer": scored["parsed_answer"],
                "error": scored["error"],
                # Needed downstream for Bayesian Condorcet posterior + cluster
                # analysis. 4-way MedQA vs 10-way MMLU-Pro produce different
                # posteriors under agreement.
                "num_choices": len(item.choices) if item.choices else 0,
                "gold": item.gold if isinstance(item.gold, str) else None,
                "tokens_in": comp.tokens_in,
                "tokens_out": comp.tokens_out,
                "latency_ms": comp.latency_ms,
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "err": None,
            }
        except AgentError as e:
            return {
                "item_id": item.id,
                "domain": item.domain,
                "condition": condition.name,
                "agent_name": agent_name,
                "family": self.config.models[agent_name].family,
                "model": self.config.models[agent_name].model,
                "seed": seed,
                "raw_response": None,
                "parsed_answer": None,
                "error": 1,
                "num_choices": len(item.choices) if item.choices else 0,
                "gold": item.gold if isinstance(item.gold, str) else None,
                "tokens_in": 0,
                "tokens_out": 0,
                "latency_ms": 0,
                "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "err": str(e),
            }

    # ── atomic append ─────────────────────────────────────────────
    def _persist(self, rec: dict) -> None:
        """One line + newline + flush + fsync. This is the checkpoint."""
        line = json.dumps(rec, ensure_ascii=False) + "\n"
        with self._write_lock:
            with self.responses_path.open("a") as fh:
                fh.write(line)
                fh.flush()
                # fsync guarantees the OS has committed the bytes to disk
                # before we consider the tuple done. Safe against kernel
                # panics, cheap enough (<1 ms per call in practice).
                try:
                    import os as _os
                    _os.fsync(fh.fileno())
                except OSError:
                    pass

    # ── progress snapshot ─────────────────────────────────────────
    def _snapshot_progress(self, total_pending: int) -> None:
        snap = {
            **self._counters,
            "total_pending_at_start": total_pending,
            "remaining": max(
                0,
                total_pending - self._counters["completed_this_session"]
                - self._counters["failed_this_session"],
            ),
            "updated_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        try:
            self.progress_path.write_text(json.dumps(snap, indent=2))
        except OSError:
            pass

    # ── lock ──────────────────────────────────────────────────────
    def _acquire_lock(self) -> None:
        if self.lock_path.exists():
            print(
                f"[runner] warning: {self.lock_path} exists — another run may be "
                f"active. Delete it if you're sure no other process is writing."
            )
        self.lock_path.write_text(f"pid={__import__('os').getpid()}\n")

    def _release_lock(self) -> None:
        self.lock_path.unlink(missing_ok=True)

    # ── signal handling ───────────────────────────────────────────
    def _install_signal_handler(self) -> None:
        first = [False]

        def handler(signum, _frame):
            if first[0]:
                print("\n[runner] second Ctrl-C, force exit.")
                raise KeyboardInterrupt
            first[0] = True
            print(
                "\n[runner] SIGINT — no new tasks; letting in-flight calls finish. "
                "Press Ctrl-C again to force exit."
            )
            self._stop_event.set()

        try:
            signal.signal(signal.SIGINT, handler)
        except ValueError:
            pass  # not on main thread

    # ── main entry ────────────────────────────────────────────────
    def run(self, items: Iterable[Item]) -> None:
        items = list(items)
        scorer = Scorer()

        pending: list[tuple[Item, ConditionSpec, str, int]] = []
        for item in items:
            for cond in self.config.conditions:
                for agent_name, seed in zip(cond.committee, cond.seeds):
                    key = (item.id, cond.name, agent_name, seed)
                    if key not in self._done_keys:
                        pending.append((item, cond, agent_name, seed))

        total_cells = len(items) * sum(
            len(c.committee) for c in self.config.conditions
        )
        print(
            f"[runner] {len(items)} items × {len(self.config.conditions)} conditions × "
            f"{sum(len(c.committee) for c in self.config.conditions)} agent-slots = "
            f"{total_cells} target tuples"
        )
        print(
            f"[runner] already done: {self._counters['done_at_start']} | "
            f"pending: {len(pending)}"
        )

        if not pending:
            print("[runner] nothing to do; materializing errors.parquet")
            self._materialize_errors()
            return

        self._acquire_lock()
        self._install_signal_handler()

        try:
            self._snapshot_progress(len(pending))
            with ThreadPoolExecutor(max_workers=self.config.n_workers) as ex:
                futures = [
                    ex.submit(self._one_call, item, cond, agent_name, seed, scorer)
                    for item, cond, agent_name, seed in pending
                ]
                progress_bar = tqdm(
                    as_completed(futures), total=len(futures), desc="calls",
                )
                for i, fut in enumerate(progress_bar, start=1):
                    rec = fut.result()
                    if rec.get("skipped"):
                        continue
                    if rec.get("err"):
                        self._counters["failed_this_session"] += 1
                    else:
                        self._counters["completed_this_session"] += 1
                    self._persist(rec)
                    if i % 20 == 0 or i == len(futures):
                        self._snapshot_progress(len(pending))
                    if self._stop_event.is_set():
                        # Cancel any not-yet-started
                        for f in futures:
                            f.cancel()
                        break
        finally:
            self._snapshot_progress(len(pending))
            self._release_lock()

        self._materialize_errors()

    # ── downstream artifact ────────────────────────────────────────
    def _materialize_errors(self) -> None:
        if not self.responses_path.exists():
            return
        rows = []
        with self.responses_path.open() as f:
            for line in f:
                try:
                    r = json.loads(line)
                except json.JSONDecodeError:
                    continue
                rows.append({
                    "item_id": r["item_id"],
                    "domain": r["domain"],
                    "condition": r["condition"],
                    "agent_name": r["agent_name"],
                    "family": r["family"],
                    "seed": r["seed"],
                    "error": r["error"],
                    "parsed_answer": r.get("parsed_answer"),
                    "num_choices": r.get("num_choices", 0),
                    "gold": r.get("gold"),
                })
        df = pd.DataFrame(rows)
        df.to_parquet(self.errors_path, index=False)
        print(f"[runner] wrote {self.errors_path} ({len(df)} rows)")
