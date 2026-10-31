"""Hidden weapon parts a boss reveals as it transforms (docs/superpowers/specs/2026-10-31-ship-glow-
and-boss-transform-design.md, Part B).

A hidden weapon is a destroyable part (`reveal: K`) on an armoured pod, of one of four kinds:

- `gatling`: a three-barrelled turret that follows the player (aimed shots, bursts, fans);
- `lance`: a laser lance pointing down the screen (lasers);
- `rack`: a box of four missile cells (homing missiles);
- `orb`: a glowing emitter on top (rings, and aimed shots or fans).

Its muzzles are worked out here from its size; the boss view draws its model with the same numbers
(`game/view/bosses/hidden_weapon_shapes.py`). Offsets in px from the boss's centre, X right, Y up
(its nose points down, at -Y), and heights above the playfield.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.boss_kit import bullet, part, volley
from game.config.record import concat, merge, record

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

# Shares of a weapon's radius `r`. The pod: an octagon of `pod` r, `height` r high (unless given).
# The gatling's turret: `turret` r across, three barrels `gap` of the turret apart, `bore` and
# `length` of it. The lance: `lance` r long, `lanceBore` r thick. The rack's cells: `cell` r round,
# `cellX` and `cellY` r off its centre, `cellTop` r above the pod. The orb: `orb` r round, its
# centre `orbTop` r above the pod.
WEAPON_SHAPE = record(
    {
        "pod": 0.9,
        "height": 0.5,
        "turret": 0.62,
        "gap": 0.32,
        "bore": 0.12,
        "length": 0.9,
        "lance": 1.9,
        "lanceBore": 0.2,
        "cell": 0.16,
        "cellX": 0.32,
        "cellY": 0.28,
        "cellTop": 0.3,
        "orb": 0.38,
        "orbTop": 0.42,
    }
)

KINDS = ["gatling", "lance", "rack", "orb", "beam"]

# A giant laser (D-228): `width` px wide (four of the usual), firing `firing` seconds every
# `every` seconds.
BEAM = record({"width": 44, "firing": 2.4, "every": 7})


def pod_height(radius: float, height: Any) -> float:
    """The height of a weapon's pod: `height` when given, else its share of the radius."""
    if height == None:  # noqa: E711
        value: float = radius * WEAPON_SHAPE.height
        return value
    given: float = height
    return given


def gatling_turret(radius: float) -> Any:
    """The gatling turret's sizes (its radius, barrel gap, bore and length)."""
    rt = radius * WEAPON_SHAPE.turret
    return record(
        {
            "radius": rt,
            "gap": rt * WEAPON_SHAPE.gap,
            "bore": rt * WEAPON_SHAPE.bore,
            "length": rt * WEAPON_SHAPE.length,
        }
    )


def weapon_guns(kind: str, at: list[Any], radius: float, height: Any) -> Any:
    """The guns of a weapon of `kind` centred on `at` (see `BossDesign.guns`)."""
    x = at[0]
    y = at[1]
    h = pod_height(radius, height)
    if kind == "gatling":
        t = gatling_turret(radius)
        # The tips of the barrels of `mini_boss_shapes.turret`, aimed down the screen.
        reach = 0.3 * t.radius + t.length + 0.5 * t.radius + 0.6 * t.bore
        lift = h + 0.28 * t.radius
        muzzles = [[x - (i - 1) * t.gap, y - reach, lift] for i in range(3)]
        return record({"gun": muzzles, "turret": [x, y]})
    if kind == "lance":
        tip = radius * WEAPON_SHAPE.lance
        return record({"laser": [[x, y - tip, h * 0.9]]})
    if kind == "rack":
        dx = radius * WEAPON_SHAPE.cellX
        dy = radius * WEAPON_SHAPE.cellY
        top = h + radius * WEAPON_SHAPE.cellTop
        cells = [[x + sx * dx, y + sy * dy, top] for sx in [-1, 1] for sy in [-1, 1]]
        return record({"missile": cells})
    if kind == "orb":
        emitter = [[x, y, h + radius * WEAPON_SHAPE.orbTop]]
        return record({"gun": emitter, "ring": emitter})
    if kind == "beam":
        return record({"laser": [[x, y - radius * WEAPON_SHAPE.lance, h * 0.9]]})
    raise ValueError('Unknown hidden weapon kind "' + kind + '"')


