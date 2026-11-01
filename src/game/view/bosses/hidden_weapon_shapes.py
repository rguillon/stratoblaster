"""The models of the hidden weapon parts a boss reveals as it transforms (see
`game/config/bosses/weapon_kinds.py`, which works out their muzzles from the same sizes; D-229).

Model space of a boss: logical pixels, +Y up, its nose at +Z (`boss_limbs.boss_point`).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.weapon_kinds import (
    WEAPON_SHAPE,
    battery_offsets,
    cannon_turret,
    gatling_turret,
)
from game.config.enemy_look import ENEMY_LOOK
from game.config.record import record
from game.view.bosses.mini_boss_shapes import offset, turned, turret
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


def _rectangle(width: float, depth: float) -> list[list[float]]:
    w = width / 2
    d = depth / 2
    return [[-w, -d], [w, -d], [w, d], [-w, d]]


def _pod(p: Any, at: Vec3, look: Any, neon: Any) -> None:
    """The pod a weapon stands on: a bevelled octagon with a neon ring round its top (a square one
    for a cannon); the mortar's is round, the battery's a long low deck, the hangar's a box."""
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
    p.hull.bevel_slab(outline, [0, h * 0.7, h], [0, r * 0.15], H.panel, Placement(at))
    p.neon.ring(r * WEAPON_SHAPE.pod * 0.8, r * 0.07, 8, neon, Placement(offset(at, 0, h, 0)))


def _round_base(p: Any, at: Vec3, look: Any, neon: Any) -> None:
    """The mortar's squat round base, a neon ring round its top."""
    r = look.radius * WEAPON_SHAPE.mortarBase
    h = look.height
    p.hull.cylinder(r, h, 10, H.panel, Placement(at), r * 0.82)
    p.neon.ring(r * 0.7, look.radius * 0.07, 10, neon, Placement(offset(at, 0, h, 0)))


