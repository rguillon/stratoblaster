"""Moving regions (D-230, BOSS-45; docs/superpowers/specs/2026-11-01-boss-weapon-variety-and-
shape-shifts-design.md, Part B): armour regions whose piece stays on the boss and moves into a new
pose as it transforms (a wing swings forward, a hull splits and slides apart), instead of bursting
off.

A region's piece is cut out of the core's drawing as any armour region's is; its `motion` takes it
from its rest pose to its end pose. The drawn geometry is the pose at angle 0 or offset 0: a piece
may rest folded (a rest angle other than 0) and unfold to the model as drawn, or rest as drawn and
move away from it.

Px from the boss's centre, X right, Y up the screen (its nose points down, at -Y), Z height above
the playfield; angles in degrees, turning by the right-hand rule about the axis: `up` (+Z, counter-
clockwise seen from above), `along` (+Y, the boss's length) or `across` (+X).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.hidden_weapons import FRAMES, armour_region
from game.config.record import merge, record

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

AXES = ["up", "along", "across"]
DEG = math.pi / 180


def swing(pivot: list[float], axis: str, angles: list[float]) -> Any:
    """A swing about `axis` (`up`, `along` or `across`) through `pivot` `[x, y, z]`, from
    `angles[0]` (at rest) to `angles[1]` (at the end), in degrees from the pose as drawn."""
    if axis not in AXES:
        raise ValueError('Unknown swing axis "' + axis + '"')
    return record({"kind": "swing", "pivot": pivot, "axis": axis, "angles": angles})


def slide(offsets: list[list[float]]) -> Any:
    """A slide from `offsets[0]` (at rest) to `offsets[1]` (at the end), each `[dx, dy, dz]` px from
    the pose as drawn."""
    return record({"kind": "slide", "offsets": offsets})


def mirrored_motion(motion: Any) -> Any:
    """`motion` mirrored across the centre line (X negated): a swing about `up` or `along` turns
    the other way."""
    if motion.kind == "slide":
        return slide([[-o[0], o[1], o[2]] for o in motion.offsets])
    p = motion.pivot
    turn = 1 if motion.axis == "across" else -1
    return swing([-p[0], p[1], p[2]], motion.axis, [a * turn for a in motion.angles])


def motion_value(motion: Any, k: float) -> Any:
    """The motion `k` of the way from its rest pose (0) to its end pose (1): an angle (degrees) or
    an offset."""
    if motion.kind == "slide":
        a = motion.offsets[0]
        b = motion.offsets[1]
        return [a[i] + (b[i] - a[i]) * k for i in range(3)]
    return motion.angles[0] + (motion.angles[1] - motion.angles[0]) * k


def inverse_value(motion: Any, value: Any) -> Any:
    """The value undoing `value` (the angle or offset back)."""
    if motion.kind == "slide":
        return [-value[0], -value[1], -value[2]]
    return -value


def move_point(motion: Any, value: Any, point: list[float]) -> list[float]:
    """`point` `[x, y, z]` moved from the pose as drawn by `value` of `motion` (see
    `motion_value`)."""
    if motion.kind == "slide":
        return [point[0] + value[0], point[1] + value[1], point[2] + value[2]]
    p = motion.pivot
    a = value * DEG
    c = math.cos(a)
    s = math.sin(a)
    x = point[0] - p[0]
    y = point[1] - p[1]
    z = point[2] - p[2]
    if motion.axis == "up":
        return [p[0] + x * c - y * s, p[1] + x * s + y * c, point[2]]
    if motion.axis == "along":
        return [p[0] + z * s + x * c, point[1], p[2] + z * c - x * s]
    return [point[0], p[1] + y * c - z * s, p[2] + y * s + z * c]


def _side(outline: list[Any]) -> str:
    sx = 0.0
    for point in outline:
        sx += point[0]
    return "right" if sx >= 0 else "left"


def moving_region(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    region_id: str,
    form: int,
    outline: list[Any],
    motion: Any,
    frame: Any = None,
    heights: Any = None,
    mirror: bool = True,
) -> list[Any]:
    """The pieces of a moving region (see the module): the part of the body inside `outline`,
    between `heights` (all of it when left out), moving by `motion` at transformation `form`, and
    with `mirror` its mirror image moving the mirror way (two regions, `region_id` + `-right` and
    `-left`). `frame` (`wing`, `shell` or `ring`): what shows where a piece was drawn once it has
    moved; nothing when left out."""
    if frame != None and frame not in FRAMES:  # noqa: E711
        raise ValueError('Unknown armour frame "' + frame + '"')
    first = armour_region(region_id, form, outline, "wing", heights, mirror)
    result: list[Any] = []
    side = _side(outline)
    for k in range(len(first.outlines)):
        mine = k == 0
        name = region_id
        if mirror:
            name = region_id + "-" + (side if mine else ("left" if side == "right" else "right"))
        result.append(
            merge(
                first,
                {
                    "id": name,
                    "outlines": [first.outlines[k]],
                    "frame": frame,
                    "motion": motion if mine else mirrored_motion(motion),
                },
            )
        )
    return result


def is_moving(region: Any) -> bool:
    """Whether `region` moves (see `moving_region`) rather than bursting off."""
    return bool(region.motion != None)  # noqa: E711


def end_spot(region: Any, point: list[float]) -> list[float]:
    """Where `point` on `region`'s piece as drawn is once it has moved."""
    m = region.motion
    return move_point(m, motion_value(m, 1), point)


def drawn_spot(region: Any, point: list[float]) -> list[float]:
    """Where `point` of `region`'s piece once it has moved is on the piece as drawn."""
    m = region.motion
    return move_point(m, inverse_value(m, motion_value(m, 1)), point)


def _inside(outline: list[Any], x: float, y: float) -> bool:
    """Whether `(x, y)` is inside `outline` (even-odd)."""
    result = False
    n = len(outline)
    for i in range(n):
        a = outline[i]
        b = outline[(i + n - 1) % n]
        if (a[1] > y) != (b[1] > y):
            cross = a[0] + (y - a[1]) * (b[0] - a[0]) / (b[1] - a[1])
            if x < cross:
                result = not result
    return result


def ridden_region(design: Any, part: Any) -> Any:
    """The moving region the hidden part `part` rides (D-230), if any: one moving at the
    transformation that reveals it, its piece under the part's pod once moved. None otherwise."""
    reveal = part.reveal
    if reveal == None:  # noqa: E711
        return None
    weapons = design.weapons
    look = weapons[part.id] if weapons != None and part.id in weapons else None  # noqa: E711
    height = look.height if look != None else 0  # noqa: E711
    for region in design.armour or []:
        if not is_moving(region) or region.form != reveal:
            continue
        # On its piece: over it, and no lower than where it was cut (not beneath a lifted one).
        spot = drawn_spot(region, [part.x, part.y, height])
        if _inside(region.outlines[0], spot[0], spot[1]) and spot[2] >= region.heights[0]:
            return region
    return None
