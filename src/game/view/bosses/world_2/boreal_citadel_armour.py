# Copyright (c) 2026 Renaud Guillon
"""The Boreal Citadel's armour (FB-BOREAL-CITADEL-08, D-254): its bow doors and its wing panels.

Its deck is a slab of flesh up to `HOLD`, under panels of rimed flesh up to the deck's top:
the panels of the bow (`bow-doors-right`, `bow-doors-left`, within `DOOR_X` of the centre line
ahead of `DOOR_Z`) are its doors, carrying the city's towers, heated domes and drift there, which
the engine swings open; the panels of its sides (`wings`, beyond `DOOR_X` from `WING_TAIL` to
`DOOR_Z`) carry the towers, drifts, dish, mast, skirt and artery there, and burst off. The other
panels are the core's. Logical pixels, nose +Z, Y up.
"""

from game.view.bosses.overlord_city import symmetric
from game.view.bosses.world_2.boreal_citadel_city import (
    AURORA,
    CITADEL_DECK,
    DOOR_LEFT,
    DOOR_RIGHT,
    DOOR_X,
    DOOR_Z,
    WING_TAIL,
    Zone,
    draw_city,
)
from game.view.bosses.world_2.boreal_citadel_details import draw_details
from game.view.bosses.world_2.w2_organic import ICE_FLESH, glow_vein
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.outline import inset_outline, reversed_copy

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from game.view.enemies.enemy_mesh import EnemyParts

type Outline = list[list[float]]
# __pragma__ ("noskip")


# The deck (right half, front to tail).
DECK = symmetric(
    [
        [20.0, 84.0],
        [44.0, 66.0],
        [60.0, 36.0],
        [62.0, -20.0],
        [54.0, -56.0],
        [36.0, -78.0],
        [18.0, -84.0],
    ],
    86,
)
# The deck's flesh: from `DECK_BOTTOM` to its full outline at `DECK_WAIST`, then sloping in by
# `DECK_SLOPE` a px of height. The core's slab stops at `HOLD`, where the panels start (the frame
# a shed panel leaves lies just over it).
DECK_BOTTOM = -8.0
DECK_WAIST = -2.0
DECK_SLOPE = 3.0 / 8.0
HOLD = 4.0
FAR = 1000.0
# The deck's outline at `HOLD`, where the panels lie (`DECK` runs clockwise: reversed to inset it).
PANEL_DECK = inset_outline(reversed_copy(DECK), (HOLD - DECK_WAIST) * DECK_SLOPE)


def clip_side(outline: Outline, axis: int, edge: float, side: float) -> Outline:
    """Return `outline` (XZ, convex) clipped to the half plane `side * (p[axis] - edge) >= 0`."""
    result: Outline = []
    n = len(outline)
    for i in range(n):
        a = outline[i]
        b = outline[(i + 1) % n]
        da = side * (a[axis] - edge)
        db = side * (b[axis] - edge)
        if da >= 0:
            result.append(a)
        if (da > 0 and db < 0) or (da < 0 and db > 0):
            t = da / (da - db)
            result.append([a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t])
    return result


def clip_box(outline: Outline, box: list[float]) -> Outline:
    """Return `outline` (XZ, convex) clipped to `box` `[x0, x1, z0, z1]`."""
    result = clip_side(outline, 0, box[0], 1)
    result = clip_side(result, 0, box[1], -1)
    result = clip_side(result, 1, box[2], 1)
    return clip_side(result, 1, box[3], -1)


def side_box(s: float, x: list[float], z: list[float]) -> list[float]:
    """Return the box from `x[0]` to `x[1]` out on model side `s`, from `z[0]` to `z[1]`."""
    if s > 0:
        return [x[0], x[1], z[0], z[1]]
    return [-x[1], -x[0], z[0], z[1]]


def draw_panel(p: EnemyParts, box: list[float]) -> None:
    """Draw the deck's panel within `box` (see `clip_box`): rimed flesh from `HOLD` to its top."""
    top = CITADEL_DECK.top
    p.flesh.bevel_slab(
        clip_box(PANEL_DECK, box),
        [HOLD, HOLD, top],
        [0.0, (top - HOLD) * DECK_SLOPE],
        ICE_FLESH.teal,
        None,
        ICE_FLESH.rime,
    )


def door_box(s: float) -> list[float]:
    """Return the box of the bow door on model side `s`."""
    return side_box(s, [0.0, DOOR_X], [DOOR_Z, FAR])


def draw_core_panels(p: EnemyParts, sides: list[int]) -> None:
    """Draw the panels no armour holds: down the middle, and on each side astern and ahead."""
    draw_panel(p, [-DOOR_X, DOOR_X, -FAR, DOOR_Z])
    for s in sides:
        draw_panel(p, side_box(s, [DOOR_X, FAR], [-FAR, WING_TAIL]))
        draw_panel(p, side_box(s, [DOOR_X, FAR], [DOOR_Z, FAR]))


def _door(zone: Zone) -> Any:
    def draw(p: EnemyParts) -> None:
        draw_panel(p, door_box(zone.sides[0]))
        draw_city(p, zone)
        draw_details(p, zone)

    return draw


# The slices each wing panel bursts into (along Z), and where along it the artery lying across it
# is (it flies off with the slice holding that point).
WING_SLICES = [[WING_TAIL, 0.0], [0.0, 20.0], [20.0, DOOR_Z]]
VEIN_AT = 20.0


def draw_wing_slice(p: EnemyParts, s: int, span: list[float]) -> None:
    """Draw the slice `span` (along Z) of the wing panel on model side `s` (FB-BOREAL-CITADEL-08).

    The panel and what stands on it: towers, drifts, the dish, a mast, a skirt, the artery from the
    dome to the outrigger lying across the panel.
    """
    top = CITADEL_DECK.top
    draw_panel(p, side_box(s, [DOOR_X, FAR], span))
    zone = Zone("wing", [s], span)
    draw_city(p, zone)
    draw_details(p, zone)
    if span[0] <= VEIN_AT < span[1]:
        glow_vein(p, [s * 18.0, top + 1.0, 40.0], [s * 56.0, top, 0.0], 1.4, AURORA)


def draw_wings(p: EnemyParts) -> None:
    """Draw both wing panels, every slice of them, as they lie at rest."""
    for s in SIDES:
        for span in WING_SLICES:
            draw_wing_slice(p, s, span)


def _wing_slice(s: int, span: list[float]) -> Any:
    def draw(p: EnemyParts) -> None:
        draw_wing_slice(p, s, span)

    return draw


def wing_pieces() -> list[Any]:
    """Return the pieces the wing panels burst into: their slices, each with what stands on it."""
    result: list[Any] = []
    for s in SIDES:
        result.extend([_wing_slice(s, span) for span in WING_SLICES])
    return result


def citadel_armour() -> Any:
    """Return the Boreal Citadel's armour drawings by region id.

    The bow doors, moving pieces that burst into nothing (`bow-doors-right` is the model's -X
    side: the config's +X is mirrored), and the wing panels, bursting into their slices.
    """
    return {
        "bow-doors-right": {"whole": _door(DOOR_RIGHT), "pieces": []},
        "bow-doors-left": {"whole": _door(DOOR_LEFT), "pieces": []},
        "wings": {"whole": draw_wings, "pieces": wing_pieces()},
    }