def _deck(p: Any, at: Vec3, look: Any, neon: Any) -> None:
    """The battery's long, low gun deck (a neon strip along its front), or the hangar's box (a
    glowing bay floor on top, under its doors)."""
    r = look.radius
    h = look.height
    if look.kind == "battery":
        width = r * WEAPON_SHAPE.deckWidth
        depth = r * WEAPON_SHAPE.deckDepth
    else:
        width = r * WEAPON_SHAPE.bayWidth
        depth = r * WEAPON_SHAPE.bayDepth
    p.hull.bevel_slab(
        _rectangle(width, depth), [0, h * 0.7, h], [0, r * 0.1], H.panel, Placement(at)
    )
    if look.kind == "battery":
        strip = [width * 0.9, r * 0.08, r * 0.08]
        p.neon.box(strip, neon, Placement(offset(at, 0, h * 0.86, depth / 2 - r * 0.05)))
        return
    floor = [width * 0.6, r * 0.04, depth * 0.7]
    p.neon.box(floor, neon, Placement(offset(at, 0, h, 0)))


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
    what slides out of it is drawn apart (`weapon_slides`)."""

    def draw(p: Any, at: Vec3) -> None:
        _pod(p, at, look, neon)

    return draw


def _mortar_tube(p: Any, at: Vec3, look: Any, neon: Any) -> None:
    """The mortar's short, wide tube on a trunnion block, tilted up towards the nose, its mouth
    glowing (`weapon_kinds.mortar_mouth`)."""
    r = look.radius
    bore = r * WEAPON_SHAPE.mortarBore
    length = r * WEAPON_SHAPE.mortarLength
    e = WEAPON_SHAPE.mortarDeg * math.pi / 180
    pitch = QUARTER - e
    foot = offset(
        at, 0, look.height + r * WEAPON_SHAPE.mortarFoot, r * WEAPON_SHAPE.mortarBack * -1
    )
    block = [bore * 2.6, r * WEAPON_SHAPE.mortarFoot + bore * 0.6, bore * 2.2]
    p.hull.box(block, H.dark, Placement(offset(foot, 0, -r * WEAPON_SHAPE.mortarFoot, 0)))
    p.hull.cylinder(bore, length - bore * 0.3, 8, H.dark, Placement(foot, 0, pitch), bore * 1.1)
    mouth = turned(foot, [0, 0, 0], length - bore * 0.3, pitch, 0)
    p.neon.ring(bore * 1.12, bore * 0.3, 8, neon, Placement(mouth, 0, pitch))


def _battery_barrels(p: Any, at: Vec3, look: Any, neon: Any) -> None:
    """The battery's barrels, in a row out of its deck's front, their tips glowing."""
    r = look.radius
    bore = r * WEAPON_SHAPE.barrelBore
    length = r * WEAPON_SHAPE.barrelLength
    front = r * WEAPON_SHAPE.deckDepth / 2
    lift = look.height * WEAPON_SHAPE.barrelLift
    for dx in battery_offsets(r):
        root = offset(at, -dx, lift, front - bore)
        p.hull.cylinder(bore, length + bore - bore * 0.5, 6, H.dark, Placement(root, 0, QUARTER))
        tip = offset(at, -dx, lift, front + length - bore * 0.5)
        p.neon.cylinder(bore * 1.1, bore * 0.5, 6, neon, Placement(tip, 0, QUARTER))


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


def _drawn(draw: Any, look: Any, neon: Any) -> Any:
    def piece(p: Any, at: Vec3) -> None:
        draw(p, at, look, neon)

    return piece


def _door_drawn(draw: Any, look: Any) -> Any:
    def piece(p: Any, at: Vec3) -> None:
        draw(p, at, look)

    return piece


def _lance_slides(look: Any, neon: Any) -> list[Any]:
    return [[_drawn(_lance, look, neon), [0, 0, 1], look.radius * WEAPON_SHAPE.lance * 0.75]]


def _rack_slides(look: Any, neon: Any) -> list[Any]:
    return [[_drawn(_rack, look, neon), [0, 1, 0], look.radius * WEAPON_SHAPE.cellTop]]


def _orb_slides(look: Any, neon: Any) -> list[Any]:
    rise = look.radius * (WEAPON_SHAPE.orbTop + WEAPON_SHAPE.orb)
    return [[_drawn(_orb, look, neon), [0, 1, 0], rise]]


def _mortar_slides(look: Any, neon: Any) -> list[Any]:
    rise = look.radius * WEAPON_SHAPE.mortarLength * 0.6
    return [[_drawn(_mortar_tube, look, neon), [0, 1, 0], rise]]


def _battery_slides(look: Any, neon: Any) -> list[Any]:
    reach = look.radius * WEAPON_SHAPE.barrelLength
    return [[_drawn(_battery_barrels, look, neon), [0, 0, 1], reach]]


def _hangar_slides(look: Any, _neon: Any) -> list[Any]:
    travel = look.radius * WEAPON_SHAPE.bayWidth * 0.18
    return [
        [_door_drawn(_door(1), look), [1, 0, 0], travel],
        [_door_drawn(_door(-1), look), [-1, 0, 0], travel],
    ]


# What slides out of each kind (turrets rise instead).
SLIDES_OF = {
    "lance": _lance_slides,
    "rack": _rack_slides,
    "orb": _orb_slides,
    "mortar": _mortar_slides,
    "battery": _battery_slides,
    "hangar": _hangar_slides,
}


def weapon_slides(look: Any, neon: Any) -> list[Any]:
    """What slides out of a hidden weapon's pod as it unfolds: a list of `[draw(p, at), axis,
    distance]` (model space), none for a turret (it rises instead, see `turret_slide`): the lance's
    barrel, the rack's cells, the orb, the mortar's tube, the battery's barrels, the hangar's two
    doors (sliding open)."""
    if look.kind not in SLIDES_OF:
        return []
    slides: list[Any] = SLIDES_OF[look.kind](look, neon)
    return slides


def turret_slide(look: Any) -> float:
    """How far a weapon's turret (a gatling's, a cannon's or a sweeper's) rises out of its pod as
    it unfolds."""
    if look.kind == "cannon":
        return float(cannon_turret(look.radius).radius * 0.9)
    if look.kind == "sweeper":
        return float(look.radius * WEAPON_SHAPE.sweeperTurret * 0.9)
    return float(gatling_turret(look.radius).radius * 0.9)


def _sweeper_turret(p: Any, top: Vec3, look: Any, neon: Any) -> None:
    """The sweeper's turret on top of its pod (`top`): a low dome, two prongs reaching forward
    (+Z), a glowing lens between their tips."""
    r = look.radius
    rt = r * WEAPON_SHAPE.sweeperTurret
    length = r * WEAPON_SHAPE.prongLength
    gap = r * WEAPON_SHAPE.prongGap
    lift = rt * WEAPON_SHAPE.lensLift
    p.hull.cylinder(rt, rt * 0.4, 8, H.panel, Placement(top, math.pi / 8), rt * 0.75)
    thick = r * 0.12
    for side in [1, -1]:
        x = side * gap / 2
        prong = Placement(offset(top, x, lift - thick * 0.6, length / 2))
        p.hull.box([thick, thick * 1.2, length], H.dark, prong, H.panel)
        p.neon.box(
            [thick * 0.3, thick * 0.4, length * 0.7],
            neon,
            place_inner(top, x, side, lift, length, thick),
        )
    o = gap * 0.36
    sphere = [[0, -o], [o * 0.7, -o * 0.7], [o, 0], [o * 0.7, o * 0.7], [0, o]]
    p.neon.lathe(sphere, 6, neon, Placement(offset(top, 0, lift, length * 0.92)))
    p.hull.box(
        [gap, thick * 0.8, thick],
        H.dark,
        Placement(offset(top, 0, lift - thick * 0.4, length * 0.8)),
    )


def place_inner(top: Vec3, x: float, side: float, lift: float, length: float, thick: float) -> Any:
    """Where the neon strip on a sweeper prong's inner face goes."""
    return Placement(offset(top, x - side * thick * 0.55, lift - thick * 0.2, length * 0.55))


def weapon_turret_drawing(look: Any, neon: Any) -> Any:
    """The drawing of a weapon's turret, `draw(p, at)` round its pivot `at` (on top of its pod): a
    gatling's three barrels, a cannon's heavy one (a neon ring round its muzzle), a sweeper's
    prongs; None for other kinds."""
    kind = look.kind
    if kind == "sweeper":

        def sweeper(p: Any, at: Vec3) -> None:
            _sweeper_turret(p, offset(at, 0, look.height, 0), look, neon)

        return sweeper
    if kind not in ["gatling", "cannon"]:
        return None
    t = gatling_turret(look.radius) if kind == "gatling" else cannon_turret(look.radius)
    barrels = 3 if kind == "gatling" else 1

    def draw(p: Any, at: Vec3) -> None:
        top = offset(at, 0, look.height, 0)
        turret(
            p,
            top,
            record(
                {
                    "radius": t.radius,
                    "barrels": barrels,
                    "gap": t.gap,
                    "bore": t.bore,
                    "length": t.length,
                    "neon": neon,
                }
            ),
        )
        if kind == "cannon":
            foot = [0, t.radius * 0.28, t.radius * 0.3]
            brake = turned(top, foot, t.length + t.radius * 0.5 - t.bore * 1.4, QUARTER, 0)
            p.neon.ring(t.bore * 1.25, t.bore * 0.7, 6, neon, Placement(brake, 0, QUARTER))
            block = [t.radius * 1.3, t.radius * 0.5, t.radius * 1.1]
            p.hull.box(block, H.dark, Placement(offset(top, 0, 0, -t.radius * 0.35)), H.panel)

    return draw
