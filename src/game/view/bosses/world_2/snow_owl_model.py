# Copyright (c) 2026 Renaud Guillon
"""The Snow Owl (MB-SNOW-OWL-01 to MB-SNOW-OWL-06, 2-3).

Logical pixels, nose +Z, Y up (towards the camera).
"""

import math

from game.config.bosses.world_2.snow_owl import OWL_CHIN_GUNS, OWL_CROWN, SNOW_OWL
from game.config.record import record
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.mini_boss_greebles import seam
from game.view.bosses.mini_boss_shapes import QUARTER, WHITE, H, scaled
from game.view.bosses.world_2.snow_owl_armour import (
    TIP_ROOT,
    clip_x,
    draw_wing_slabs,
    owl_armour,
)
from game.view.bosses.world_2.snow_owl_parts import (
    OWL_WHITE,
    eye,
    icicles,
    radar_pod,
)
from game.view.bosses.world_2.w2_organic import ICE_FLESH, deck_section, sinew
from game.view.enemies.enemy_shapes import FIGHTER_SECTION, SIDES, canopy_paint
from game.view.enemies.organic_parts import reactor_sac
from render.geometry.organic import RibSpec, ribs
from render.geometry.solids import LoftOptions, Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from game.view.enemies.enemy_mesh import BuiltEnemyModel, EnemyParts

# __pragma__ ("noskip")


# The right wing seen from above, from the leading edge's root out to the tip and back.
HALF_WING = [  # type: list[list[float]]
    [0, 15],
    [14, 14],
    [28, 10],
    [40, 5],
    [48, 1],
    [51, -3],
    [49, -7],
    [45, -8],
    [42, -6],
    [39, -10],
    [35, -8],
    [31, -12],
    [27, -10],
    [22, -14],
    [14, -14],
    [6, -17],
    [0, -18],
]
# Both wings: an owl's broad, rounded wing, its trailing edge cut into feathers. The left half
# is the right one mirrored and walked back from the tip to the root (without its end points).
WING = list(HALF_WING)
for j in range(len(HALF_WING) - 2):
    i = len(HALF_WING) - 2 - j
    WING.append([-HALF_WING[i][0], HALF_WING[i][1]])
# The rimed flesh over the wings.
WING_RIME = scaled(WING, 0.86, 0, 2)
# The leading edge's neon of the inner wing, root to the tip panel's root (one wing; mirrored).
LEADING_EDGE = [  # type: list[list[float]]
    [5, 13.6],
    [14, 12.8],
    [28, 8.8],
    [30, 7.97],
]
# The back's deck: the flattened back the plating lies on (MB-SNOW-OWL-07, `snow_owl_armour`),
# `FLAT` of the way up its stations.
DECK = 5.9
FLAT = 0.62
# The body's section: the fighter's flanks under a flat back.
BACK_SECTION = deck_section(FLAT)


def back_station(z: float, half_width: float, bottom: float) -> list[float]:
    """Return a loft station of the back whose flat deck lies at `DECK`."""
    return [z, half_width, bottom, bottom + (DECK - bottom) / FLAT]


# The back along the centre line, tail to the head's root (loft stations: z, half width, bottom,
# top), and the head rising from the deck to the neck.
BACK = [
    back_station(-27, 5, -1),
    back_station(-18, 10, -3),
    back_station(-4, 13, -4),
    back_station(6, 12.3, -3.2),
]
HEAD = [  # type: list[list[float]]
    [6, 12.3, -3.2, 6.0],
    [12, 11.8, -3, 10.5],
    [20, 9, -2, 8],
    [24, 5, 0, 5],
]
# Where the inner wing's trailing-edge icicles hang (one wing; mirrored for the other).
WING_ICICLES = [  # type: list[list[float]]
    [29, -1, -10],
    [20, -1, -12.5],
]


def draw_wings(p: EnemyParts) -> None:
    """Draw the inner wings, to the root of the tip panels (MB-SNOW-OWL-05, MB-SNOW-OWL-07).

    Membrane on bone struts under a crust of snow, white neon along their leading edges; the tip
    panels are the moving pieces of `snow_owl_armour`.
    """
    flesh = p.flesh
    neon = p.neon
    # MB-SNOW-OWL-02: broad membrane wings on bone struts, rime on their fronts; too big to flutter.
    inner = clip_x(clip_x(WING, TIP_ROOT, -1), -TIP_ROOT, 1)
    rime = clip_x(clip_x(WING_RIME, TIP_ROOT, -1), -TIP_ROOT, 1)
    draw_wing_slabs(p, inner, rime)
    for s in SIDES:
        for i in range(len(LEADING_EDGE) - 1):
            a = LEADING_EDGE[i]
            b = LEADING_EDGE[i + 1]
            seam(neon, [s * a[0], a[1]], [s * b[0], b[1]], [1.6, 0.8, 0.7], OWL_WHITE)
        # Feather lines across the trailing edge.
        for pt in [[45, -3], [38, -5], [30, -7], [21, -9]]:
            sinew(
                flesh,
                [s * 6, 2.4, 2],
                [s * (pt[0] - 2), 2, pt[1] - 3],
                0.7,
                ICE_FLESH.bone,
                [0, 0.6, 4],
            )
        sinew(flesh, [s * 5, 2.4, 10], [s * 50, 1.8, -2], 1.1, ICE_FLESH.bone, [0, 1, 6])
        icicles(flesh, WING_ICICLES, s)


