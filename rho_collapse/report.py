"""Human-readable Markdown summary of a run.

Consumes `rho_by_domain.json`, emits `report.md`.
"""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path


def _fmt(x, digits: int = 3) -> str:
    try:
        if x is None or x != x:
            return "—"
        return f"{x:.{digits}f}"
    except (TypeError, ValueError):
        return "—"


class Reporter:
    def __init__(self, rho_report_json: str | Path) -> None:
        self.data = json.loads(Path(rho_report_json).read_text())

    def write_markdown(self, out_path: str | Path) -> Path:
        lines: list[str] = []
        lines.append("# ρ-collapse run report")
        lines.append("")
        lines.append(f"_Generated {datetime.utcnow().isoformat(timespec='seconds')}Z_")
        lines.append("")

        # ── Headline table ────────────────────────────────────────────
        lines.append("## Headline: ρ, N_eff, and saturation check")
        lines.append("")
        lines.append(
            "| Domain | Condition | N | Items | Mean acc | ρ (95% CI) | N_eff / N | Saturated? |"
        )
        lines.append("|---|---|---|---|---|---|---|---|")
        for cell in self.data["results"]:
            n = cell["n_agents"]
            n_eff = cell["n_eff"]
            n_eff_frac = f"{_fmt(n_eff, 2)} / {n}"
            rho_str = (
                f"{_fmt(cell['rho_mean'])} "
                f"({_fmt(cell['rho_ci_low'])}, {_fmt(cell['rho_ci_high'])})"
            )
            sat = "⚠ yes" if cell.get("saturation_warning") else "no"
            lines.append(
                f"| {cell['domain']} | {cell['condition']} | {n} | "
                f"{cell['n_items']} | {_fmt(cell.get('mean_agent_accuracy'))} | "
                f"{rho_str} | {n_eff_frac} | {sat} |"
            )
        lines.append("")

        if any(c.get("saturation_warning") for c in self.data["results"]):
            lines.append(
                "> **⚠ Saturation warning.** One or more cells has mean per-agent "
                "accuracy > 0.95. In these cells `ρ ≈ 0` may indicate 'not enough "
                "errors to correlate' rather than genuine agent independence. "
                "Rerun those cells on a harder subset before publishing."
            )
            lines.append("")

        # ── Per-cell breakdown ────────────────────────────────────────
        lines.append("## Per-cell breakdown")
        lines.append("")
        for cell in self.data["results"]:
            lines.append(
                f"### {cell['domain']} × {cell['condition']}"
            )
            lines.append("")
            lines.append(
                f"- **Items scored:** {cell['n_items']}"
                f"  |  **Agents:** {cell['n_agents']}"
                f"  |  **Mean per-agent acc:** {_fmt(cell.get('mean_agent_accuracy'))}"
                f"  |  **ρ:** {_fmt(cell['rho_mean'])}"
                f" (95% CI {_fmt(cell['rho_ci_low'])}, {_fmt(cell['rho_ci_high'])})"
                f"  |  **N_eff:** {_fmt(cell['n_eff'], 2)}"
                f"  |  **C:** {_fmt(cell.get('avg_num_choices'), 1)}"
            )
            lines.append("")
            lines.append("**Per-agent accuracy**")
            lines.append("")
            for a, acc in sorted(cell["per_agent_accuracy"].items()):
                lines.append(f"- `{a}` — {_fmt(acc)}")
            lines.append("")

            if cell.get("k_agree"):
                lines.append(
                    "**Cluster analysis** — for each item, the largest cluster "
                    "of agents that picked the same letter. `Observed` = how often "
                    "that cluster was actually correct; `Naive` = Condorcet posterior "
                    "assuming independence; `Corrected` = same with k rescaled by "
                    "N_eff / N; `Gap` = Naive − Observed (positive = overconfidence)."
                )
                lines.append("")
                lines.append(
                    "| Largest cluster k | Items | Observed correct | Naive posterior "
                    "| Corrected posterior | Overconfidence gap |"
                )
                lines.append("|---|---|---|---|---|---|")
                for ka in cell["k_agree"]:
                    lines.append(
                        f"| {ka['k']} | {ka['n_items']} | "
                        f"{_fmt(ka['observed_correct_rate'])} | "
                        f"{_fmt(ka['naive_posterior'])} | "
                        f"{_fmt(ka['corrected_posterior'])} | "
                        f"{_fmt(ka['overconfidence_gap'])} |"
                    )
                lines.append("")

        Path(out_path).write_text("\n".join(lines))
        return Path(out_path)
