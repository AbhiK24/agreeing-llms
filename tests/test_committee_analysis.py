"""Pure helpers of the committee-selection analysis driver."""
from __future__ import annotations

from math import isclose

import numpy as np
import pandas as pd

from rho_collapse.committee import Panel
from rho_collapse.committee_analysis import (
    enumerate_committees,
    lodo_eval,
    pooled_stats,
    regret_matrix,
    seed_committee_plurality,
    select_by_strategy,
    split_half_eval,
)


def _panel(answers: dict[str, list], gold: list[str], domain="law", C=4) -> Panel:
    df = pd.DataFrame(answers)
    df.index = [f"{domain}-i{k}" for k in range(len(df))]
    return Panel(domain=domain, answers=df,
                 gold=pd.Series(gold, index=df.index), modal_num_choices=C)


def _synthetic_panel(domain: str, seed: int, m: int = 200) -> Panel:
    """Three ~85% models with one shared-error pair, plus a weak loner."""
    rng = np.random.default_rng(seed)
    gold = np.full(m, "A")
    wrong = np.array(["B", "C", "D"])
    shared = rng.random(m) < 0.15
    pick = wrong[rng.integers(0, 3, m)]
    cols = {
        "m1": np.where(shared, pick, gold),
        "m2": np.where(shared, pick, gold),
        "m3": np.where(rng.random(m) < 0.15, wrong[rng.integers(0, 3, m)], gold),
        "m4": np.where(rng.random(m) < 0.40, wrong[rng.integers(0, 3, m)], gold),
    }
    df = pd.DataFrame(cols, index=[f"{domain}-i{k}" for k in range(m)])
    return Panel(domain, df, pd.Series(gold, index=df.index), 4)


def test_enumerate_committees_counts_and_columns() -> None:
    panel = _synthetic_panel("law", 0)
    table = enumerate_committees(panel, [3, 4])
    assert len(table) == 4 + 1          # C(4,3) + C(4,4)
    assert (table[table["size"] == 3]["members"].nunique()) == 4
    row = table.iloc[0]
    for col in ("mean_acc", "mean_rho", "n_eff", "evidence", "plurality_acc"):
        assert np.isfinite(row[col])


def test_enumerate_flags_correlated_pair() -> None:
    panel = _synthetic_panel("law", 1)
    table = enumerate_committees(panel, [3]).set_index("members")
    # The clone pair (m1, m2) drags ρ̄ up relative to the independent trio.
    assert table.loc["m1+m2+m3", "mean_rho"] > table.loc["m1+m3+m4", "mean_rho"]


def test_regret_matrix_zero_diagonal_nonnegative() -> None:
    tables = {
        d: enumerate_committees(_synthetic_panel(d, i), [3])
        for i, d in enumerate(["law", "med"])
    }
    reg = regret_matrix(tables, size=3)
    assert isclose(reg.loc["law", "law"], 0.0)
    assert isclose(reg.loc["med", "med"], 0.0)
    assert (reg.values >= -1e-12).all()


def test_pooled_stats_matches_manual_concat() -> None:
    p1 = _panel({"m1": ["A", "B"], "m2": ["A", "A"]}, ["A", "A"], domain="d1")
    p2 = _panel({"m1": ["A", "A"], "m2": ["B", "A"]}, ["A", "A"], domain="d2")
    acc, rho = pooled_stats([p1, p2])
    assert isclose(acc["m1"], 3 / 4)
    assert isclose(acc["m2"], 3 / 4)
    assert list(rho.columns) == ["m1", "m2"]


def test_select_by_strategy_top_acc() -> None:
    acc = pd.Series({"a": 0.9, "b": 0.5, "c": 0.8})
    rho = pd.DataFrame(np.eye(3), index=list("abc"), columns=list("abc"))
    assert select_by_strategy("top_acc", acc, rho, 4, 2) == ["a", "c"]


def test_seed_committee_plurality_scores_all_items() -> None:
    def r(item, seed, parsed, cond="D1_same_model", gold="A"):
        return {"item_id": item, "domain": "law", "condition": cond,
                "agent_name": "m", "seed": seed, "parsed_answer": parsed,
                "gold": gold, "tokens_out": 100}
    rows = [
        # i1: seeds vote A, A, B → gold A wins
        r("i1", 1, "A"), r("i1", 2, "A"), r("i1", 3, "B"),
        # i2: only one seed answers, wrongly
        r("i2", 1, "C"),
        # i3: exists in the dataset (via another condition) but no D1
        # seed produced an answer → counts as wrong, not dropped
        r("i3", 1, "A", cond="D3_cross_culture"),
    ]
    out = seed_committee_plurality(rows)
    assert out["law"]["n_items"] == 3
    assert isclose(out["law"]["accuracy"], 1 / 3)   # only i1 correct
    assert out["law"]["n_seeds"] == 3
    assert isclose(out["law"]["cost"], 300.0)        # 3 seeds × 100 tokens


def test_seed_committee_plurality_tie_expected_value() -> None:
    def r(item, seed, parsed):
        return {"item_id": item, "domain": "law", "condition": "D1_same_model",
                "agent_name": "m", "seed": seed, "parsed_answer": parsed,
                "gold": "A", "tokens_out": 10}
    out = seed_committee_plurality([r("i1", 1, "A"), r("i1", 2, "B")])
    assert isclose(out["law"]["accuracy"], 0.5)


def test_split_half_and_lodo_run_end_to_end() -> None:
    panels = {d: _synthetic_panel(d, i) for i, d in
              enumerate(["law", "med", "sci"])}
    sh = split_half_eval(panels["law"], size=3, n_splits=3, seed=0)
    assert set(sh) == {"rho_greedy", "rho_exhaustive", "top_acc",
                       "empirical", "random"}
    assert 0.0 <= sh["rho_greedy"]["mean"] <= 1.0

    lodo = lodo_eval(panels, size=3)
    assert set(lodo) == {"law", "med", "sci"}
    for res in lodo.values():
        assert res["oracle"]["accuracy"] >= res["rho_greedy"]["accuracy"] - 1e-9
        assert len(res["top_acc"]["members"]) == 3
