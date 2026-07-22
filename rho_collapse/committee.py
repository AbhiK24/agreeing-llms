"""Committee enumeration and ρ-aware selection from a pool of T=0 agents.

The paper's first half diagnoses the problem: same-model committees
collapse to N_eff ≈ 1.3 effective agents because errors are correlated.
This module closes the loop — it turns the same design-effect math into a
*selection* procedure:

1. Build an items × models answer panel from the raw T=0 sweep (every
   model answered every item, so any subset of the pool is a valid
   committee — no new API calls needed).
2. Estimate per-model accuracy p_i and the pairwise error-correlation
   matrix ρ_ij from a calibration split.
3. Score a candidate committee by its **corrected evidence**

       S(committee) = N_eff(N, ρ̄) · log( p̄·(C−1) / (1−p̄) )

   i.e. the number of effectively independent agents times the log-odds
   evidence each one contributes. Under independence this is the exact
   Condorcet log-evidence of a unanimous committee; under correlation the
   design effect discounts it.
4. Select greedily (or exhaustively for small pools) under constraints:
   committee size budget and optional per-model cost budget.

Everything here is deterministic given the input rows.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
from math import isfinite, log
from typing import Iterable, Sequence

import numpy as np
import pandas as pd

from .rho import RhoEstimator

# Condition priority when a model was called more than once per item at
# T=0 (DeepSeek and Kimi appear in both D2 and D3). Routing
# nondeterminism (LIMITATIONS L8) makes the duplicates agree only ~93%
# of the time, so the choice must be a fixed rule, not "whichever".
DEFAULT_CONDITION_PRIORITY = (
    "D2_cross_family_chinese",
    "D3_cross_culture",
)


# ── answer panel ────────────────────────────────────────────────────────────

@dataclass
class Panel:
    """One domain's items × models answer matrix."""
    domain: str
    answers: pd.DataFrame          # items × models; parsed letter or NaN
    gold: pd.Series                # item_id → gold letter
    modal_num_choices: int         # modal C for the domain (Condorcet math)

    @property
    def models(self) -> list[str]:
        return list(self.answers.columns)

    @property
    def n_items(self) -> int:
        return int(len(self.answers))


def build_panels(
    rows: Iterable[dict],
    temperature: float = 0.0,
    condition_priority: Sequence[str] = DEFAULT_CONDITION_PRIORITY,
) -> dict[str, Panel]:
    """Build per-domain answer panels from raw response records.

    Keeps only rows at the given temperature with a definite parsed
    answer. When a (item, model) pair has rows in several conditions,
    the earliest condition in `condition_priority` wins; conditions not
    listed rank after all listed ones.
    """
    prio = {c: i for i, c in enumerate(condition_priority)}
    fallback_rank = len(condition_priority)

    best: dict[str, dict[tuple[str, str], tuple[int, str]]] = {}
    gold: dict[str, dict[str, str]] = {}
    choices: dict[str, list[int]] = {}
    seen_models: dict[str, set[str]] = {}

    for r in rows:
        if r.get("temperature") != temperature:
            continue
        parsed = r.get("parsed_answer")
        domain = r["domain"]
        item, model = r["item_id"], r["agent_name"]
        seen_models.setdefault(domain, set()).add(model)
        if r.get("gold"):
            gold.setdefault(domain, {}).setdefault(item, r["gold"])
        if r.get("num_choices"):
            choices.setdefault(domain, []).append(int(r["num_choices"]))
        if not parsed:
            continue
        rank = prio.get(r.get("condition"), fallback_rank)
        slot = best.setdefault(domain, {})
        prev = slot.get((item, model))
        if prev is None or rank < prev[0]:
            slot[(item, model)] = (rank, parsed)

    panels: dict[str, Panel] = {}
    for domain, cells in best.items():
        records = {
            (item, model): parsed for (item, model), (_, parsed) in cells.items()
        }
        ser = pd.Series(records)
        ser.index = pd.MultiIndex.from_tuples(ser.index, names=["item_id", "model"])
        answers = ser.unstack("model")
        # A model with zero definite answers in the domain still gets an
        # (all-NaN) column so downstream code sees the full pool.
        answers = answers.reindex(columns=sorted(seen_models[domain]))
        gold_ser = pd.Series(gold[domain]).reindex(answers.index)
        modal_c = (
            int(pd.Series(choices[domain]).mode().iloc[0])
            if choices.get(domain) else 2
        )
        panels[domain] = Panel(
            domain=domain,
            answers=answers,
            gold=gold_ser,
            modal_num_choices=modal_c,
        )
    return panels


