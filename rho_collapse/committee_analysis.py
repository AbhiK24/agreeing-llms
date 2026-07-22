"""Committee-selection analysis: enumerate → generalization test → algorithm eval.

Runs entirely on the frozen paper-v1 T=0 sweep (no API calls):

    python -m rho_collapse.committee_analysis \
        --responses paper-v1/raw/responses.pre-final-filter.jsonl.bak \
        --out runs/committee-v1

Produces:
- committees.csv       every committee of size 3-8 × domain, with p̄, ρ̄,
                       N_eff, corrected-evidence score, plurality accuracy
- selection_eval.json  split-half + leave-one-domain-out strategy comparison
- report.md            human-readable findings
"""
from __future__ import annotations

import argparse
import json
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd

from .committee import (
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
from .rho import RhoEstimator


# ── pure helpers (unit-tested) ──────────────────────────────────────────────

def enumerate_committees(
    panel: Panel, sizes: range | list[int]
) -> pd.DataFrame:
    """Every committee of the given sizes, with all committee-level stats."""
    acc = per_model_accuracy(panel)
    rho_df = pairwise_rho(error_frame(panel))
    rows = []
    for size in sizes:
        for combo in combinations(panel.models, size):
            members = list(combo)
            rho = mean_pairwise_rho(rho_df, members)
            neff = RhoEstimator.n_eff(size, rho)
            plur, n_items = plurality_accuracy(panel, members, mode="abstain")
            strict, n_strict = plurality_accuracy(panel, members, mode="strict")
            rows.append({
                "domain": panel.domain,
                "size": size,
                "members": "+".join(members),
                "mean_acc": float(acc[members].mean()),
                "mean_rho": rho,
                "n_eff": neff,
                "evidence": evidence_score(members, acc, rho_df,
                                           panel.modal_num_choices),
                "plurality_acc": plur,
                "n_items": n_items,
                "strict_acc": strict,
                "n_items_strict": n_strict,
            })
    return pd.DataFrame(rows)


def regret_matrix(tables: dict[str, pd.DataFrame], size: int) -> pd.DataFrame:
    """Deploy each domain's best size-k committee on every other domain.

    Cell (train, test) = accuracy the test domain loses by importing the
    train domain's winner instead of its own:
        regret = best_plurality(test) − plurality(test, best_committee(train))
    Diagonal is 0 by construction.
    """
    domains = sorted(tables)
    best = {
        d: tables[d][tables[d]["size"] == size]
             .sort_values("plurality_acc", ascending=False)
             .iloc[0]["members"]
        for d in domains
    }
    out = pd.DataFrame(index=domains, columns=domains, dtype=float)
    for train in domains:
        for test in domains:
            t = tables[test][tables[test]["size"] == size].set_index("members")
            out.loc[train, test] = float(
                t["plurality_acc"].max() - t.loc[best[train], "plurality_acc"]
            )
    return out


def pooled_stats(panels: list[Panel]) -> tuple[pd.Series, pd.DataFrame]:
    """Accuracy and pairwise ρ over the concatenation of several panels."""
    errors = pd.concat([error_frame(p) for p in panels])
    return 1.0 - errors.mean(), pairwise_rho(errors)


def select_by_strategy(
    strategy: str,
    cal_acc: pd.Series,
    cal_rho: pd.DataFrame,
    num_choices: int,
    size: int,
    cal_panel: Panel | None = None,
) -> list[str]:
    """The four selection strategies compared in the paper.

    rho_greedy      constrained greedy on corrected evidence (the algorithm)
    rho_exhaustive  argmax corrected evidence over all size-k committees
    top_acc         the k highest-accuracy models (what practitioners do)
    empirical       best plurality accuracy ON THE CALIBRATION SET
                    (overfit ceiling; needs cal_panel)
    """
    pool = list(cal_acc.index)
    if strategy == "rho_greedy":
        return greedy_select(pool, cal_acc, cal_rho, num_choices, n_max=size).members
    if strategy == "rho_exhaustive":
        return exhaustive_select(pool, cal_acc, cal_rho, num_choices, size).members
    if strategy == "top_acc":
        return list(cal_acc.sort_values(ascending=False).index[:size])
    if strategy == "empirical":
        assert cal_panel is not None
        best, best_acc = None, -1.0
        for combo in combinations(pool, size):
            a, _ = plurality_accuracy(cal_panel, list(combo), mode="abstain")
            if a > best_acc:
                best, best_acc = list(combo), a
        return best
    raise ValueError(f"unknown strategy: {strategy!r}")


STRATEGIES = ("rho_greedy", "rho_exhaustive", "top_acc", "empirical")


def split_half_eval(
    panel: Panel, size: int, n_splits: int = 20, seed: int = 42
) -> dict[str, dict]:
    """Estimate on a random half of items, deploy on the other half."""
    rng = np.random.default_rng(seed)
    items = panel.answers.index.to_numpy()
    scores: dict[str, list[float]] = {s: [] for s in STRATEGIES}
    picks: dict[str, list[str]] = {s: [] for s in STRATEGIES}
    random_scores: list[float] = []

    for _ in range(n_splits):
        perm = rng.permutation(len(items))
        cal_idx, test_idx = perm[: len(items) // 2], perm[len(items) // 2:]
        cal = Panel(panel.domain, panel.answers.iloc[cal_idx],
                    panel.gold.iloc[cal_idx], panel.modal_num_choices)
        test = Panel(panel.domain, panel.answers.iloc[test_idx],
                     panel.gold.iloc[test_idx], panel.modal_num_choices)
        cal_acc = per_model_accuracy(cal)
        cal_rho = pairwise_rho(error_frame(cal))
        for strat in STRATEGIES:
            members = select_by_strategy(
                strat, cal_acc, cal_rho, panel.modal_num_choices, size,
                cal_panel=cal,
            )
            a, _ = plurality_accuracy(test, members, mode="abstain")
            scores[strat].append(a)
            picks[strat].append("+".join(sorted(members)))
        # random baseline: one uniformly drawn committee per split
        rand = list(rng.choice(panel.models, size=size, replace=False))
        a, _ = plurality_accuracy(test, rand, mode="abstain")
        random_scores.append(a)

    def _summ(vals: list[float]) -> dict:
        return {"mean": float(np.mean(vals)), "std": float(np.std(vals))}

    out = {s: {**_summ(scores[s]),
               "modal_committee": pd.Series(picks[s]).mode().iloc[0]}
           for s in STRATEGIES}
    out["random"] = _summ(random_scores)
    return out


def lodo_eval(panels: dict[str, Panel], size: int) -> dict[str, dict]:
    """Leave-one-domain-out: calibrate on two domains, deploy on the third."""
    out: dict[str, dict] = {}
    for held_out in sorted(panels):
        cal_panels = [p for d, p in panels.items() if d != held_out]
        cal_acc, cal_rho = pooled_stats(cal_panels)
        test = panels[held_out]
        # pooled calibration panel for the empirical strategy
        pooled_panel = Panel(
            "pooled",
            pd.concat([p.answers for p in cal_panels]),
            pd.concat([p.gold for p in cal_panels]),
            test.modal_num_choices,
        )
        res: dict[str, dict] = {}
        for strat in STRATEGIES:
            members = select_by_strategy(
                strat, cal_acc, cal_rho, test.modal_num_choices, size,
                cal_panel=pooled_panel,
            )
            a, n = plurality_accuracy(test, members, mode="abstain")
            res[strat] = {"members": sorted(members), "accuracy": a, "n_items": n}
        # reference points on the held-out domain itself
        table = enumerate_committees(test, [size])
        res["oracle"] = {
            "members": sorted(table.sort_values("plurality_acc", ascending=False)
                              .iloc[0]["members"].split("+")),
            "accuracy": float(table["plurality_acc"].max()),
        }
        res["random_expectation"] = {"accuracy": float(table["plurality_acc"].mean())}
        out[held_out] = res
    return out


def seed_committee_plurality(
    rows: list[dict], condition: str = "D1_same_model"
) -> dict[str, dict]:
    """Abstention-tolerant plurality of a multi-seed committee, per domain.

    Scores over EVERY item of the domain (items where no seed produced a
    definite answer count as wrong), so the numbers are comparable with
    the T=0 panel committees — unlike paper-v1's committee-complete
    filter, which inflates accuracy by dropping hard items (L0).
    """
    votes: dict[tuple[str, str], dict] = {}
    gold: dict[str, str] = {}
    all_items: dict[str, set] = {}
    toks: dict[str, list[float]] = {}
    n_seeds: dict[str, set] = {}
    for r in rows:
        all_items.setdefault(r["domain"], set()).add(r["item_id"])
        if r.get("gold"):
            gold.setdefault(r["item_id"], r["gold"])
        if r.get("condition") != condition:
            continue
        n_seeds.setdefault(r["domain"], set()).add(r.get("seed"))
        if r.get("tokens_out"):
            toks.setdefault(r["domain"], []).append(float(r["tokens_out"]))
        if r.get("parsed_answer"):
            votes.setdefault((r["domain"], r["item_id"]), {})[r.get("seed")] = \
                r["parsed_answer"]

    out: dict[str, dict] = {}
    for domain, items in all_items.items():
        total = 0.0
        for item in items:
            seat = votes.get((domain, item))
            if not seat:
                continue
            counts = pd.Series(list(seat.values())).value_counts()
            winners = counts[counts == counts.max()].index
            if gold.get(item) in winners:
                total += 1.0 / len(winners)
        k = len(n_seeds.get(domain, set()))
        out[domain] = {
            "accuracy": total / len(items) if items else float("nan"),
            "n_items": len(items),
            "n_seeds": k,
            "cost": k * float(np.mean(toks[domain])) if toks.get(domain) else float("nan"),
        }
    return out


def head_to_head(
    panels: dict[str, Panel],
    rows: list[dict],
    costs: pd.Series,
) -> dict[str, dict]:
    """The final-act table: the protocol vs what practitioners do today."""
    d1 = seed_committee_plurality(rows)
    out: dict[str, dict] = {}
    for domain, panel in panels.items():
        acc = per_model_accuracy(panel)
        rho_df = pairwise_rho(error_frame(panel))
        proto = protocol_select(acc, rho_df, costs,
                                num_choices=panel.modal_num_choices)
        top5 = list(acc.sort_values(ascending=False).index[:5])
        entries = {
            "protocol": proto.members,
            "top5_acc": top5,
            "full_pool": panel.models,
        }
        res: dict[str, dict] = {}
        for name, members in entries.items():
            a, _ = plurality_accuracy(panel, members, mode="abstain")
            res[name] = {
                "members": sorted(members),
                "accuracy": a,
                "cost": float(costs[members].sum()),
            }
        res["protocol"]["trace"] = proto.trace
        res["same_model_5seeds"] = d1[domain]
        out[domain] = res
    return out


# ── report ──────────────────────────────────────────────────────────────────

def _fmt_committee(members: str | list[str]) -> str:
    if isinstance(members, str):
        members = members.split("+")
    return ", ".join(sorted(members))


def write_report(
    out_dir: Path,
    panels: dict[str, Panel],
    tables: dict[str, pd.DataFrame],
    regret: pd.DataFrame,
    split_half: dict[str, dict],
    lodo: dict[str, dict],
    costs: pd.Series,
    constrained_demo: dict,
    size: int,
    h2h: dict[str, dict] | None = None,
    rank_transfer: dict | None = None,
) -> Path:
    lines: list[str] = []
    w = lines.append
    w("# Committee selection from the paper-v1 T=0 sweep")
    w("")
    w("All numbers derive from `paper-v1/raw/responses.pre-final-filter.jsonl.bak`")
    w("(T=0 rows only; D2 row preferred over D3 for the two duplicated models).")
    w("Plurality accuracy uses abstention-tolerant voting over the full item")
    w("set, so every committee is scored on identical items.")
    w("")

    w("## Per-model accuracy and cost (T=0 pool)")
    w("")
    w("| Model | " + " | ".join(sorted(panels)) + " | mean tokens_out |")
    w("|---|" + "---|" * (len(panels) + 1))
    accs = {d: per_model_accuracy(p) for d, p in panels.items()}
    for m in sorted(panels[sorted(panels)[0]].models):
        cells = " | ".join(f"{accs[d].get(m, float('nan')):.3f}" for d in sorted(panels))
        w(f"| {m} | {cells} | {costs.get(m, float('nan')):.0f} |")
    w("")

    w(f"## Best size-{size} committee per domain (plurality accuracy)")
    w("")
    w("| Domain | Committee | Plurality acc | Mean acc | ρ̄ | N_eff |")
    w("|---|---|---|---|---|---|")
    for d in sorted(tables):
        t = tables[d][tables[d]["size"] == size].sort_values(
            "plurality_acc", ascending=False)
        top = t.iloc[0]
        w(f"| {d} | {_fmt_committee(top['members'])} | {top['plurality_acc']:.3f} "
          f"| {top['mean_acc']:.3f} | {top['mean_rho']:.3f} | {top['n_eff']:.2f} |")
    w("")

    w("## Generalization regret (deploy row-domain's winner on column-domain)")
    w("")
    w("Accuracy given up versus the column domain's own best committee:")
    w("")
    w("| train \\ test | " + " | ".join(regret.columns) + " |")
    w("|---|" + "---|" * len(regret.columns))
    for train in regret.index:
        cells = " | ".join(f"{regret.loc[train, c]:.3f}" for c in regret.columns)
        w(f"| {train} | {cells} |")
    w("")

    w(f"## Within-domain split-half (size {size}, 20 splits)")
    w("")
    w("Calibrate on half the items, deploy on the other half:")
    w("")
    w("| Domain | " + " | ".join(list(STRATEGIES) + ["random"]) + " |")
    w("|---|" + "---|" * (len(STRATEGIES) + 1))
    for d in sorted(split_half):
        r = split_half[d]
        cells = " | ".join(
            f"{r[s]['mean']:.3f} ± {r[s]['std']:.3f}"
            for s in list(STRATEGIES) + ["random"]
        )
        w(f"| {d} | {cells} |")
    w("")

    w(f"## Leave-one-domain-out (size {size})")
    w("")
    w("Calibrate p and ρ on the other two domains, deploy on the held-out one:")
    w("")
    w("| Held-out | " + " | ".join(list(STRATEGIES) + ["oracle", "random E"]) + " |")
    w("|---|" + "---|" * (len(STRATEGIES) + 2))
    for d in sorted(lodo):
        r = lodo[d]
        cells = " | ".join(f"{r[s]['accuracy']:.3f}" for s in STRATEGIES)
        w(f"| {d} | {cells} | {r['oracle']['accuracy']:.3f} "
          f"| {r['random_expectation']['accuracy']:.3f} |")
    w("")
    w("Committees chosen (LODO):")
    w("")
    for d in sorted(lodo):
        for s in STRATEGIES:
            w(f"- **{d} / {s}**: {_fmt_committee(lodo[d][s]['members'])}")
    w("")

    if h2h:
        w("## Head-to-head: the protocol vs current practice")
        w("")
        w("`same_model_5seeds` is the D1 condition (5 seeds of DeepSeek V4 at")
        w("T=0.7) rescored with abstention voting over all items, so it is")
        w("directly comparable. Cost = mean output tokens per item.")
        w("")
        w("| Domain | Strategy | Committee | Accuracy | Cost (tok/item) |")
        w("|---|---|---|---|---|")
        for d in sorted(h2h):
            r = h2h[d]
            for s in ("protocol", "same_model_5seeds", "top5_acc", "full_pool"):
                e = r[s]
                mem = _fmt_committee(e["members"]) if "members" in e \
                    else f"deepseek_v4 × {e['n_seeds']} seeds"
                w(f"| {d} | {s} | {mem} | {e['accuracy']:.3f} | {e['cost']:.0f} |")
        w("")

    if rank_transfer:
        w("## Rank transfer across domains (Spearman over size-5 committees)")
        w("")
        w("Neither accuracy ranks nor ρ ranks transfer — committee choice is")
        w("domain-specific all the way down:")
        w("")
        w("| Domain pair | plurality-acc rank corr | ρ̄ rank corr |")
        w("|---|---|---|")
        for pair, v in rank_transfer.items():
            w(f"| {pair} | {v['acc_spearman']:+.3f} | {v['rho_spearman']:+.3f} |")
        w("")

    w("## Constrained selection demo (cost budget)")
    w("")
    w(f"Cost proxy: mean tokens_out per call. Budget = "
      f"{constrained_demo['budget']:.0f} tokens across the committee.")
    w("")
    for d, r in sorted(constrained_demo["per_domain"].items()):
        w(f"- **{d}**: unconstrained → {_fmt_committee(r['unconstrained'])} "
          f"(cost {r['unconstrained_cost']:.0f}); "
          f"budgeted → {_fmt_committee(r['budgeted'])} "
          f"(cost {r['budgeted_cost']:.0f}, "
          f"plurality {r['budgeted_acc']:.3f} vs {r['unconstrained_acc']:.3f})")
    w("")

    path = out_dir / "report.md"
    path.write_text("\n".join(lines))
    return path


# ── main ────────────────────────────────────────────────────────────────────

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--responses", required=True,
                    help="raw responses JSONL (pre-final-filter backup)")
    ap.add_argument("--out", required=True, help="output directory")
    ap.add_argument("--size", type=int, default=5, help="headline committee size")
    ap.add_argument("--splits", type=int, default=20)
    args = ap.parse_args(argv)

    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    rows = [json.loads(l) for l in open(args.responses)]
    panels = build_panels(rows)
    print(f"panels: { {d: p.n_items for d, p in panels.items()} }")

    # cost proxy: mean output tokens per call at T=0
    t0 = pd.DataFrame(
        [{"m": r["agent_name"], "tok": r.get("tokens_out")}
         for r in rows if r.get("temperature") == 0.0 and r.get("tokens_out")]
    )
    costs = t0.groupby("m")["tok"].mean()

    sizes = range(3, len(panels[sorted(panels)[0]].models) + 1)
    tables = {d: enumerate_committees(p, sizes) for d, p in panels.items()}
    pd.concat(tables.values()).to_csv(out_dir / "committees.csv", index=False)
    print("enumeration done")

    regret = regret_matrix(tables, args.size)
    split_half = {d: split_half_eval(p, args.size, n_splits=args.splits)
                  for d, p in panels.items()}
    print("split-half done")
    lodo = lodo_eval(panels, args.size)
    print("LODO done")

    # predictive validity of the evidence score
    spearman = {
        d: float(t[t["size"] == args.size][["evidence", "plurality_acc"]]
                 .corr(method="spearman").iloc[0, 1])
        for d, t in tables.items()
    }

    # rank transfer across domains: does anything generalize?
    s5 = pd.concat(tables.values())
    s5 = s5[s5["size"] == args.size]
    piv_acc = s5.pivot(index="members", columns="domain", values="plurality_acc")
    piv_rho = s5.pivot(index="members", columns="domain", values="mean_rho")
    rank_transfer = {}
    for a, b in combinations(sorted(panels), 2):
        rank_transfer[f"{a} vs {b}"] = {
            "acc_spearman": float(piv_acc[[a, b]].corr(method="spearman").iloc[0, 1]),
            "rho_spearman": float(piv_rho[[a, b]].corr(method="spearman").iloc[0, 1]),
        }

    h2h = head_to_head(panels, rows, costs)

    # constrained demo: budget = 60% of the unconstrained pick's cost
    demo: dict = {"per_domain": {}}
    budget = None
    for d, p in sorted(panels.items()):
        acc = per_model_accuracy(p)
        rho_df = pairwise_rho(error_frame(p))
        unc = greedy_select(p.models, acc, rho_df, p.modal_num_choices,
                            n_max=args.size)
        unc_cost = float(costs[unc.members].sum())
        if budget is None:
            budget = 0.6 * unc_cost
            demo["budget"] = budget
        bud = greedy_select(p.models, acc, rho_df, p.modal_num_choices,
                            n_max=args.size, costs=costs, budget=budget)
        demo["per_domain"][d] = {
            "unconstrained": unc.members,
            "unconstrained_cost": unc_cost,
            "unconstrained_acc": plurality_accuracy(p, unc.members)[0],
            "budgeted": bud.members,
            "budgeted_cost": float(costs[bud.members].sum()),
            "budgeted_acc": plurality_accuracy(p, bud.members)[0],
        }

    (out_dir / "selection_eval.json").write_text(json.dumps({
        "split_half": split_half,
        "lodo": lodo,
        "regret": {r: regret.loc[r].to_dict() for r in regret.index},
        "evidence_spearman": spearman,
        "rank_transfer": rank_transfer,
        "head_to_head": h2h,
        "constrained_demo": demo,
    }, indent=2, default=float))

    report = write_report(out_dir, panels, tables, regret, split_half, lodo,
                          costs, demo, args.size, h2h=h2h,
                          rank_transfer=rank_transfer)
    print(f"report: {report}")
    print(f"evidence-score Spearman vs plurality acc: {spearman}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
