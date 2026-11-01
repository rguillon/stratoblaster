"""The bosses' transformations (docs/superpowers/specs/2026-10-31-ship-glow-and-boss-transform-
design.md, Part B): every boss reveals new weapons as it loses parts, and gets no easier for it."""

from typing import Any

import pytest

from game.config.bosses.hidden_weapons import FRAMES, armour_region, region_blasts
from game.config.bosses.moving_regions import (
    drawn_spot,
    is_moving,
    motion_value,
    move_point,
    ridden_region,
)
from game.config.bosses.weapon_kinds import KINDS
from game.sim.boss_build import default_transforms
from game.sim.boss_kinds import BOSS_DESIGNS
from render.geometry.shatter import inside

# How much each kind of shot weighs in a boss's fire rate: a bullet 1, a homing missile 2, a laser
# (its sweep across the screen) 8; an enemy a part launches (a hangar's Gnat, D-229) 2.
WEIGHT = {"missiles": 2, "laser": 8}
LAUNCHED = 2

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
    originals = _originals(design)
    named = design.get("transformParts")
    if named:
        # It transforms once the parts named for each transformation are destroyed (D-228).
        destroyed = {i for ids in named[:form] for i in ids}
    else:
        thresholds = default_transforms(design) or []
        lost = 0 if form == 0 else thresholds[form - 1]
        destroyed = {p["id"] for p in originals[:lost]}
    lost = len(destroyed)
    live = {"core"}
    live.update(
        p["id"]
        for p in originals
        if p["id"] not in destroyed and (p.get("retire") is None or p["retire"] > form)
    )
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
    for launch in design.get("launches") or []:
        if launch["from"] in live:
            total += LAUNCHED * launch["count"] / launch["every"]
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
    fired.update(launch["from"] for launch in design.get("launches") or [])
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
        # A moving region may leave no frame (D-230).
        assert region.frame in FRAMES or (is_moving(region) and region.frame is None)
        assert all(len(outline) >= 3 for outline in region.outlines)


@pytest.mark.parametrize("design", BOSS_DESIGNS, ids=IDS)
def test_every_hidden_weapon_unfolds_from_a_region_its_transformation_sheds(design: Any) -> None:
    for p in _hidden(design):
        if design.weapons[p["id"]].get("rig"):
            # At the end of a rig it unfolds (D-228: the Scorpion's tail), not in a region.
            continue
        if ridden_region(design, p) is not None:
            # On a moving region's piece, where it ends up (D-230).
            continue
        # Where armour bursts off, or where a moving piece was drawn (it leaves the spot open); a
        # centre weapon may sit on the seam between two mirrored pieces.
        regions = [r for r in design.armour if r.form == p["reveal"]]
        assert any(
            inside(o, p["x"] + dx, p["y"]) for r in regions for o in r.outlines for dx in [0, 0.5]
        ), p["id"]


def _rest_outline(region: Any) -> list[list[float]]:
    rest = motion_value(region.motion, 0)
    return [move_point(region.motion, rest, [x, y, 0])[:2] for x, y in region.outlines[0]]


@pytest.mark.parametrize("design", BOSS_DESIGNS, ids=IDS)
def test_no_part_the_player_can_hit_stands_on_a_piece_as_it_moves(design: Any) -> None:
    # D-230: positions in core/ never move; a part on a moving piece must be gone by then.
    named = design.get("transformParts") or []
    for region in design.armour:
        if not is_moving(region):
            continue
        form = region.form
        gone = {i for ids in named[:form] for i in ids}
        outline = _rest_outline(region)
        for p in design.stats.parts:
            reveal = p.get("reveal")
            if reveal is not None and reveal >= form:
                continue
            retire = p.get("retire")
            if (retire is not None and retire <= form) or p["id"] in gone:
                continue
            assert not inside(outline, p["x"], p["y"]), f"{p['id']} on {region.id}"


@pytest.mark.parametrize("design", BOSS_DESIGNS, ids=IDS)
def test_a_weapon_riding_a_moving_piece_ends_up_on_it(design: Any) -> None:
    for p in _hidden(design):
        region = ridden_region(design, p)
        if region is None:
            continue
        look = design.weapons[p["id"]]
        spot = drawn_spot(region, [p["x"], p["y"], look["height"]])
        # Its whole pod, not only its centre.
        r = p["radius"] * 0.6
        for dx, dy in [(0, 0), (r, 0), (-r, 0), (0, r), (0, -r)]:
            assert inside(region.outlines[0], spot[0] + dx, spot[1] + dy), p["id"]


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


# Boss weapon variety (D-229; docs/superpowers/specs/2026-11-01-boss-weapon-variety-and-shape-shifts-
# design.md): the hidden weapons spread over the kinds.


def _kind(design: Any, part_id: str) -> str:
    kind: str = design.weapons[part_id]["kind"]
    return kind


def _world(design: Any) -> int:
    """Ten bosses a world, a mini then a final boss for each of its five levels (P07-R05)."""
    return BOSS_DESIGNS.index(design) // 10 + 1


def _all_weapons() -> list[tuple[Any, Any]]:
    return [(d, p) for d in BOSS_DESIGNS for p in _hidden(d) if _kind(d, p["id"]) != "beam"]


def test_no_kind_of_weapon_is_more_than_a_fifth_of_them() -> None:
    weapons = _all_weapons()
    counts: dict[str, int] = {}
    for d, p in weapons:
        counts[_kind(d, p["id"])] = counts.get(_kind(d, p["id"]), 0) + 1
    assert max(counts.values()) <= len(weapons) * 0.2, counts
    assert set(counts) == set(KINDS) - {"beam"}


def test_every_world_reveals_at_least_six_kinds_of_weapon() -> None:
    for world in range(1, 5):
        kinds = {_kind(d, p["id"]) for d, p in _all_weapons() if _world(d) == world}
        assert len(kinds) >= 6, (world, kinds)


@pytest.mark.parametrize("design", BOSS_DESIGNS, ids=IDS)
def test_a_final_boss_reveals_new_kinds_at_its_second_transformation(design: Any) -> None:
    hidden = _hidden(design)
    first = {_kind(design, p["id"]) for p in hidden if p["reveal"] == 1}
    second = {_kind(design, p["id"]) for p in hidden if p["reveal"] == 2}
    assert not first & second


def test_hangars_are_few_and_on_final_bosses_only() -> None:
    hangars = [(d, p) for d, p in _all_weapons() if _kind(d, p["id"]) == "hangar"]
    assert hangars
    assert all(_is_final(d) for d, _ in hangars)
    for world in range(1, 5):
        assert len([d for d, _ in hangars if _world(d) == world]) <= 1


def test_at_least_ten_bosses_reveal_a_weapon_on_their_centre_line() -> None:
    centred = {d["id"] for d, p in _all_weapons() if p["x"] == 0}
    assert len(centred) >= 10, centred


def test_eight_bosses_change_shape_as_they_transform() -> None:
    # D-230: two a world, each moving its own way.
    shifting = [d for d in BOSS_DESIGNS if any(is_moving(r) for r in d.armour)]
    assert len(shifting) == 8
    for world in range(1, 5):
        assert len([d for d in shifting if _world(d) == world]) == 2