# ── per-model statistics ────────────────────────────────────────────────────

def error_frame(panel: Panel) -> pd.DataFrame:
    """Items × models frame: 1.0 = wrong, 0.0 = right, NaN = no answer."""
    gold = panel.gold
    return panel.answers.apply(lambda col: (col != gold).astype(float).where(col.notna()))


def per_model_accuracy(panel: Panel) -> pd.Series:
    """Accuracy over the items each model actually answered."""
    return 1.0 - error_frame(panel).mean()


def pairwise_rho(errors: pd.DataFrame, min_overlap: int = 10) -> pd.DataFrame:
    """Pairwise-complete Pearson correlation of binary error columns.

    Pairs with fewer than `min_overlap` common items, or with a constant
    error column on the overlap, get ρ = 0 (same convention as
    RhoEstimator: caller should watch saturation separately).
    """
    models = list(errors.columns)
    out = pd.DataFrame(np.eye(len(models)), index=models, columns=models)
    for a, b in combinations(models, 2):
        sub = errors[[a, b]].dropna()
        if len(sub) < min_overlap:
            rho = 0.0
        else:
            rho = RhoEstimator._pearson(sub[a].values, sub[b].values)
        out.loc[a, b] = out.loc[b, a] = rho
    return out


def mean_pairwise_rho(rho_df: pd.DataFrame, members: Sequence[str]) -> float:
    """Mean off-diagonal ρ over the committee's member pairs."""
    if len(members) < 2:
        return 0.0
    vals = [rho_df.loc[a, b] for a, b in combinations(members, 2)]
    return float(np.mean(vals))


# ── committee scoring ───────────────────────────────────────────────────────

def evidence_score(
    members: Sequence[str],
    accuracy: pd.Series,
    rho_df: pd.DataFrame,
    num_choices: int,
) -> float:
    """Corrected total evidence: N_eff(N, ρ̄) · log-odds(p̄).

    p̄ is the committee's mean per-agent accuracy; ρ̄ its mean pairwise
    error correlation. log-odds is against a specific wrong answer out
    of C−1, i.e. log(p̄(C−1)/(1−p̄)) — each effectively independent
    agent contributes that much log-likelihood toward the gold answer.
    """
    n = len(members)
    if n == 0:
        return float("-inf")
    p = float(np.clip(accuracy[list(members)].mean(), 1e-6, 1 - 1e-6))
    rho = mean_pairwise_rho(rho_df, members)
    neff = RhoEstimator.n_eff(n, rho)
    return neff * log(p * (num_choices - 1) / (1.0 - p))


def plurality_accuracy(
    panel: Panel,
    members: Sequence[str],
    mode: str = "abstain",
) -> tuple[float, int]:
    """Expected plurality-vote accuracy of a committee on a panel.

    mode="abstain" (default, production-realistic): vote over every item
    in the panel; members without a definite answer abstain; an item
    where nobody answers scores 0. This keeps the item set identical
    across committees, so rankings are comparable.

    mode="strict" (paper-v1 convention): keep only items where every
    member answered.

    Ties are scored as expected value under a uniform random tie-break:
    if the gold answer is among m tied largest clusters, the item scores
    1/m.

    Returns (expected accuracy, number of items scored).
    """
    sub = panel.answers[list(members)]
    if mode == "strict":
        sub = sub.dropna(how="any")
    elif mode != "abstain":
        raise ValueError(f"unknown mode: {mode!r}")
    gold = panel.gold.reindex(sub.index)

    total = 0.0
    for item, row in sub.iterrows():
        votes = row.dropna()
        if votes.empty:
            continue  # nobody answered → scores 0
        counts = votes.value_counts()
        top = counts.max()
        winners = counts[counts == top].index
        if gold[item] in winners:
            total += 1.0 / len(winners)
    n = int(len(sub))
    return (total / n if n else float("nan")), n


# ── selection under constraints ─────────────────────────────────────────────

@dataclass
class SelectionResult:
    members: list[str]
    score: float
    trace: list[dict] = field(default_factory=list)  # per-step audit


