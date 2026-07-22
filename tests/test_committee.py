"""Committee enumeration and ρ-aware selection.

These tests pin the behaviours the committee-selection finding rests on:
panel construction with the condition-priority dedup rule, plurality
voting (abstentions, ties), pairwise-complete ρ, the corrected-evidence
score, and the constrained greedy — in particular that greedy prefers a
diverse committee over a redundant one even when the redundant one has
higher raw accuracy.
"""
from __future__ import annotations

from math import isclose, log

import numpy as np
import pandas as pd
import pytest

from rho_collapse.committee import (
    Panel,
    build_panels,
    error_frame,
    evidence_score,
    exhaustive_select,
    greedy_select,
    mean_pairwise_rho,
    pairwise_rho,
    per_model_accuracy,
    plurality_accuracy,
    protocol_select,
)


# ── helpers ─────────────────────────────────────────────────────────────────

def _row(item, model, parsed, gold="A", domain="law",
         condition="D3_cross_culture", temperature=0.0, num_choices=10):
    return {
        "item_id": item, "domain": domain, "condition": condition,
        "agent_name": model, "parsed_answer": parsed, "gold": gold,
        "temperature": temperature, "num_choices": num_choices,
    }


def _panel(answers: dict[str, list], gold: list[str], domain="law", C=10) -> Panel:
    df = pd.DataFrame(answers)
    df.index = [f"i{k}" for k in range(len(df))]
    return Panel(
        domain=domain,
        answers=df,
        gold=pd.Series(gold, index=df.index),
        modal_num_choices=C,
    )


# ══════════════════════════════════════════════════════════════════════════
# 1. Panel construction
# ══════════════════════════════════════════════════════════════════════════

def test_build_panels_filters_temperature_and_blank_answers() -> None:
    rows = [
        _row("i1", "m1", "A"),
        _row("i1", "m2", None),                      # no definite answer
        _row("i2", "m1", "B", temperature=0.7),      # wrong temperature
    ]
    panels = build_panels(rows)
    panel = panels["law"]
    assert panel.n_items == 1
    assert panel.answers.loc["i1", "m1"] == "A"
    assert pd.isna(panel.answers.loc["i1", "m2"])


def test_build_panels_condition_priority_dedup() -> None:
    # Same (item, model) answered in both D2 and D3 with different letters
    # (the ~7% routing-nondeterminism case): D2 must win.
    rows = [
        _row("i1", "m1", "B", condition="D3_cross_culture"),
        _row("i1", "m1", "C", condition="D2_cross_family_chinese"),
    ]
    panel = build_panels(rows)["law"]
    assert panel.answers.loc["i1", "m1"] == "C"


def test_build_panels_d3_fills_when_d2_has_no_answer() -> None:
    rows = [
        _row("i1", "m1", None, condition="D2_cross_family_chinese"),
        _row("i1", "m1", "B", condition="D3_cross_culture"),
    ]
    panel = build_panels(rows)["law"]
    assert panel.answers.loc["i1", "m1"] == "B"


def test_build_panels_modal_num_choices() -> None:
    rows = [
        _row("i1", "m1", "A", num_choices=10),
        _row("i2", "m1", "A", num_choices=10),
        _row("i3", "m1", "A", num_choices=4),
    ]
    assert build_panels(rows)["law"].modal_num_choices == 10


# ══════════════════════════════════════════════════════════════════════════
# 2. Accuracy and ρ from panels
# ══════════════════════════════════════════════════════════════════════════

def test_per_model_accuracy_ignores_missing() -> None:
    panel = _panel(
        {"m1": ["A", "A", None, "B"], "m2": ["A", "B", "A", "B"]},
        gold=["A", "A", "A", "A"],
    )
    acc = per_model_accuracy(panel)
    assert isclose(acc["m1"], 2 / 3)   # answered 3, right on 2
    assert isclose(acc["m2"], 2 / 4)


def test_pairwise_rho_identical_and_independent() -> None:
    rng = np.random.default_rng(7)
    a = rng.integers(0, 2, 400).astype(float)
    b = rng.integers(0, 2, 400).astype(float)
    errors = pd.DataFrame({"m1": a, "m2": a, "m3": b})
    rho = pairwise_rho(errors)
    assert isclose(rho.loc["m1", "m2"], 1.0)
    assert abs(rho.loc["m1", "m3"]) < 0.15
    # symmetric with unit diagonal
    assert rho.equals(rho.T)
    assert (np.diag(rho.values) == 1.0).all()


