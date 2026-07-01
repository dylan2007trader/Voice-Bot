"""Load patient scenarios from scenarios/scenarios.yaml."""

from __future__ import annotations

import os
import yaml

_SCENARIOS_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "scenarios", "scenarios.yaml"
)


def load_scenarios() -> list[dict]:
    with open(_SCENARIOS_PATH, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_scenario(scenario_id: str) -> dict:
    for s in load_scenarios():
        if s["id"] == scenario_id:
            return s
    raise SystemExit(f"No scenario with id '{scenario_id}'. Run `list` to see them all.")
