# Copyright (c) 2026 Renaud Guillon
"""MB-ARROW-LANCE-01 to MB-ARROW-LANCE-05: the Arrow Lance, the Lab's L-8 mini boss.

Model space: logical pixels, nose +Z (down the screen), Y up towards the camera. A sleek stealth
delta: a flat, faceted arrowhead of dark metal plates, a low faceted spine down its middle, a
sawtooth trailing edge, two engine nacelles at the back and yellow light lines along its leading
edges. A machine, not a creature (the Lab's second set, 2026-11-06). Its gun
mounts are drawn by `build_boss_model` (BOSS-58).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.arrow_lance import (
    ARROW_LANCE,
    DELTA,
    NOSE_TOP,
    PANEL_HEIGHTS,
    ROTOR_AT,
    SPINE_AT,
    SPINE_TOP,
    WING_PANEL,
    WING_TOP,
)
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_shapes import edge_strips, mirrored, strip
from game.view.bosses.mini_boss_greebles import lamps, seam, vent
from game.view.bosses.mini_boss_shapes import offset, sign_of
from game.view.bosses.world_1_organic_kit import M
from game.view.enemies.enemy_shapes import FIGHTER_SECTION, SIDES
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

type Vec3 = list[Any]
# __pragma__ ("noskip")


Y = BOSS_LOOK.neon["arrow-lance"]
# Its smoked canopy glass and its darkest plating.
GLASS = [0.05, 0.06, 0.075]
SOOT = [0.035, 0.035, 0.042]

# The delta's wing: its bottom, its edge's waist and its top (MB-ARROW-LANCE-02).
WING_Y = [0, 1.2, 2.5]
# The spine: stations along Z (tail to nose): z, half width, belly and ridge.
SPINE: list[Any] = [
    [-27, 5, 0.5, 6],
    [-18, 8, 0, 8.4],
    [6, 9.5, 0, 8.6],
    [24, 7.5, 0, 7.4],
    [40, 4.5, 0.5, 5.2],
    [53, 0, 2, 2],
]
# The deck on the spine the core's guns stand on, from `DECK[0]` to `DECK[1]` along Z, `DECK[2]`
# wide either side.
DECK = [-22, 18, 6.4]
# The engine nacelles: x either side, their axis' height, radius, and their span along Z.
NACELLE = [7.5, 3.6, 3.4, -32, -8]


def _model(outline: list[Any]) -> list[Any]:
    """Return a config outline (`[x, y]`, Y up the screen) in model space (`[-x, -y]`)."""
    return [[-q[0], -q[1]] for q in outline]


def _delta() -> list[Any]:
    """Return the whole delta's outline in model space."""
    return _model(mirrored(DELTA))


def _draw_wing(p: Any) -> None:
    """Draw the delta's wing (MB-ARROW-LANCE-02): a thin, faceted plate of dark metal.

    Its edges chamfered all round, angular panels raised on its outer wings round the pods, dark
    panel lines across it and yellow light lines just behind its leading edges.
    """
    p.hull.bevel_slab(_delta(), WING_Y, [0.6, 2.2], M.base, None, M.panel)
    top = WING_Y[2]
    for s in SIDES:
        # The outer wing's raised facets, behind the panels and round the wingtip pods.
        outer = [[s * 34, -10], [s * 46.5, -16], [s * 48, -21], [s * 40, -27], [s * 31, -21]]
        p.hull.bevel_slab(outer, [top - 0.4, top, top + 1.2], [0, 0.8], M.panel, None, M.base)
        inner = [[s * 12, -14], [s * 30, -14], [s * 27, -20], [s * 17, -27], [s * 9, -22]]
        p.hull.bevel_slab(inner, [top - 0.4, top, top + 0.8], [0, 0.6], M.base, None, M.panel)
        # Its leading edge's light line, nose to wingtip, and a short one along its trailing teeth.
        edge_strips(p.neon, [[s * 1.5, 52], [s * 48.5, -19.5]], 0.7, [top - 0.6, top + 0.15], Y)
        edge_strips(p.neon, [[s * 31, -22], [s * 40, -27.6]], 0.5, [top - 0.4, top + 0.2], Y)
        # Panel lines across the wing (dark, raised a hair).
        for line in [
            [[11, 30], [24, 10]],
            [[11, 18], [40, -14]],
            [[10, -8], [28, -22]],
            [[28, -12], [46, -17]],
        ]:
            seam(
                p.hull, [s * line[0][0], line[0][1]], [s * line[1][0], line[1][1]], [top, 0.5, 0.3]
            )
        vent(p.hull, [s * 22, top, -20], [5, 3], 3, -s * 0.6)
    lamps(p.neon, [[48.5, top, -21], [-48.5, top, -21]], 1.4, Y)