def test_pairwise_rho_low_overlap_is_zero() -> None:
    errors = pd.DataFrame({
        "m1": [1.0, 0.0] + [np.nan] * 20,
        "m2": [1.0, 0.0] + [np.nan] * 20,
    })
    rho = pairwise_rho(errors, min_overlap=10)
    assert rho.loc["m1", "m2"] == 0.0


def test_mean_pairwise_rho_subset() -> None:
    rho = pd.DataFrame(
        [[1.0, 0.8, 0.2], [0.8, 1.0, 0.4], [0.2, 0.4, 1.0]],
        index=["a", "b", "c"], columns=["a", "b", "c"],
    )
    assert isclose(mean_pairwise_rho(rho, ["a", "b"]), 0.8)
    assert isclose(mean_pairwise_rho(rho, ["a", "b", "c"]), (0.8 + 0.2 + 0.4) / 3)
    assert mean_pairwise_rho(rho, ["a"]) == 0.0


# ══════════════════════════════════════════════════════════════════════════
# 3. Plurality vote
# ══════════════════════════════════════════════════════════════════════════

def test_plurality_majority_wins() -> None:
    panel = _panel(
        {"m1": ["A", "B"], "m2": ["A", "B"], "m3": ["B", "B"]},
        gold=["A", "B"],
    )
    acc, n = plurality_accuracy(panel, ["m1", "m2", "m3"])
    assert n == 2
    assert isclose(acc, 1.0)  # item 0: A wins 2-1 (gold); item 1: unanimous gold


def test_plurality_tie_scores_expected_value() -> None:
    # Two-way tie including gold → 1/2 credit.
    panel = _panel({"m1": ["A"], "m2": ["B"]}, gold=["A"])
    acc, n = plurality_accuracy(panel, ["m1", "m2"])
    assert isclose(acc, 0.5)


def test_plurality_abstain_vs_strict() -> None:
    # m2 abstains on item 1; m1 alone is wrong there.
    panel = _panel(
        {"m1": ["A", "C"], "m2": ["A", None]},
        gold=["A", "B"],
    )
    acc_abstain, n_abstain = plurality_accuracy(panel, ["m1", "m2"], mode="abstain")
    assert n_abstain == 2 and isclose(acc_abstain, 0.5)
    acc_strict, n_strict = plurality_accuracy(panel, ["m1", "m2"], mode="strict")
    assert n_strict == 1 and isclose(acc_strict, 1.0)


def test_plurality_all_abstain_scores_zero() -> None:
    panel = _panel({"m1": ["A", None], "m2": ["A", None]}, gold=["A", "B"])
    acc, n = plurality_accuracy(panel, ["m1", "m2"])
    assert n == 2 and isclose(acc, 0.5)


def test_plurality_unknown_mode_raises() -> None:
    panel = _panel({"m1": ["A"]}, gold=["A"])
    with pytest.raises(ValueError):
        plurality_accuracy(panel, ["m1"], mode="bogus")


# ══════════════════════════════════════════════════════════════════════════
# 4. Evidence score
# ══════════════════════════════════════════════════════════════════════════

def _uniform_stats(models, acc_val, rho_val):
    acc = pd.Series({m: acc_val for m in models})
    rho = pd.DataFrame(rho_val, index=models, columns=models)
    for m in models:
        rho.loc[m, m] = 1.0
    return acc, rho


def test_evidence_score_independent_matches_condorcet() -> None:
    # ρ = 0 → N_eff = N → score is N · log-odds exactly.
    models = ["a", "b", "c"]
    acc, rho = _uniform_stats(models, 0.8, 0.0)
    s = evidence_score(models, acc, rho, num_choices=10)
    assert isclose(s, 3 * log(0.8 * 9 / 0.2))


def test_evidence_score_full_correlation_equals_single_agent() -> None:
    # ρ = 1 → N_eff = 1 → five copies are worth exactly one agent.
    models = list("abcde")
    acc, rho = _uniform_stats(models, 0.8, 1.0)
    s5 = evidence_score(models, acc, rho, num_choices=10)
    s1 = evidence_score(["a"], acc, rho, num_choices=10)
    assert isclose(s5, s1)


