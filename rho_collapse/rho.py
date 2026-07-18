"""Statistical core: ρ, N_eff, cluster analysis, and the overconfidence gap.

Everything here is deterministic. Inputs come from
`runs/<run_id>/errors.parquet`; outputs go to `rho_by_domain.json`.

Key formulas
------------
1. Pairwise error correlation ρ — mean Pearson correlation of per-agent
   error columns across all C(N,2) agent pairs.

2. Design-effect adjusted committee size
        N_eff = N / (1 + (N-1) · ρ)
   with ρ clipped to [0, 1] (negative ρ would inflate N_eff artificially).

3. Cluster analysis — for each item, group the N agents by their picked
   answer. Let k = size of the largest cluster on that item, and let
   "correct" = 1 iff the largest cluster's answer is the gold answer.
   Overconfidence is measured per (largest-cluster-size k) bin.

4. Bayesian Condorcet posterior — the naive confidence a Condorcet-style
   analysis would assign to a committee where k of N picked the same
   answer, under the independence assumption:

        P(correct | k agree)  =  p^k
                                --------------------------------------
                                p^k  +  (C-1) · ((1-p)/(C-1))^k

   where p = average per-agent accuracy and C = number of answer choices.
   The corrected posterior uses k_eff = k · N_eff / N in place of k.
"""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from itertools import combinations
from math import isfinite
from pathlib import Path

import numpy as np
import pandas as pd


# ── Result dataclasses ──────────────────────────────────────────────────────

@dataclass
class KAgreeResult:
    """One row of the k-largest-cluster analysis."""
    k: int                          # size of the largest cluster on the item
    n_items: int                    # count of items with this cluster size
    observed_correct_rate: float    # fraction where the largest cluster was correct
    naive_posterior: float          # Condorcet, assuming independence
    corrected_posterior: float      # Condorcet with k_eff = k · N_eff / N
    overconfidence_gap: float       # naive_posterior − observed_correct_rate


@dataclass
class CellResult:
    domain: str
    condition: str
    n_agents: int
    n_items: int
    avg_num_choices: float          # 4 (MedQA) or 10 (MMLU-Pro); may be mixed
    per_agent_accuracy: dict[str, float]
    mean_agent_accuracy: float
    rho_mean: float
    rho_ci_low: float
    rho_ci_high: float
    n_eff: float
    saturation_warning: bool        # accuracy > 0.95 flags a spurious ρ ≈ 0
    k_agree: list[KAgreeResult]


# ── ρ estimator ─────────────────────────────────────────────────────────────