def _draw_spine(p: Any) -> None:
    """Draw the spine (MB-ARROW-LANCE-02): a low, faceted fuselage from its tail to its nose.

    Its sensor glass behind the nose pod, the deck the spine turret and the back rotor stand on,
    and a yellow line down each shoulder.
    """
    p.hull.loft(FIGHTER_SECTION, SPINE, M.base)
    z0 = DECK[0]
    z1 = DECK[1]
    w = DECK[2]
    deck = [[0, z1 + 5], [w, z1], [w, z0 + 3], [w - 3, z0], [-w + 3, z0], [-w, z0 + 3], [-w, z1]]
    p.hull.bevel_slab(deck, [SPINE_TOP - 3, SPINE_TOP - 0.8, SPINE_TOP], [0, 0.8], M.panel)
    for s in SIDES:
        edge_strips(p.neon, [[s * 6.6, z1 - 1], [s * 6.6, z0 + 3]], 0.45, [7.6, 8.4], Y)
        strip(p.neon, [s * 2, 34], [s * 5.5, 22], 0.4, [6.9, 7.4], Y)
    # The spine turret's seat (its mount, BOSS-58).
    seat = [0, SPINE_TOP - 0.2, -SPINE_AT[1]]
    p.hull.cylinder(5.4, 0.6, 8, M.dark, Placement(seat, math.pi / 8))
    # Its sensor chines either side of the nose pod, a smoked glass slit on each.
    for s in SIDES:
        p.hull.box([1.2, 1.2, 8], SOOT, Placement([s * 5.5, 5.6, 26], -s * 0.25))
        p.hull.box([0.8, 0.4, 6], GLASS, Placement([s * 5.5, 6.8, 26], -s * 0.25))


def _draw_engines(p: Any) -> None:
    """Draw the two engine nacelles at its back (MB-ARROW-LANCE-02), their nozzles glowing."""
    x, axis, r, z0, z1 = NACELLE
    for s in SIDES:
        p.hull.cylinder(r, z1 - z0, 8, M.panel, Placement([s * x, axis, z0], 0, math.pi / 2))
        p.hull.cylinder(
            r * 1.15, 3, 8, M.dark, Placement([s * x, axis, z0 - 1.5], 0, math.pi / 2), r * 0.95
        )
        p.neon.ring(r * 0.9, 0.4, 8, Y, Placement([s * x, axis, z0 - 1.6], 0, math.pi / 2))
        p.reactor([s * x, axis, z0 - 1.8], r * 0.75)
        p.hull.box(
            [r * 1.2, 1, z1 - z0 - 4], SOOT, Placement([s * x, axis + r - 0.4, (z0 + z1) / 2])
        )


def _draw_hatch(p: Any) -> None:
    """Draw the hatch over the back rotor (BOSS-58): a flat octagonal cap, a seam of light round."""
    at: Vec3 = [0, SPINE_TOP, -ROTOR_AT[1]]
    p.hull.cylinder(6, 1.4, 8, M.panel, Placement(at, math.pi / 8), 5.2)
    p.hull.cylinder(3.4, 0.8, 8, M.base, Placement(offset(at, 0, 1.4, 0), math.pi / 8), 2.8)
    p.neon.ring(5.7, 0.25, 8, Y, Placement(offset(at, 0, 1, 0), math.pi / 8))


