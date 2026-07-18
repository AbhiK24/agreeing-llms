"""ρ estimator, Bayesian Condorcet posterior, and cluster analysis.

Every headline number the paper reports comes out of this module, so the
tests here pin the boundary cases explicitly.
"""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from rho_collapse.rho import RhoEstimator


# ── helpers ─────────────────────────────────────────────────────────────────

def _make_errors_df(matrix: np.ndarray, domain: str = "medicine",
                    condition: str = "D1", num_choices: int = 4,
                    gold: str = "A", answers: np.ndarray | None = None) -> pd.DataFrame:
    """Build a runner-style DataFrame from a raw M × N error matrix.

    If `answers` is provided (shape M × N of strings), those become
    `parsed_answer`; otherwise we synthesize plausible letters so that
    error=0 → parsed=gold and error=1 → parsed="Z" (a distinct wrong choice).
    """
    rows = []
    n_items, n_agents = matrix.shape
    for i in range(n_items):
        for j in range(n_agents):
            if answers is not None:
                parsed = answers[i, j]
            else:
                parsed = gold if matrix[i, j] == 0 else "Z"
            rows.append({
                "item_id": f"item-{i:04d}",
                "domain": domain,
                "condition": condition,
                "agent_name": f"agent{j}",
                "family": "test",
                "seed": 1,
                "error": int(matrix[i, j]),
                "parsed_answer": parsed,
                "num_choices": num_choices,
                "gold": gold,
            })
    return pd.DataFrame(rows)


# ══════════════════════════════════════════════════════════════════════════
# 1. ρ boundary cases
# ══════════════════════════════════════════════════════════════════════════

def test_rho_near_zero_for_independent_errors() -> None:
    rng = np.random.default_rng(0)
    matrix = rng.integers(0, 2, size=(500, 5))
    est = RhoEstimator(_make_errors_df(matrix))
    assert abs(est.mean_rho("medicine", "D1")) < 0.1


def test_rho_one_for_identical_columns() -> None:
    rng = np.random.default_rng(1)
    col = rng.integers(0, 2, size=(500,))
    matrix = np.tile(col.reshape(-1, 1), (1, 5))
    est = RhoEstimator(_make_errors_df(matrix))
    assert est.mean_rho("medicine", "D1") > 0.99


def test_rho_positive_for_partially_shared_errors() -> None:
    rng = np.random.default_rng(2)
    base = (rng.random(500) < 0.4).astype(int)
    matrix = np.zeros((500, 5), dtype=int)
    for j in range(5):
        keep = rng.random(500) < 0.7
        matrix[:, j] = np.where(keep, base, (rng.random(500) < 0.4).astype(int))
    est = RhoEstimator(_make_errors_df(matrix))
    assert est.mean_rho("medicine", "D1") > 0.3


# ══════════════════════════════════════════════════════════════════════════
# 2. N_eff formula
# ══════════════════════════════════════════════════════════════════════════

def test_n_eff_equals_n_when_rho_zero() -> None:
    assert RhoEstimator.n_eff(5, 0.0) == 5.0


def test_n_eff_collapses_to_one_when_rho_one() -> None:
    assert RhoEstimator.n_eff(5, 1.0) == 1.0


def test_n_eff_midrange() -> None:
    # rho = 0.65, N = 5 → design effect = 1 + 4*0.65 = 3.6 → N_eff ≈ 1.389
    assert abs(RhoEstimator.n_eff(5, 0.65) - 5 / 3.6) < 1e-6


def test_n_eff_clips_negative_rho() -> None:
    assert RhoEstimator.n_eff(5, -0.2) == 5.0


# ══════════════════════════════════════════════════════════════════════════
# 3. Bayesian Condorcet posterior — hand-computed cases
# ══════════════════════════════════════════════════════════════════════════

def test_posterior_reduces_to_p_when_k_is_1() -> None:
    """One agent's answer under uniform prior: posterior = per-agent accuracy."""
    for p in [0.3, 0.5, 0.7, 0.9]:
        for C in [4, 10]:
            got = RhoEstimator.bayes_posterior(k=1, p=p, num_choices=C)
            assert abs(got - p) < 1e-6, f"k=1 posterior != p (p={p}, C={C}, got={got})"


def test_posterior_saturates_toward_one_with_large_k() -> None:
    """As k → ∞ and per-agent accuracy > 1/C, posterior → 1."""
    for C in [4, 10]:
        posterior = RhoEstimator.bayes_posterior(k=20, p=0.7, num_choices=C)
        assert posterior > 0.999, f"C={C} posterior at k=20 was {posterior}"


def test_posterior_more_confident_with_more_choices() -> None:
    """Agreeing on 1 of 10 answers is more informative than agreeing on 1 of 4."""
    for k in [2, 3, 5]:
        p_10 = RhoEstimator.bayes_posterior(k=k, p=0.6, num_choices=10)
        p_4 = RhoEstimator.bayes_posterior(k=k, p=0.6, num_choices=4)
        assert p_10 > p_4, f"C=10 posterior should exceed C=4 (k={k})"


def test_posterior_matches_manual_calculation() -> None:
    """k=2, p=0.5, C=4 → posterior = 0.75 by hand."""
    got = RhoEstimator.bayes_posterior(k=2, p=0.5, num_choices=4)
    assert abs(got - 0.75) < 1e-6, f"expected 0.75, got {got}"


