# Copyright (c) 2026 Renaud Guillon
"""The models of the hidden weapon parts a boss reveals as it transforms.

See `game/config/bosses/weapon_kinds.py`, which works out their muzzles from the same sizes
(BOSS-40, D-229). Which weapons each boss hides is its own boss file's (its hidden weapons
requirements, specs/bosses/mini/*.md and specs/bosses/final/*.md).

Model space of a boss: logical pixels, +Y up, its nose at +Z (`boss_limbs.boss_point`).
"""

import math

from game.config.bosses.weapon_kinds import WEAPON_SHAPE
from game.config.enemy_look import ENEMY_LOOK
from game.config.record import field
from game.view.bosses.mini_boss_shapes import offset
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

Vec3 = list[Any]
# __pragma__ ("noskip")


H = ENEMY_LOOK.hull
QUARTER = math.pi / 2


def _octagon(radius: float) -> list[list[float]]:
    result: list[list[float]] = []
    for k in range(8):
        a = (2 * math.pi * (k + 0.5)) / 8
        result.append([math.cos(a) * radius, math.sin(a) * radius])
    return result


def _rectangle(width: float, depth: float) -> list[list[float]]:
    w = width / 2
    d = depth / 2
    return [[-w, -d], [w, -d], [w, d], [-w, d]]


def _base(look: Any) -> float:
    """Return the height a pod stands on (its surface: a wing's membrane, else the playfield)."""
    base: float = field(look, "base", 0) or 0
    return base


def _heights(look: Any) -> list[float]:
    """Return a pod's slab heights: from what it stands on, its bevel's start, its top."""
    base = _base(look)
    h = look.height
    return [base, base + (h - base) * 0.7, h]


def _pod(p: Any, at: Vec3, look: Any, neon: Any) -> None:
    """Add the pod a weapon stands on.

    A bevelled octagon with a neon ring round its top (a square one for a cannon); the mortar's is
    round, the battery's a long low deck, the hangar's a box.
    """
    kind = look.kind
    if kind == "mortar":
        _round_base(p, at, look, neon)
        return
    if kind in ["battery", "hangar"]:
        _deck(p, at, look, neon)
        return
    r = look.radius
    h = look.height
    outline = _octagon(r * WEAPON_SHAPE.pod)
    if kind == "cannon":
        side = r * WEAPON_SHAPE.cannonBase * 2
        outline = _rectangle(side, side)
    p.hull.bevel_slab(outline, _heights(look), [0, r * 0.15], H.panel, Placement(at))
    p.neon.ring(r * WEAPON_SHAPE.pod * 0.8, r * 0.07, 8, neon, Placement(offset(at, 0, h, 0)))


def _round_base(p: Any, at: Vec3, look: Any, neon: Any) -> None:
    """Add the mortar's squat round base, a neon ring round its top."""
    r = look.radius * WEAPON_SHAPE.mortarBase
    h = look.height
    base = _base(look)
    p.hull.cylinder(r, h - base, 10, H.panel, Placement(offset(at, 0, base, 0)), r * 0.82)
    p.neon.ring(r * 0.7, look.radius * 0.07, 10, neon, Placement(offset(at, 0, h, 0)))


def _deck(p: Any, at: Vec3, look: Any, neon: Any) -> None:
    """Add the battery's long, low gun deck (a neon strip along its front).

    Or the hangar's box (a glowing bay floor on top, under its doors).
    """
    r = look.radius
    h = look.height
    if look.kind == "battery":
        width = r * WEAPON_SHAPE.deckWidth
        depth = r * WEAPON_SHAPE.deckDepth
    else:
        width = r * WEAPON_SHAPE.bayWidth
        depth = r * WEAPON_SHAPE.bayDepth
    p.hull.bevel_slab(
        _rectangle(width, depth), _heights(look), [0, r * 0.1], H.panel, Placement(at)
    )
    if look.kind == "battery":
        strip = [width * 0.9, r * 0.08, r * 0.08]
        base = _base(look)
        lift = base + (h - base) * 0.86
        p.neon.box(strip, neon, Placement(offset(at, 0, lift, depth / 2 - r * 0.05)))
        return
    floor = [width * 0.6, r * 0.04, depth * 0.7]
    p.neon.box(floor, neon, Placement(offset(at, 0, h, 0)))


def weapon_drawing(look: Any, neon: Any) -> Any:
    """Return the drawing of a hidden weapon part's pod (`look`: kind, radius, pod height).

    `draw(p, at)`; its mount is drawn apart (`boss_gun_models`), and what slides out of it
    (`weapon_slides`).
    """

    def draw(p: Any, at: Vec3) -> None:
        _pod(p, at, look, neon)

    return draw


def _door(side: float) -> Any:
    """One of the hangar's two doors (`side` 1: model +X), drawn open, on its box's rim."""

    def draw(p: Any, at: Vec3, look: Any) -> None:
        r = look.radius
        width = r * WEAPON_SHAPE.bayWidth
        depth = r * WEAPON_SHAPE.bayDepth
        door = [width * 0.32, r * 0.08, depth * 0.78]
        p.hull.box(
            door, H.dark, Placement(offset(at, side * width * 0.34, look.height, 0)), H.panel
        )

    return draw


def _door_drawn(draw: Any, look: Any) -> Any:
    def piece(p: Any, at: Vec3) -> None:
        draw(p, at, look)

    return piece


def _hangar_slides(look: Any, _neon: Any) -> list[Any]:
    travel = look.radius * WEAPON_SHAPE.bayWidth * 0.18
    return [
        [_door_drawn(_door(1), look), [1, 0, 0], travel],
        [_door_drawn(_door(-1), look), [-1, 0, 0], travel],
    ]


def weapon_slides(look: Any, _neon: Any) -> list[Any]:
    """Return what slides out of a hidden weapon's pod as it unfolds, besides its mount.

    A list of `[draw(p, at), axis, distance]` (model space): a hangar's two doors, sliding open;
    nothing for the others (their mount rises out of the pod, `boss_model`).
    """
    if look.kind != "hangar":
        return []
    return _hangar_slides(look, _neon)
