"""The bosses' transformations (docs/superpowers/specs/2026-10-31-ship-glow-and-boss-transform-
design.md, Part B): every boss reveals new weapons as it loses parts, and gets no easier for it."""

from typing import Any

import pytest

from game.config.bosses.hidden_weapons import FRAMES, armour_region, region_blasts
from game.config.bosses.weapon_kinds import KINDS
from game.sim.boss_build import default_transforms
from game.sim.boss_kinds import BOSS_DESIGNS
from render.geometry.shatter import inside

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
    live.update(p["id"] for p in originals[lost:] if p.get("retire") is None or p["retire"] > form)
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


@pytest.mark.parametrize("design", BOSS_DESIGNS, ids=IDS)
def test_each_transformation_sheds_an_armour_region(design: Any) -> None:
    # docs/superpowers/specs/2026-10-31-boss-armour-shedding-design.md: it breaks open.
    forms = {p["reveal"] for p in _hidden(design)}
    shed = {region.form for region in design.armour}
    assert shed == forms
    for region in design.armour:
        assert region.frame in FRAMES
        assert all(len(outline) >= 3 for outline in region.outlines)


@pytest.mark.parametrize("design", BOSS_DESIGNS, ids=IDS)
def test_every_hidden_weapon_unfolds_from_a_region_its_transformation_sheds(design: Any) -> None:
    for p in _hidden(design):
        if design.weapons[p["id"]].get("rig"):
            # At the end of a rig it unfolds (D-228: the Scorpion's tail), not in a region.
            continue
        regions = [r for r in design.armour if r.form == p["reveal"]]
        assert any(inside(o, p["x"], p["y"]) for r in regions for o in r.outlines), p["id"]


def test_a_region_is_mirrored_across_the_centre_line_unless_asked_not_to() -> None:
    region = armour_region("wings", 1, [[10, 0], [30, 0], [30, 20]], "wing")
    assert region.outlines[1] == [[-30, 20], [-30, 0], [-10, 0]]
    assert region.heights == [-1000, 1000]
    single = armour_region("back", 2, [[-5, 0], [5, 0], [0, 9]], "shell", [0, 4], False)
    assert len(single.outlines) == 1 and single.heights == [0, 4]
    with pytest.raises(ValueError, match="Unknown armour frame"):
        armour_region("x", 1, [[0, 0], [1, 0], [0, 1]], "lattice")


def test_a_region_bursts_in_blasts_spread_over_its_outlines() -> None:
    region = armour_region("wings", 1, [[10, 0], [30, 0], [30, 20], [10, 20]], "wing")
    blasts = region_blasts(region, 5)
    assert 2 <= len(blasts) <= 5
    # One on each side of the centre line.
    assert any(b[0] > 0 for b in blasts) and any(b[0] < 0 for b in blasts)
    assert blasts[0][:2] == [20, 10]
    assert blasts[0][2] >= 8
    assert all(b[2] > 0 for b in blasts)