def test_evidence_score_decreases_with_rho() -> None:
    models = list("abc")
    acc, rho_lo = _uniform_stats(models, 0.8, 0.1)
    _, rho_hi = _uniform_stats(models, 0.8, 0.7)
    assert evidence_score(models, acc, rho_lo, 10) > evidence_score(models, acc, rho_hi, 10)


# ══════════════════════════════════════════════════════════════════════════
# 5. Selection
# ══════════════════════════════════════════════════════════════════════════

def _diverse_vs_redundant_pool():
    """Pool where accuracy-only selection is provably wrong.

    clones c1-c3: 90% accurate but ρ = 0.95 with each other.
    divers d1-d2: 82% accurate, ρ ≈ 0 with everyone.
    Top-3-by-accuracy = the three clones → N_eff ≈ 1.03.
    """
    models = ["c1", "c2", "c3", "d1", "d2"]
    acc = pd.Series({"c1": 0.90, "c2": 0.90, "c3": 0.90, "d1": 0.82, "d2": 0.82})
    rho = pd.DataFrame(0.0, index=models, columns=models)
    for a in ("c1", "c2", "c3"):
        for b in ("c1", "c2", "c3"):
            rho.loc[a, b] = 0.95
    for m in models:
        rho.loc[m, m] = 1.0
    return models, acc, rho


def test_greedy_prefers_diverse_over_redundant() -> None:
    models, acc, rho = _diverse_vs_redundant_pool()
    res = greedy_select(models, acc, rho, num_choices=10, n_max=3)
    # One clone (the accuracy anchor) plus both independent agents.
    assert len([m for m in res.members if m.startswith("c")]) == 1
    assert set(m for m in res.members if m.startswith("d")) == {"d1", "d2"}
    # And it must beat the accuracy-only committee on corrected evidence.
    top_acc = evidence_score(["c1", "c2", "c3"], acc, rho, 10)
    assert res.score > top_acc


def test_greedy_stops_when_addition_hurts() -> None:
    # Adding a second 95%-correlated clone lowers corrected evidence, so
    # greedy should stop at n=3 even though n_max allows 4.
    models, acc, rho = _diverse_vs_redundant_pool()
    res = greedy_select(models, acc, rho, num_choices=10, n_max=4)
    assert len(res.members) == 3


def test_greedy_respects_cost_budget() -> None:
    models, acc, rho = _diverse_vs_redundant_pool()
    costs = pd.Series({"c1": 10.0, "c2": 10.0, "c3": 10.0, "d1": 1.0, "d2": 1.0})
    res = greedy_select(models, acc, rho, num_choices=10, n_max=3,
                        costs=costs, budget=5.0)
    # No clone is affordable — only the two cheap diverse agents fit.
    assert set(res.members) == {"d1", "d2"}


def test_greedy_trace_is_auditable() -> None:
    models, acc, rho = _diverse_vs_redundant_pool()
    res = greedy_select(models, acc, rho, num_choices=10, n_max=3)
    assert len(res.trace) == len(res.members)
    assert [t["added"] for t in res.trace] == res.members
    assert res.trace[-1]["score"] == res.score


def test_exhaustive_matches_greedy_on_easy_pool() -> None:
    models, acc, rho = _diverse_vs_redundant_pool()
    ex = exhaustive_select(models, acc, rho, num_choices=10, size=3)
    gr = greedy_select(models, acc, rho, num_choices=10, n_max=3)
    assert set(ex.members) == set(gr.members)
    assert isclose(ex.score, gr.score)


def test_exhaustive_empty_pool_raises() -> None:
    acc = pd.Series(dtype=float)
    rho = pd.DataFrame()
    with pytest.raises(ValueError):
        exhaustive_select([], acc, rho, num_choices=10, size=3)


# ══════════════════════════════════════════════════════════════════════════
# 6. Protocol: floor → size by N_eff → fill by cost
# ══════════════════════════════════════════════════════════════════════════

def _protocol_pool(rho_val: float):
    models = ["strong_cheap", "strong_mid", "strong_dear", "ok_cheap", "weak"]
    acc = pd.Series({"strong_cheap": 0.88, "strong_mid": 0.90,
                     "strong_dear": 0.89, "ok_cheap": 0.82, "weak": 0.55})
    rho = pd.DataFrame(rho_val, index=models, columns=models)
    for m in models:
        rho.loc[m, m] = 1.0
    costs = pd.Series({"strong_cheap": 1.0, "strong_mid": 5.0,
                       "strong_dear": 20.0, "ok_cheap": 0.5, "weak": 0.1})
    return acc, rho, costs