def weapon_volley(kind: str, part_id: str, style: str, first: float) -> Any:
    """What a weapon of `kind` fires, first `first` seconds into a stage: the gatling bursts of 4,
    the lance its laser, the rack 2 homing missiles, the orb rings of 10 (bullets in `style`)."""
    if kind == "gatling":
        return volley.burst(part_id, 2.2, 4, 0.12, bullet(style, 190), first)
    if kind == "lance":
        return volley.laser(part_id, 7.5, 1.4, first)
    if kind == "rack":
        return volley.missiles(part_id, 6, 2, 30, first)
    if kind == "beam":
        return volley.laser(part_id, BEAM.every, BEAM.firing, first, BEAM.width)
    return volley.ring(part_id, 2.6, 10, 13, bullet(style, 175), first)


def hidden_weapon(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
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
    """A hidden weapon part revealed by transformation `reveal`: `part` (shielding the core, a 30 %
    bonus drop), its `guns`, its `look` (kind, radius, pod height and `mount`, for its model) and
    its `volleys` (see `weapon_volley`). `mount`, `[dx, dy, fold]`: the hinge it unfolds about,
    offset in px from its centre, and its turn (radians, about the vertical) folded flat; left
    out, the view hinges it on its inner side, folded back along the hull."""
    look: Any = {"kind": kind, "radius": radius, "height": pod_height(radius, height)}
    if mount != None:  # noqa: E711
        look["mount"] = mount
    return record(
        {
            "part": part(part_id, at, radius, health, {"reveal": reveal, "drop": 0.3}),
            "guns": weapon_guns(kind, at, radius, height),
            "look": look,
            "volleys": [weapon_volley(kind, part_id, style, first)],
        }
    )


def tail_cannon(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    part_id: str, at: list[Any], radius: float, health: float, reveal: int, first: float
) -> Any:
    """A cannon at the end of a rig the boss unfolds at transformation `reveal` (D-228: the
    Scorpion's tail), at `at`, firing a giant laser out behind the boss (+Y: once it has turned
    round, towards the player). Its look is a `beam` on a `rig`: the boss model draws it, and it
    comes out of no armour region."""
    height = radius * 0.6
    return record(
        {
            "part": part(part_id, at, radius, health, {"reveal": reveal, "drop": 0.3}),
            "guns": {"laser": [[at[0], at[1] + radius * 1.2, height]]},
            "look": {"kind": "beam", "radius": radius, "height": height, "rig": True},
            "volleys": [volley.laser(part_id, BEAM.every, BEAM.firing, first, BEAM.width)],
        }
    )


FRAMES = ["wing", "shell", "ring"]


def armour_region(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    region_id: str,
    form: int,
    outline: list[Any],
    frame: str,
    heights: Any = None,
    mirror: bool = True,
) -> Any:
    """An armour region a boss sheds at transformation `form` (docs/superpowers/specs/2026-10-31-
    boss-armour-shedding-design.md): the part of its body inside `outline` (px from its centre,
    X right, Y up; with its mirror image across the centre line when `mirror`), between `heights`
    [low, high] above the playfield (all of them when left out). It bursts off in chunks and leaves
    a dark metal `frame` (`wing`, `shell` or `ring`)."""
    if frame not in FRAMES:
        raise ValueError('Unknown armour frame "' + frame + '"')
    outlines = [outline]
    if mirror:
        n = len(outline)
        outlines.append([[-outline[n - 1 - k][0], outline[n - 1 - k][1]] for k in range(n)])
    return record(
        {
            "id": region_id,
            "form": form,
            "outlines": outlines,
            "frame": frame,
            "heights": heights if heights != None else [-1000, 1000],  # noqa: E711
        }
    )


def region_blasts(region: Any, most: int) -> list[list[float]]:
    """Where a region bursts: `[x, y, radius]` blasts at the middle of each of its outlines and on
    their corners, at most `most` in all, spread round each outline."""
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
    """`design` with its hidden `weapons` (see `hidden_weapon`): their parts after its own, their
    guns and looks, and their volleys (and the `more` volleys given) in every stage, each firing
    once its part is revealed, until it is destroyed; and the `armour` regions it sheds as they
    come out (see `armour_region`)."""
    stats = design.stats
    parts = list(stats.parts)
    guns = merge(design.guns, {})
    looks: Any = record({})
    volleys: list[Any] = []
    for weapon in weapons:
        parts.append(weapon.part)
        guns[weapon.part.id] = weapon.guns
        looks[weapon.part.id] = weapon.look
        volleys.extend(weapon.volleys)
    if more != None:  # noqa: E711
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
        },
    )


def health_of(design: Any, share: float) -> float:
    """A hidden weapon's health: `share` of the boss's sturdiest original part, rounded to 10."""
    most = 0.0
    for p in design.stats.parts:
        most = max(most, p.health)
    return math.floor((most * share) / 10 + 0.5) * 10
