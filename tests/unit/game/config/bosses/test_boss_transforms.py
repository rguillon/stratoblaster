"""The bosses' transformations (docs/superpowers/specs/2026-10-31-ship-glow-and-boss-transform-
design.md, Part B): every boss reveals new weapons as it loses parts, and gets no easier for it."""

from typing import Any

import pytest

from game.config.bosses.hidden_weapons import KINDS
from game.sim.boss_build import default_transforms
from game.sim.boss_kinds import BOSS_DESIGNS

# How much each kind of shot weighs in a boss's fire rate: a bullet 1, a homing missile 2, a laser
# (its sweep across the screen) 8.
WEIGHT = {"missiles": 2, "laser": 8}

IDS = [design["id"] for design in BOSS_DESIGNS]


def _is_final(design: Any) -> bool:
    """Mini boss then final boss of each level, in order (P07-R05)."""
    return BOSS_DESIGNS.index(design) % 2 == 1


def _originals(design: Any) -> list[Any]:
    return [p for p in design.stats.parts if p.get("reveal") is None]


def _hidden(design: Any) -> list[Any]:
    return [p for p in design.stats.parts if p.get("reveal") is not None]


def _volley_rate(shot: Any) -> float:
    shape = shot["shape"]
    kind = shape["kind"]
    count = 1 if kind == "laser" else shape.get("count", 1)
    return WEIGHT.get(kind, 1) * count / shot["every"]


def fire_rate(design: Any, form: int) -> float:
    """The boss's fire rate (weighted shots a second) just after transformation `form` (0: as it
    comes in), the parts that brought it on being the first of its original parts destroyed."""
    thresholds = default_transforms(design) or []
    lost = 0 if form == 0 else thresholds[form - 1]
    originals = _originals(design)
    destroyed = {p["id"] for p in originals[:lost]}
    live = {"core"}
    live.update(p["id"] for p in originals[lost:])
    live.update(p["id"] for p in _hidden(design) if p["reveal"] <= form)
    stages = design.stages
    stage = stages[min(lost, len(stages) - 1)] or []
    total = 0.0
    for shot in stage:
        if shot["from"] not in live:
            continue
        if shot.get("needs") is not None and shot["needs"] not in live:
            continue
        if shot.get("after") is not None and shot["after"] not in destroyed:
            continue
        total += _volley_rate(shot)
    return total


@pytest.mark.parametrize("design", BOSS_DESIGNS, ids=IDS)
def test_a_mini_boss_transforms_once_and_a_final_boss_twice(design: Any) -> None:
    hidden = _hidden(design)
    forms = 2 if _is_final(design) else 1
    assert sorted({p["reveal"] for p in hidden}) == list(range(1, forms + 1))
    thresholds = default_transforms(design)
    assert thresholds is not None
    assert len(thresholds) == forms
    # Every transformation can happen: enough original parts to destroy, in order.
    assert thresholds == sorted(thresholds)
    assert thresholds[0] >= 1
    assert thresholds[-1] <= len(_originals(design))


@pytest.mark.parametrize("design", BOSS_DESIGNS, ids=IDS)
def test_each_transformation_reveals_one_to_three_armed_weapons(design: Any) -> None:
    hidden = _hidden(design)
    for form in {p["reveal"] for p in hidden}:
        assert 1 <= len([p for p in hidden if p["reveal"] == form]) <= 3
    fired = {shot["from"] for stage in design.stages for shot in (stage or [])}
    for p in hidden:
        assert p["id"] in design.guns
        assert design.weapons[p["id"]]["kind"] in KINDS
        assert p["id"] in fired, f"{p['id']} never fires"


@pytest.mark.parametrize("design", BOSS_DESIGNS, ids=IDS)
def test_a_boss_gets_no_easier_as_it_transforms(design: Any) -> None:
    forms = 2 if _is_final(design) else 1
    rates = [fire_rate(design, form) for form in range(forms + 1)]
    assert rates == sorted(rates), rates
    assert rates[-1] > rates[0]