def test_posterior_uses_k_eff_for_correction() -> None:
    """A committee with ρ=0.65, N=5 has N_eff=1.4. Its k=5 corrected
    posterior must equal a raw k=1.4 Bayesian posterior."""
    p = 0.7
    C = 4
    n = 5
    rho = 0.65
    n_eff = RhoEstimator.n_eff(n, rho)
    k = 5
    k_eff = k * n_eff / n
    corrected = RhoEstimator.bayes_posterior(k=k_eff, p=p, num_choices=C)
    # Sanity: corrected should sit BELOW naive (k=5), ABOVE single agent (k=1)
    naive = RhoEstimator.bayes_posterior(k=k, p=p, num_choices=C)
    single = RhoEstimator.bayes_posterior(k=1, p=p, num_choices=C)
    assert single < corrected < naive


# ══════════════════════════════════════════════════════════════════════════
# 4. Cluster analysis — bin by largest same-answer cluster
# ══════════════════════════════════════════════════════════════════════════

def test_cluster_analysis_captures_confidently_wrong_items() -> None:
    """The bug we're fixing: 5 agents all pick a wrong letter must land in
    bin k=5 (largest cluster = 5), not be dropped."""
    n_items = 20
    n_agents = 5
    matrix = np.ones((n_items, n_agents), dtype=int)  # all wrong
    answers = np.full((n_items, n_agents), "C")       # all agreed on C
    df = _make_errors_df(matrix, gold="A", answers=answers)
    est = RhoEstimator(df)
    cell = est.cell("medicine", "D1")
    # We expect a bin at k=5 with observed_correct_rate = 0 (all wrong)
    ks = {ka.k for ka in cell.k_agree}
    assert 5 in ks
    k5 = next(ka for ka in cell.k_agree if ka.k == 5)
    assert k5.n_items == n_items
    assert k5.observed_correct_rate == 0.0


def test_cluster_analysis_captures_confidently_right_items() -> None:
    """5 agents all pick the correct letter → bin k=5, observed 1.0."""
    n_items = 20
    n_agents = 5
    matrix = np.zeros((n_items, n_agents), dtype=int)
    answers = np.full((n_items, n_agents), "A")
    df = _make_errors_df(matrix, gold="A", answers=answers)
    cell = RhoEstimator(df).cell("medicine", "D1")
    k5 = next(ka for ka in cell.k_agree if ka.k == 5)
    assert k5.observed_correct_rate == 1.0


def test_cluster_bin_size_reflects_largest_cluster() -> None:
    """3 agents pick A, 2 pick B → largest cluster size = 3."""
    n_items = 15
    answers = np.array(
        [["A", "A", "A", "B", "B"] for _ in range(n_items)]
    )
    matrix = np.zeros(answers.shape, dtype=int)  # A is correct
    df = _make_errors_df(matrix, gold="A", answers=answers)
    cell = RhoEstimator(df).cell("medicine", "D1")
    ks = {ka.k for ka in cell.k_agree}
    assert ks == {3}, f"expected only k=3, got {ks}"


# ══════════════════════════════════════════════════════════════════════════
# 5. Saturation warning
# ══════════════════════════════════════════════════════════════════════════

def test_saturation_warning_triggers_above_threshold() -> None:
    """When per-agent accuracy > 0.95 the cell flags saturation so the
    reader isn't tricked by a spurious ρ ≈ 0."""
    n_items = 100
    n_agents = 5
    matrix = np.zeros((n_items, n_agents), dtype=int)
    matrix[:3, 0] = 1  # 97% accuracy for agent 0, 100% for others
    df = _make_errors_df(matrix, gold="A")
    cell = RhoEstimator(df).cell("medicine", "D1")
    assert cell.saturation_warning is True


def test_no_saturation_warning_at_moderate_accuracy() -> None:
    rng = np.random.default_rng(0)
    matrix = rng.integers(0, 2, size=(500, 5))  # ~50% accuracy
    df = _make_errors_df(matrix, gold="A")
    cell = RhoEstimator(df).cell("medicine", "D1")
    assert cell.saturation_warning is False


# ══════════════════════════════════════════════════════════════════════════
# 6. Bootstrap CI
# ══════════════════════════════════════════════════════════════════════════

def test_bootstrap_ci_brackets_point_estimate() -> None:
    rng = np.random.default_rng(3)
    matrix = rng.integers(0, 2, size=(300, 4))
    est = RhoEstimator(_make_errors_df(matrix))
    rho = est.mean_rho("medicine", "D1")
    lo, hi = est.bootstrap_ci("medicine", "D1", iters=200)
    assert lo - 0.05 <= rho <= hi + 0.05


# ══════════════════════════════════════════════════════════════════════════
# 7. End-to-end report shape
# ══════════════════════════════════════════════════════════════════════════

def test_report_produces_expected_cells() -> None:
    rng = np.random.default_rng(4)
    frames = []
    for domain in ("medicine", "science", "law"):
        for condition in ("D1", "D2"):
            matrix = rng.integers(0, 2, size=(100, 4))
            frames.append(_make_errors_df(matrix, domain=domain, condition=condition))
    df = pd.concat(frames, ignore_index=True)
    report = RhoEstimator(df).run_report()
    assert len(report["results"]) == 6
    for cell in report["results"]:
        assert cell["n_agents"] == 4
        assert cell["n_items"] == 100
        # Every headline field the report renders
        for key in [
            "rho_mean", "rho_ci_low", "rho_ci_high", "n_eff",
            "mean_agent_accuracy", "avg_num_choices", "saturation_warning",
            "k_agree", "per_agent_accuracy",
        ]:
            assert key in cell, f"missing {key}"