def greedy_select(
    candidates: Sequence[str],
    accuracy: pd.Series,
    rho_df: pd.DataFrame,
    num_choices: int,
    n_max: int,
    costs: pd.Series | None = None,
    budget: float | None = None,
) -> SelectionResult:
    """ρ-aware greedy committee selection under constraints.

    Starts from the single highest-evidence agent, then repeatedly adds
    the candidate that maximizes the committee's corrected evidence
    S = N_eff · log-odds(p̄), subject to |committee| ≤ n_max and, if
    given, Σ cost ≤ budget. Stops early when no affordable addition
    improves S — a correlated or weak agent can *reduce* corrected
    evidence, and the design effect makes that visible.
    """
    chosen: list[str] = []
    spent = 0.0
    trace: list[dict] = []
    score = float("-inf")

    while len(chosen) < n_max:
        best_m, best_s = None, score
        for m in candidates:
            if m in chosen:
                continue
            if costs is not None and budget is not None:
                if spent + float(costs[m]) > budget:
                    continue
            s = evidence_score(chosen + [m], accuracy, rho_df, num_choices)
            if best_m is None or s > best_s:
                best_m, best_s = m, s
        if best_m is None or (chosen and best_s <= score):
            break
        chosen.append(best_m)
        score = best_s
        spent += float(costs[best_m]) if costs is not None else 0.0
        trace.append({
            "added": best_m,
            "score": score,
            "mean_rho": mean_pairwise_rho(rho_df, chosen),
            "mean_acc": float(accuracy[chosen].mean()),
            "spent": spent,
        })
    return SelectionResult(members=chosen, score=score, trace=trace)


def protocol_select(
    accuracy: pd.Series,
    rho_df: pd.DataFrame,
    costs: pd.Series,
    *,
    num_choices: int = 10,
    floor_delta: float = 0.10,
    min_marginal_neff: float = 0.10,
    n_max: int | None = None,
    budget: float | None = None,
) -> SelectionResult:
    """The paper's committee-building protocol: size by N_eff, floor by
    accuracy, fill by cost.

    The enumeration study motivates each step:
    1. **Floor** — drop models more than `floor_delta` below the pool's
       best accuracy. Min-member accuracy is the strongest robust driver
       of committee accuracy; everything subtler fails out-of-sample.
    2. **Size** — with the qualifying pool's mean pairwise ρ̂, grow N
       only while the design effect still pays: stop at the first N
       where N_eff(N+1) − N_eff(N) < `min_marginal_neff`. At ρ ≈ 0.5
       this stops at N = 3; members 4+ add almost no independent
       evidence.
    3. **Fill** — take the N cheapest qualifying models. Roster
       fine-tuning beyond the floor does not transfer out-of-sample, so
       cost is the only defensible tie-breaker. Optional `budget` caps
       total cost; `n_max` caps size.

    Returns a SelectionResult whose trace records the qualifying pool,
    ρ̂, and the chosen size, so the decision is auditable.
    """
    floor = float(accuracy.max()) - floor_delta
    qualifying = list(accuracy[accuracy >= floor].index)
    rho_hat = mean_pairwise_rho(rho_df, qualifying)

    n_cap = len(qualifying) if n_max is None else min(n_max, len(qualifying))
    n = 1
    while n < n_cap:
        gain = RhoEstimator.n_eff(n + 1, rho_hat) - RhoEstimator.n_eff(n, rho_hat)
        if gain < min_marginal_neff:
            break
        n += 1

    by_cost = list(costs[qualifying].sort_values().index)
    members: list[str] = []
    spent = 0.0
    for m in by_cost:
        if len(members) >= n:
            break
        c = float(costs[m])
        if budget is not None and spent + c > budget:
            continue
        members.append(m)
        spent += c

    score = evidence_score(members, accuracy, rho_df,
                           num_choices) if members else float("-inf")
    return SelectionResult(
        members=members,
        score=score,
        trace=[{
            "floor": floor,
            "qualifying": qualifying,
            "rho_hat": rho_hat,
            "target_size": n,
            "spent": spent,
        }],
    )


def exhaustive_select(
    candidates: Sequence[str],
    accuracy: pd.Series,
    rho_df: pd.DataFrame,
    num_choices: int,
    size: int,
) -> SelectionResult:
    """Argmax of corrected evidence over all committees of a fixed size."""
    best: SelectionResult | None = None
    for combo in combinations(candidates, size):
        s = evidence_score(combo, accuracy, rho_df, num_choices)
        if best is None or s > best.score:
            best = SelectionResult(members=list(combo), score=s)
    if best is None:
        raise ValueError("no committee of the requested size exists")
    return best