def _draw_hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a collar round the opening the rotor rises out of."""
    at: Vec3 = [0, SPINE_TOP, -ROTOR_AT[1]]
    p.hull.ring(5.6, 0.9, 16, M.base, Placement(at))
    p.neon.ring(5.6, 0.3, 16, Y, Placement(offset(at, 0, 0.9, 0)))


def _draw_panels(p: Any) -> None:
    """Draw the stealth panels over its mid-wings (MB-ARROW-LANCE-05): the armour it sheds.

    A thick faceted plate either side of the spine, a yellow slit along its front edge and dark
    panel lines on it; the mortars lie folded under them.
    """
    low = PANEL_HEIGHTS[0]
    high = PANEL_HEIGHTS[1]
    right = _model(WING_PANEL)
    for s in SIDES:
        outline = [[s * abs(q[0]), q[1]] for q in right]
        p.hull.bevel_slab(outline, [low, high - 1.6, high], [0, 1.6], M.panel, None, M.base)
        strip(p.neon, [s * 13, 15.4], [s * 21, 15.4], 0.5, [high - 1.2, high - 0.3], Y)
        seam(p.hull, [s * 14, 10], [s * 25, -6], [high, 0.4, 0.2], SOOT)
        seam(p.hull, [s * 13, -1], [s * 19, -10], [high, 0.4, 0.2], SOOT)


def _nose_pod(p: Any, at: Vec3) -> None:
    """Add the nose pod (MB-ARROW-LANCE-03): a faceted arrow tip over the spine's front.

    Its laser turret stands on its top (its mount, BOSS-58); yellow chevrons on its flanks.
    """
    tip = [[0, 17], [6, 3], [6.5, -6], [3, -10], [-3, -10], [-6.5, -6], [-6, 3]]
    p.hull.bevel_slab(
        tip, [3.5, NOSE_TOP - 1.4, NOSE_TOP], [0, 1.4], M.panel, Placement(at), M.base
    )
    p.hull.cylinder(4.8, 0.5, 8, M.dark, Placement(offset(at, 0, NOSE_TOP - 0.1, 0), math.pi / 8))
    for s in SIDES:
        edge_strips(
            p.neon,
            [[at[0] + s * 1.2, at[2] + 15], [at[0] + s * 5.6, at[2] + 3.5]],
            0.5,
            [NOSE_TOP - 1.3, NOSE_TOP - 0.6],
            Y,
        )
        p.hull.box([1, 1.6, 6], SOOT, Placement(offset(at, s * 5.8, 3.2, -3)))


def _wing_pod(p: Any, at: Vec3) -> None:
    """Add a wingtip pod (MB-ARROW-LANCE-03): a long, faceted gun pod lying on the wingtip.

    Its twin-barrelled turret on its back (its mount, BOSS-58), a yellow light line down its outer
    side, a sensor tip at its front.
    """
    s = sign_of(at[0])
    pod = [[0, 13], [3.5, 8], [5, -2], [4, -12], [-4, -12], [-5, -2], [-3.5, 8]]
    top = WING_TOP
    p.hull.bevel_slab(
        pod, [WING_Y[2] - 0.6, top - 1.2, top], [0, 1.2], M.panel, Placement(at), M.base
    )
    p.hull.cylinder(4.6, 0.5, 8, M.dark, Placement(offset(at, 0, top - 0.1, 0), math.pi / 8))
    edge_strips(
        p.neon,
        [[at[0] + s * 4.4, at[2] + 6], [at[0] + s * 4.6, at[2] - 9]],
        0.5,
        [top - 1.1, top - 0.4],
        Y,
    )
    p.hull.cylinder(0.8, 4, 6, SOOT, Placement(offset(at, 0, top - 2.2, 12), 0, math.pi / 2), 0.3)
    p.hull.box([7, 0.8, 2.4], SOOT, Placement(offset(at, 0, top - 2, -12)))


def _draw_core(p: Any) -> None:
    """Draw the core: the delta's wing, its spine and its engines."""
    _draw_wing(p)
    _draw_spine(p)
    _draw_engines(p)


def build_arrow_lance(scene: Any) -> Any:
    """MB-ARROW-LANCE-01, MB-ARROW-LANCE-04: the Arrow Lance.

    A sleek stealth delta of dark faceted metal with yellow light lines: its nose pod's laser
    turret, a gun pod on each wingtip, the core's spine turret and the back rotor under a hatch.
    """
    return build_boss_model(
        ARROW_LANCE,
        scene,
        Y,
        {
            "core": _draw_core,
            "parts": {"nose": _nose_pod, "wing-left": _wing_pod, "wing-right": _wing_pod},
            "armour": {
                "panels": {"whole": _draw_panels},
                "rotor-hatch": {"whole": _draw_hatch, "frame": _draw_hatch_frame},
            },
        },
    )
