"""Config parsing — pinning per-condition temperature override.

The paper's reproducibility claim rests on D2 and D3 running at T = 0
while D1 stays at T > 0 (because D1 at T = 0 is degenerate). If someone
accidentally removes the per-condition override, the whole story falls
apart silently. Pin it.
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from rho_collapse.runner import ExperimentConfig


def _dump(tmp_path: Path, doc: dict) -> Path:
    p = tmp_path / "experiment.yaml"
    p.write_text(yaml.safe_dump(doc))
    return p


def test_per_condition_temperature_overrides_global(tmp_path: Path) -> None:
    cfg_path = _dump(tmp_path, {
        "run_id": "test",
        "temperature": 0.0,
        "models": {"m": {"provider": "openrouter", "model": "x/y", "family": "x"}},
        "conditions": {
            "D1": {
                "temperature": 0.7,
                "committee": ["m", "m"],
                "seeds": [1, 2],
            },
            "D2": {
                "committee": ["m", "m"],
                "seeds": [1, 1],
            },
        },
    })
    cfg = ExperimentConfig.from_yaml(cfg_path)
    assert cfg.temperature == 0.0
    d1 = next(c for c in cfg.conditions if c.name == "D1")
    d2 = next(c for c in cfg.conditions if c.name == "D2")
    assert d1.temperature == 0.7, "D1 override lost"
    assert d2.temperature is None, "D2 should inherit (None = fall back to global)"


def test_shipped_experiment_yaml_uses_correct_temperatures() -> None:
    """The shipped config's D2 and D3 must be reproducible at T = 0."""
    repo_root = Path(__file__).resolve().parents[1]
    yaml_path = repo_root / "configs" / "experiment.yaml"
    if not yaml_path.exists():
        pytest.skip("shipped config not in this checkout")
    cfg = ExperimentConfig.from_yaml(yaml_path)
    assert cfg.temperature == 0.0, "global temperature must be 0 for reproducibility"
    names = {c.name: c for c in cfg.conditions}
    if "D1_same_model" in names:
        # D1 MUST NOT be T = 0 or seeds produce identical outputs.
        d1_temp = names["D1_same_model"].temperature
        assert d1_temp is not None and d1_temp > 0, (
            "D1 must override T > 0; T=0 makes all seeds identical"
        )
    for cross_name in ("D2_cross_family_chinese", "D3_cross_culture"):
        if cross_name in names:
            # None (inherits 0.0) or explicit 0.0 both fine.
            t = names[cross_name].temperature
            effective = cfg.temperature if t is None else t
            assert effective == 0.0, f"{cross_name} must run at T=0"
