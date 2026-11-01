# Copyright (c) 2026 Renaud Guillon
"""Hidden weapon parts a boss reveals as it transforms.

Designs: docs/superpowers/specs/2026-10-31-ship-glow-and-boss-transform-design.md, Part B;
docs/superpowers/specs/2026-11-01-boss-weapon-variety-and-shape-shifts-design.md.

A hidden weapon is a destroyable part (`reveal: K`) on a pod, of one of the kinds of
`weapon_kinds` (their sizes, muzzles and volleys). Offsets in px from the boss's centre, X right,
Y up (its nose points down, at -Y), and heights above the playfield.
"""

import math

from game.config.bosses.boss_kit import part, volley
from game.config.bosses.weapon_kinds import (
    BEAM,
    pod_height,
    weapon_guns,
    weapon_launches,
    weapon_volleys,
)
from game.config.record import concat, merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


def hidden_weapon(
    part_id: str,
    kind: str,
    at: list[Any],
    radius: float,
    health: float,
    reveal: int,
    style: str,
    first: float,
    height: Any = None,
    mount: Any = None,
) -> Any:
    """Return a hidden weapon part revealed by transformation `reveal` (BOSS-38).

    `part` (shielding the core, a 30 % bonus drop), its `guns`, its `look` (kind, radius, pod height
    and `mount`, for its model), its `volleys` (see `weapon_volleys`) and its `launches` (a
    hangar's, see `weapon_launches`). `mount`, `[dx, dy, fold]`: the hinge it unfolds about, offset
    in px from its centre, and its turn (radians, about the vertical) folded flat; left out, the
    view hinges it on its inner side, folded back along the hull.
    """
    look: Any = {"kind": kind, "radius": radius, "height": pod_height(radius, height)}
    if mount != None:
        look["mount"] = mount
    return record({
        "part": part(part_id, at, radius, health, {"reveal": reveal, "drop": 0.3}),
        "guns": weapon_guns(kind, at, radius, height),
        "look": look,
        "volleys": weapon_volleys(kind, part_id, style, first),
        "launches": weapon_launches(kind, part_id, first),
    })


def tail_cannon(
    part_id: str, at: list[Any], radius: float, health: float, reveal: int, first: float
) -> Any:
    """Return a cannon at the end of a rig the boss unfolds at transformation `reveal`.

    It sits at the tail (D-228, BOSS-46: the Scorpion's tail): at `at`, it fires a giant laser out
    behind the boss (+Y: once it has turned round, towards the player). Its look is a `beam` on a
    `rig`: the boss model draws it, and it comes out of no armour region.
    """
    height = radius * 0.6
    return record({
        "part": part(part_id, at, radius, health, {"reveal": reveal, "drop": 0.3}),
        "guns": {"laser": [[at[0], at[1] + radius * 1.2, height]]},
        "look": {"kind": "beam", "radius": radius, "height": height, "rig": True},
        "volleys": [volley.laser(part_id, BEAM.every, BEAM.firing, first, BEAM.width)],
        "launches": [],
    })


FRAMES = ["wing", "shell", "ring"]


def armour_region(
    region_id: str,
    form: int,
    outline: list[Any],
    frame: str,
    heights: Any = None,
    mirror: bool = True,
) -> Any:
    """Return an armour region a boss sheds at transformation `form` (BOSS-42).

    Design: docs/superpowers/specs/2026-10-31-boss-armour-shedding-design.md. It is the part of its
    body inside `outline` (px from its centre, X right, Y up; with its mirror image across the
    centre line when `mirror`), between `heights` [low, high] above the playfield (all of them when
    left out). It bursts off in chunks and leaves a dark metal `frame` (`wing`, `shell` or `ring`).
    """
    if frame not in FRAMES:
        raise ValueError('Unknown armour frame "' + frame + '"')
    outlines = [outline]
    if mirror:
        n = len(outline)
        outlines.append([[-outline[n - 1 - k][0], outline[n - 1 - k][1]] for k in range(n)])
    return record({
        "id": region_id,
        "form": form,
        "outlines": outlines,
        "frame": frame,
        "heights": heights if heights != None else [-1000, 1000],
    })


def region_blasts(region: Any, most: int) -> list[list[float]]:
    """Where a region bursts (BOSS-37).

    `[x, y, radius]` blasts at the middle of each of its outlines and on their corners, at most
    `most` in all, spread round each outline.
    """
    result: list[list[float]] = []
    per = max(1, math.floor(most / len(region.outlines)))
    for outline in region.outlines:
        sx = 0.0
        sy = 0.0
        for point in outline:
            sx += point[0]
            sy += point[1]
        cx = sx / len(outline)
        cy = sy / len(outline)
        reach = 0.0
        for point in outline:
            reach = max(reach, math.hypot(point[0] - cx, point[1] - cy))
        radius = max(8, reach * 0.45)
        result.append([cx, cy, radius])
        corners = per - 1
        for k in range(corners):
            point = outline[math.floor((k * len(outline)) / max(1, corners))]
            result.append([(point[0] + cx) / 2, (point[1] + cy) / 2, radius * 0.7])
    return result[:most]


def with_weapons(design: Any, weapons: list[Any], armour: list[Any], more: Any = None) -> Any:
    """`design` with its hidden `weapons` (see `hidden_weapon`).

    Their parts after its own, their guns and looks, their volleys (and the `more` volleys given) in
    every stage and their launches with its own, each firing once its part is revealed, until it is
    destroyed; and the `armour` regions it sheds as they come out (see `armour_region`). A mini
    boss's transformation reveals a pair, a final boss's two transformations a pair each (BOSS-35).
    """
    stats = design.stats
    parts = list(stats.parts)
    guns = merge(design.guns, {})
    looks: Any = record({})
    volleys: list[Any] = []
    launches: list[Any] = list(design.launches) if design.launches != None else []
    for weapon in weapons:
        parts.append(weapon.part)
        guns[weapon.part.id] = weapon.guns
        looks[weapon.part.id] = weapon.look
        volleys.extend(weapon.volleys)
        launches.extend(weapon.launches)
    if more != None:
        volleys.extend(more)
    stages = [concat(stage, volleys) for stage in design.stages]
    return merge(
        design,
        {
            "stats": merge(stats, {"parts": parts}),
            "guns": guns,
            "weapons": looks,
            "stages": stages,
            "armour": armour,
            "launches": launches,
        },
    )


def health_of(design: Any, share: float) -> float:
    """Return a hidden weapon's health: `share` of the boss's sturdiest original part.

    Rounded to 10.
    """
    most = 0.0
    for p in design.stats.parts:
        most = max(most, p.health)
    return math.floor((most * share) / 10 + 0.5) * 10