def test_protocol_floors_out_weak_model() -> None:
    acc, rho, costs = _protocol_pool(0.6)
    res = protocol_select(acc, rho, costs)
    assert "weak" not in res.members          # 0.55 < 0.90 − 0.10
    assert "weak" not in res.trace[0]["qualifying"]
    assert "ok_cheap" in res.trace[0]["qualifying"]  # 0.82 ≥ 0.80 qualifies


def test_protocol_sizes_small_when_rho_high() -> None:
    # ρ = 0.6: marginal N_eff gains are 0.25, 0.11, 0.07… → stop at N = 3.
    acc, rho, costs = _protocol_pool(0.6)
    res = protocol_select(acc, rho, costs)
    assert res.trace[0]["target_size"] == 3
    assert len(res.members) == 3


def test_protocol_sizes_large_when_independent() -> None:
    # ρ = 0: every marginal member adds a full agent → take the whole
    # qualifying pool.
    acc, rho, costs = _protocol_pool(0.0)
    res = protocol_select(acc, rho, costs)
    assert len(res.members) == len(res.trace[0]["qualifying"])


def test_protocol_fills_cheapest_first() -> None:
    acc, rho, costs = _protocol_pool(0.6)
    res = protocol_select(acc, rho, costs)
    # cheapest three qualifying: ok_cheap (0.5), strong_cheap (1), strong_mid (5)
    assert res.members == ["ok_cheap", "strong_cheap", "strong_mid"]


def test_protocol_respects_budget_and_nmax() -> None:
    acc, rho, costs = _protocol_pool(0.6)
    res = protocol_select(acc, rho, costs, budget=2.0)
    assert res.members == ["ok_cheap", "strong_cheap"]  # strong_mid unaffordable
    res2 = protocol_select(acc, rho, costs, n_max=1)
    assert res2.members == ["ok_cheap"]


# ══════════════════════════════════════════════════════════════════════════
# 7. End-to-end on a synthetic panel: selection improves held-out votes
# ══════════════════════════════════════════════════════════════════════════

def test_rho_aware_selection_beats_accuracy_only_on_held_out_votes() -> None:
    """The finding the paper's final section rests on, in miniature.

    Generate correlated answers: three clones share error events; two
    diverse agents err independently. Estimate stats on a calibration
    half, select by each strategy, score plurality accuracy on the
    held-out half. ρ-aware must win.
    """
    rng = np.random.default_rng(42)
    M = 2000
    gold = np.full(M, "A")
    wrong = np.array(["B", "C", "D"])

    shared_err = rng.random(M) < 0.10          # clone-common error events
    shared_pick = wrong[rng.integers(0, 3, M)]  # clones agree on the wrong letter

    cols: dict[str, np.ndarray] = {}
    for name in ("c1", "c2", "c3"):
        own_err = rng.random(M) < 0.02
        ans = np.where(shared_err, shared_pick, gold)
        ans = np.where(~shared_err & own_err, wrong[rng.integers(0, 3, M)], ans)
        cols[name] = ans
    for name in ("d1", "d2"):
        err = rng.random(M) < 0.15
        cols[name] = np.where(err, wrong[rng.integers(0, 3, M)], gold)

    df = pd.DataFrame(cols, index=[f"i{k}" for k in range(M)])
    gold_ser = pd.Series(gold, index=df.index)
    cal = Panel("syn", df.iloc[: M // 2], gold_ser.iloc[: M // 2], 4)
    test = Panel("syn", df.iloc[M // 2:], gold_ser.iloc[M // 2:], 4)

    acc = per_model_accuracy(cal)
    rho = pairwise_rho(error_frame(cal))

    rho_aware = greedy_select(list(df.columns), acc, rho, num_choices=4, n_max=3)
    acc_only = list(acc.sort_values(ascending=False).index[:3])

    a_rho, _ = plurality_accuracy(test, rho_aware.members)
    a_acc, _ = plurality_accuracy(test, acc_only)
    assert set(acc_only) == {"c1", "c2", "c3"}   # the trap is real
    assert a_rho > a_acc
