"""The models of the hidden weapon parts a boss reveals as it transforms (see
`game/config/bosses/hidden_weapons.py`, which works out their muzzles from the same sizes).

Model space of a boss: logical pixels, +Y up, its nose at +Z (`boss_limbs.boss_point`).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.hidden_weapons import WEAPON_SHAPE, gatling_turret
from game.config.enemy_look import ENEMY_LOOK
from game.config.record import record
from game.view.bosses.mini_boss_shapes import offset, turret
from render.geometry.solids import Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

Vec3 = list[Any]
__pragma__("noskip")

H = ENEMY_LOOK.hull
QUARTER = math.pi / 2


def _octagon(radius: float) -> list[list[float]]:
    result: list[list[float]] = []
    for k in range(8):
        a = (2 * math.pi * (k + 0.5)) / 8
        result.append([math.cos(a) * radius, math.sin(a) * radius])
    return result


def _pod(p: Any, at: Vec3, look: Any, neon: Any) -> None:
    """The armoured pod a weapon stands on: a bevelled octagon with a neon ring round its top."""
    r = look.radius
    h = look.height
    p.hull.bevel_slab(
        _octagon(r * WEAPON_SHAPE.pod), [0, h * 0.7, h], [0, r * 0.15], H.panel, Placement(at)
    )
    p.neon.ring(r * WEAPON_SHAPE.pod * 0.8, r * 0.07, 8, neon, Placement(offset(at, 0, h, 0)))


def _lance(p: Any, at: Vec3, look: Any, neon: Any) -> None:
    """A laser lance pointing down the screen (+Z), a glowing tip at its muzzle."""
    r = look.radius
    bore = r * WEAPON_SHAPE.lanceBore
    length = r * WEAPON_SHAPE.lance
    base = offset(at, 0, look.height * 0.9, 0)
    p.hull.cylinder(bore, length - bore, 6, H.dark, Placement(base, 0, QUARTER), bore * 0.6)
    p.neon.cylinder(
        bore * 0.7,
        bore,
        6,
        neon,
        Placement(offset(base, 0, 0, length - bore), 0, QUARTER),
        0,
    )


def _rack(p: Any, at: Vec3, look: Any, neon: Any) -> None:
    """Four missile cells standing on the pod, their tips glowing."""
    r = look.radius
    top = r * WEAPON_SHAPE.cellTop
    cell = r * WEAPON_SHAPE.cell
    for sx in [-1, 1]:
        for sz in [-1, 1]:
            foot = offset(at, sx * r * WEAPON_SHAPE.cellX, look.height, sz * r * WEAPON_SHAPE.cellY)
            p.hull.cylinder(cell, top * 0.75, 6, H.dark, Placement(foot))
            p.neon.cylinder(
                cell * 0.8, top * 0.25, 6, neon, Placement(offset(foot, 0, top * 0.75, 0))
            )


def _orb(p: Any, at: Vec3, look: Any, neon: Any) -> None:
    """A glowing emitter orb held in a cradle on top of the pod."""
    r = look.radius
    o = r * WEAPON_SHAPE.orb
    centre = offset(at, 0, look.height + r * WEAPON_SHAPE.orbTop, 0)
    p.hull.cylinder(
        o * 1.1,
        r * WEAPON_SHAPE.orbTop,
        8,
        H.dark,
        Placement(offset(at, 0, look.height, 0)),
        o * 0.7,
    )
    sphere = [[0, -o], [o * 0.7, -o * 0.7], [o, 0], [o * 0.7, o * 0.7], [0, o]]
    p.neon.lathe(sphere, 6, neon, Placement(centre))


def weapon_drawing(look: Any, neon: Any) -> Any:
    """The drawing of a hidden weapon part's pod (`look`: kind, radius, pod height), `draw(p, at)`;
    what slides out of it is drawn apart (`weapon_slide`)."""

    def draw(p: Any, at: Vec3) -> None:
        _pod(p, at, look, neon)

    return draw


def weapon_slide(look: Any, neon: Any) -> Any:
    """What slides out of a hidden weapon's pod as it unfolds: `[draw(p, at), axis, distance]`
    (model space), or None for a gatling (its turret rises instead, see `turret_slide`)."""
    r = look.radius
    if look.kind == "lance":

        def lance(p: Any, at: Vec3) -> None:
            _lance(p, at, look, neon)

        return [lance, [0, 0, 1], r * WEAPON_SHAPE.lance * 0.75]
    if look.kind == "rack":

        def rack(p: Any, at: Vec3) -> None:
            _rack(p, at, look, neon)

        return [rack, [0, 1, 0], r * WEAPON_SHAPE.cellTop]
    if look.kind == "orb":

        def orb(p: Any, at: Vec3) -> None:
            _orb(p, at, look, neon)

        return [orb, [0, 1, 0], r * (WEAPON_SHAPE.orbTop + WEAPON_SHAPE.orb)]
    return None


def turret_slide(look: Any) -> float:
    """How far a gatling's turret rises out of its pod as it unfolds."""
    return float(gatling_turret(look.radius).radius * 0.9)


def weapon_turret_drawing(look: Any, neon: Any) -> Any:
    """The drawing of a gatling's turret, `draw(p, at)` round its pivot `at` (on top of its pod);
    None for other kinds."""
    if look.kind != "gatling":
        return None
    t = gatling_turret(look.radius)

    def draw(p: Any, at: Vec3) -> None:
        turret(
            p,
            offset(at, 0, look.height, 0),
            record(
                {
                    "radius": t.radius,
                    "barrels": 3,
                    "gap": t.gap,
                    "bore": t.bore,
                    "length": t.length,
                    "neon": neon,
                }
            ),
        )

    return draw