class RhoEstimator:
    """Consumes the errors DataFrame; emits per-(domain, condition) cells."""

    SATURATION_ACC_THRESHOLD = 0.95

    def __init__(self, errors_df: pd.DataFrame) -> None:
        self.df = errors_df.copy()

    # ── error-matrix helper ────────────────────────────────────────
    def _cell_df(self, domain: str, condition: str) -> pd.DataFrame:
        sub = self.df[
            (self.df["domain"] == domain) & (self.df["condition"] == condition)
        ]
        if sub.empty:
            return sub
        sub = sub.copy()
        sub["_agent_id"] = sub["agent_name"] + "#" + sub["seed"].astype(str)
        return sub

    def _error_matrix(
        self, cell_df: pd.DataFrame
    ) -> tuple[pd.DataFrame, list[str]]:
        """Return items × agents error matrix."""
        if cell_df.empty:
            return pd.DataFrame(), []
        pivot = cell_df.pivot_table(
            index="item_id", columns="_agent_id", values="error", aggfunc="first",
        )
        pivot = pivot.dropna(how="any")
        return pivot, list(pivot.columns)

    # ── pairwise ρ ────────────────────────────────────────────────
    @staticmethod
    def _pearson(a: np.ndarray, b: np.ndarray) -> float:
        """Pearson correlation. Returns 0 if either column is constant, but
        the caller should also check saturation to know whether ρ ≈ 0
        means "independent" or "no errors to correlate"."""
        if a.std() == 0 or b.std() == 0:
            return 0.0
        return float(np.corrcoef(a, b)[0, 1])

    def mean_rho(self, domain: str, condition: str) -> float:
        matrix, agents = self._error_matrix(self._cell_df(domain, condition))
        if matrix.empty or len(agents) < 2:
            return float("nan")
        vals = [
            self._pearson(matrix.iloc[:, i].values, matrix.iloc[:, j].values)
            for i, j in combinations(range(len(agents)), 2)
        ]
        return float(np.mean(vals))

    def bootstrap_ci(
        self, domain: str, condition: str, iters: int = 1000, seed: int = 42,
    ) -> tuple[float, float]:
        matrix, agents = self._error_matrix(self._cell_df(domain, condition))
        if matrix.empty or len(agents) < 2:
            return (float("nan"), float("nan"))
        rng = np.random.default_rng(seed)
        arr = matrix.values
        M = arr.shape[0]
        samples = []
        for _ in range(iters):
            idx = rng.integers(0, M, size=M)
            sub = arr[idx]
            vals = [
                self._pearson(sub[:, i], sub[:, j])
                for i, j in combinations(range(sub.shape[1]), 2)
            ]
            samples.append(float(np.mean(vals)))
        lo, hi = np.quantile(samples, [0.025, 0.975])
        return float(lo), float(hi)

    @staticmethod
    def n_eff(n: int, rho: float) -> float:
        """Design-effect corrected committee size. Negative ρ (rare) clipped
        to 0 so we don't inflate N_eff above the actual committee size."""
        if n <= 0:
            return float("nan")
        rho_clipped = max(rho, 0.0) if isfinite(rho) else 0.0
        return n / (1.0 + (n - 1) * rho_clipped)

    # ── Bayesian Condorcet posterior ──────────────────────────────
    @staticmethod
    def bayes_posterior(k: float, p: float, num_choices: int) -> float:
        """P(correct | cluster of size k picked the same answer) under
        independence, per-agent accuracy p, and num_choices answer options.

        Uses the standard Bayes update with a uniform prior over which of
        the C answers is correct:
            L_correct = p^k
            L_specific_wrong = ((1-p)/(C-1))^k
            posterior = L_correct / (L_correct + (C-1) · L_specific_wrong)

        Correctly reduces to `p` when k = 1 (single agent), and to 1 when
        k → ∞ with p > 1/C (asymptotic certainty).
        """
        if num_choices < 2 or k <= 0 or not isfinite(p):
            return float("nan")
        p = min(max(p, 1e-6), 1 - 1e-6)  # clip away from 0/1 for stability
        C = num_choices
        # Likelihood ratio: L_specific_wrong / L_correct = ((1-p)/(p·(C-1)))^k
        lr = ((1 - p) / (p * (C - 1))) ** k
        return 1.0 / (1.0 + (C - 1) * lr)

    # ── cluster analysis ──────────────────────────────────────────
    @staticmethod
    def _largest_cluster(cell_group: pd.DataFrame) -> tuple[int, bool] | None:
        """For one item's agent rows, return (largest-cluster-size, correct?).

        None/unparseable answers are excluded from clustering. If no agent
        produced a parseable answer, returns None.
        """
        answers = cell_group["parsed_answer"].dropna()
        if answers.empty:
            return None
        counts = answers.value_counts()
        largest_size = int(counts.iloc[0])
        largest_answer = counts.index[0]
        gold_series = cell_group["gold"].dropna()
        if gold_series.empty:
            # No gold recorded for this row (shouldn't happen post v0.2)
            return None
        gold = gold_series.iloc[0]
        return largest_size, (largest_answer == gold)

    def _cluster_bins(self, cell_df: pd.DataFrame) -> dict[int, list[bool]]:
        """Bin every item by its largest-cluster size."""
        bins: dict[int, list[bool]] = {}
        if cell_df.empty or "parsed_answer" not in cell_df.columns:
            return bins
        for _, group in cell_df.groupby("item_id"):
            res = self._largest_cluster(group)
            if res is None:
                continue
            k, correct = res
            bins.setdefault(k, []).append(correct)
        return bins

    # ── per-cell rollup ───────────────────────────────────────────
    def cell(self, domain: str, condition: str, ci_iters: int = 500) -> CellResult:
        cell_df = self._cell_df(domain, condition)
        matrix, agents = self._error_matrix(cell_df)
        n_agents = len(agents)
        rho = self.mean_rho(domain, condition)
        ci_lo, ci_hi = self.bootstrap_ci(domain, condition, iters=ci_iters)
        n_eff_val = self.n_eff(n_agents, rho) if n_agents > 0 else float("nan")

        per_agent_acc = {
            a: float(1 - matrix[a].mean()) if not matrix.empty else 0.0
            for a in agents
        }
        p_bar = (
            float(np.mean(list(per_agent_acc.values()))) if per_agent_acc else 0.0
        )
        saturation = p_bar > self.SATURATION_ACC_THRESHOLD

        # Number of choices — should be constant per domain but we average
        # for safety and pass in as float.
        avg_C = float(cell_df["num_choices"].dropna().mean()) if not cell_df.empty else 0.0
        C_int = int(round(avg_C)) if avg_C >= 2 else 2

        # Cluster bins
        bins = self._cluster_bins(cell_df)
        k_results: list[KAgreeResult] = []
        for k in sorted(bins.keys()):
            outcomes = bins[k]
            if not outcomes:
                continue
            observed = float(np.mean([1.0 if x else 0.0 for x in outcomes]))
            naive = self.bayes_posterior(k=k, p=p_bar, num_choices=C_int)
            k_eff = k * (n_eff_val / n_agents) if n_agents > 0 else k
            corrected = self.bayes_posterior(k=k_eff, p=p_bar, num_choices=C_int)
            k_results.append(KAgreeResult(
                k=k,
                n_items=len(outcomes),
                observed_correct_rate=observed,
                naive_posterior=naive,
                corrected_posterior=corrected,
                overconfidence_gap=naive - observed,
            ))

        return CellResult(
            domain=domain,
            condition=condition,
            n_agents=n_agents,
            n_items=int(len(matrix)),
            avg_num_choices=avg_C,
            per_agent_accuracy=per_agent_acc,
            mean_agent_accuracy=p_bar,
            rho_mean=rho,
            rho_ci_low=ci_lo,
            rho_ci_high=ci_hi,
            n_eff=n_eff_val,
            saturation_warning=saturation,
            k_agree=k_results,
        )

    # ── whole run ──────────────────────────────────────────────────
    def run_report(self) -> dict:
        results = []
        for domain in sorted(self.df["domain"].unique()):
            for condition in sorted(self.df["condition"].unique()):
                cell = self.cell(domain, condition)
                if cell.n_items == 0:
                    continue
                results.append({
                    **asdict(cell),
                    "k_agree": [asdict(k) for k in cell.k_agree],
                })
        return {"results": results}

    def write_json(self, out_path: str | Path) -> Path:
        Path(out_path).parent.mkdir(parents=True, exist_ok=True)
        report = self.run_report()
        Path(out_path).write_text(json.dumps(report, indent=2, default=float))
        return Path(out_path)
