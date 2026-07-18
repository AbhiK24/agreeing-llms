"""Command-line entrypoint.

    rho-collapse run --config configs/experiment.yaml [--dry-run] [--limit N]
    rho-collapse report --run runs/rho-v1

The full flow is:
    Loader → Runner (writes responses.jsonl + errors.parquet)
           → RhoEstimator (writes rho_by_domain.json)
           → Reporter (writes report.md)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

from rho_collapse.loader import Loader
from rho_collapse.report import Reporter
from rho_collapse.rho import RhoEstimator
from rho_collapse.runner import ExperimentConfig, Runner


def _cmd_run(args: argparse.Namespace) -> int:
    cfg = ExperimentConfig.from_yaml(args.config)
    if args.dry_run:
        # Restrict to the first N items per domain and only the first condition
        cfg.conditions = cfg.conditions[:1]
        limit = args.limit or 10
        # Discover domains dynamically from the dataset so the CLI stays
        # correct across dataset revisions (v0.1 was science/medicine/code;
        # v0.2 is science/medicine/law).
        counts = Loader(args.data).counts_by_domain()
        items = []
        for domain in sorted(counts):
            items.extend(Loader(args.data).load(domain=domain, limit=limit))
        print(f"[cli] DRY-RUN — {len(items)} items × {len(cfg.conditions)} conditions")
    else:
        items = list(Loader(args.data).load(limit=args.limit))
        print(f"[cli] full run — {len(items)} items × {len(cfg.conditions)} conditions")

    runner = Runner(cfg, out_dir=args.out_dir)
    runner.run(items)

    # Downstream: ρ + report
    return _cmd_report(argparse.Namespace(run=str(runner.out_root)))


def _cmd_report(args: argparse.Namespace) -> int:
    run_dir = Path(args.run)
    errors_path = run_dir / "errors.parquet"
    responses_path = run_dir / "responses.jsonl"
    if not errors_path.exists():
        if not responses_path.exists():
            print(f"[cli] no data in {run_dir} (need responses.jsonl or errors.parquet)",
                  file=sys.stderr)
            return 1
        # Materialize errors.parquet from responses.jsonl on the fly.
        import json
        rows = []
        with responses_path.open() as f:
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
                    "family": r.get("family", ""),
                    "seed": r["seed"],
                    "error": r["error"],
                    "parsed_answer": r.get("parsed_answer"),
                    "num_choices": r.get("num_choices", 0),
                    "gold": r.get("gold"),
                    "temperature": r.get("temperature"),
                })
        pd.DataFrame(rows).to_parquet(errors_path, index=False)
        print(f"[cli] materialized {errors_path} from responses.jsonl")
    df = pd.read_parquet(errors_path)
    est = RhoEstimator(df)
    rho_json = est.write_json(run_dir / "rho_by_domain.json")
    md = Reporter(rho_json).write_markdown(run_dir / "report.md")
    print(f"[cli] wrote {rho_json}")
    print(f"[cli] wrote {md}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="rho-collapse")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_run = sub.add_parser("run", help="Full sweep")
    p_run.add_argument("--config", required=True, help="YAML experiment config")
    p_run.add_argument("--data", default="data/combined.jsonl")
    p_run.add_argument("--out-dir", default="runs")
    p_run.add_argument("--dry-run", action="store_true")
    p_run.add_argument("--limit", type=int, default=None)
    p_run.set_defaults(func=_cmd_run)

    p_rep = sub.add_parser("report", help="Recompute ρ + Markdown from an existing run")
    p_rep.add_argument("--run", required=True, help="path to runs/<run_id>")
    p_rep.set_defaults(func=_cmd_report)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