def draw_body(p: EnemyParts) -> None:
    """Draw the body: the flat-backed fuselage, the head, ear tufts, vents and twin reactors.

    The back's plating (the glands, crystals, spines and stripes on it) is the armour it sheds,
    `snow_owl_armour`.
    """
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    # MB-SNOW-OWL-02: a plump body of cold flesh, ribbed, a sinewy neck holding the great eye.
    hull.ring(6.4, 1.2, 8, H.panel, Placement([0, 5, 21], 0, QUARTER))
    flesh.loft(
        BACK_SECTION,
        BACK,
        ICE_FLESH.teal,
        None,
        LoftOptions(False, canopy_paint([1, 2], ICE_FLESH.rime)),
    )
    flesh.loft(FIGHTER_SECTION, HEAD, ICE_FLESH.teal)
    ribs(
        flesh,
        [-16, -8, 0],
        RibSpec(11, 4, 7, 0.7),
        ICE_FLESH.bone,
    )
    flesh.cylinder(6, 5, 7, ICE_FLESH.sinew, Placement([0, 5, 23], math.pi / 8, QUARTER))
    for s in SIDES:
        # Ear tufts, swept back over the head, a white light on each tip.
        flesh.box(
            [2.4, 9, 4],
            ICE_FLESH.graphite,
            Placement([s * 6.5, 8, 15], 0, -0.5, -s * 0.45),
            ICE_FLESH.rime,
        )
        neon.box([1.2, 1.2, 1.2], OWL_WHITE, Placement([s * 9.9, 14.6, 10.7]))
        reactor_sac(p, [s * 4, 2.5, -27.2], 2.6, OWL_WHITE, ICE_FLESH.graphite)


def draw_guns(p: EnemyParts) -> None:
    """Draw the crown emitter on the back (its rings) and the chin guns (MB-SNOW-OWL-03).

    The chin guns sit either side of the eye.
    """
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    crowns = [boss_point(m[0], m[1], m[2]) for m in OWL_CROWN]
    if len(crowns) > 0:
        crown = crowns[0]
        # On a stem from the deck: the plating round it is shed (BOSS-52).
        hull.cylinder(2.6, crown[1] - 2 - DECK, 8, H.base, Placement([crown[0], DECK, crown[2]]))
        hull.cylinder(3.4, 1.5, 8, H.base, Placement([crown[0], crown[1] - 2, crown[2]]))
        neon.ring(3.5, 0.4, 8, OWL_WHITE, Placement([crown[0], crown[1] - 1.2, crown[2]]))
        charge.cylinder(2, 0.5, 8, WHITE, Placement([crown[0], crown[1] - 0.5, crown[2]]))
        muzzle(crown, "ring")
    for m in OWL_CHIN_GUNS:
        tip = boss_point(m[0], m[1], m[2])
        x = tip[0]
        y = tip[1]
        z = tip[2]
        hull.box([5, 4.5, 9], H.base, Placement([x, y - 2.6, z - 12]), H.panel)
        hull.cylinder(1.3, 9.4, 6, H.dark, Placement([x, y, z - 10], 0, QUARTER))
        charge.cylinder(1.35, 0.6, 6, WHITE, Placement([x, y, z - 0.6], 0, QUARTER))
        muzzle(tip, "gun")


def draw_core(p: EnemyParts) -> None:
    """Draw the core body: the inner wings, the body and the guns (the hood is on the plating)."""
    draw_wings(p)
    draw_body(p)
    draw_guns(p)


def boss_drawing(core: Any, parts: Any, turrets: Any, limbs: Any, ring: Any) -> Any:
    """Return the `BossDrawing` of a boss model: what the model is drawn from, with its armour."""
    return record({
        "core": core,
        "parts": parts,
        "turrets": turrets,
        "limbs": limbs,
        "ring": ring,
        "armour": owl_armour(WING, WING_RIME),
    })


def build_snow_owl(scene: Any) -> BuiltEnemyModel:
    """MB-SNOW-OWL-01, MB-SNOW-OWL-04: the Snow Owl.

    A wide-winged recon drone with white neon: snow on its broad wings, two radar pods with turning
    antennas on them and a big round sensor eye at its front. MB-SNOW-OWL-02: now a living owl of
    cold flesh with membrane wings on bone, its radomes grafted on swollen nacelles, its eye a real
    eye in a lid of flesh. Its wing tips and its back plating are its armour (MB-SNOW-OWL-07).
    """
    parts = record({"pod-left": radar_pod, "pod-right": radar_pod, "eye": eye})
    return build_boss_model(
        SNOW_OWL,
        scene,
        OWL_WHITE,
        boss_drawing(draw_core, parts, None, None, None),
    )
