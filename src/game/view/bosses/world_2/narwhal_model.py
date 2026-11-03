# Copyright (c) 2026 Renaud Guillon
"""The Narwhal (FB-NARWHAL-01 to FB-NARWHAL-06, 2-1).

The final boss of the Ice floes level. Logical pixels, nose +Z, Y up (towards the camera). A long
flying submarine: a round hull with a hump on its back, cruciform tail planes and a shrouded
propeller, teal neon along its back; its spiral horn, torpedo tubes and ballast pods are its parts.
Its back and spine plating are armour drawn apart (`narwhal_armour`, D-254): the core's hull is
flat on top under them (`narwhal_hull`).
"""

import math

from game.config.bosses.world_2.narwhal import NARWHAL, NARWHAL_EMITTER
from game.config.enemy_look import ENEMY_LOOK
from game.config.record import record
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_shapes import edge_strips, shift, turret
from game.view.bosses.world_2.narwhal_armour import back_armour, spine_armour
from game.view.bosses.world_2.narwhal_details import hull_dressing
from game.view.bosses.world_2.narwhal_hull import DECK, N, hull_body
from game.view.bosses.world_2.narwhal_parts import (
    ballast_pod,
    horn_lance,
    torpedo_tube,
)
from game.view.bosses.world_2.w2_organic import (
    ICE_FLESH,
    crystals,
    glow_vein,
    spine_row,
)
from game.view.enemies.enemy_shapes import SIDES, flip_x
from render.geometry.organic import organ
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from game.view.enemies.enemy_mesh import BuiltEnemyModel, EnemyParts

# __pragma__ ("noskip")


H = ENEMY_LOOK.hull
QUARTER = math.pi / 2

# The right stern plane, and the upper and lower rudders (in their own plane, rolled upright).
STERN_PLANE = [  # type: list[list[float]]
    [6, -50],
    [24, -59],
    [25, -65],
    [5, -63],
]
RUDDER = [  # type: list[list[float]]
    [0, -48],
    [13, -58],
    [13, -64],
    [0, -64],
]
# The propeller shroud: a lathe profile out along its outer wall and back along its inner one.
SHROUD = [  # type: list[list[float]]
    [6.4, 0],
    [7, 0.5],
    [7, 6],
    [6.2, 6],
    [6.2, 0.5],
]
# The deck gun's pivot on the forward deck (the core's turret, `NARWHAL["guns"]["core"]`), and the
# height its base turns at: a pedestal of the core holds it there once the spine's plating is gone.
DECK_GUN_Z = 32
DECK_GUN_Y = 15


def draw_hull(p: EnemyParts) -> None:
    """Draw the pressure hull, its teal neon under the chin, the ballast pods' pylons.

    And the deck gun's pedestal, inside the spine's plating at rest.
    """
    hull = p.hull
    flesh = p.flesh
    # FB-NARWHAL-02: a whale's body of cold teal flesh (its ribs and the metal bands grafted round
    # it ride its plating, `narwhal_armour`).
    hull_body(p)
    # A neon line under its chin and along its keel lamps.
    p.neon.box([1, 0.5, 30], N, Placement([0, -7.2, 0]))
    for s in SIDES:
        pylon = [
            [s * 15, -28],
            [s * 33, -24],
            [s * 33, -12],
            [s * 15, -6],
        ]
        flesh.bevel_slab(pylon, [3, 5, 7], [0.5, 1], ICE_FLESH.sinew, None, ICE_FLESH.rime)
    hull.cylinder(6.5, DECK_GUN_Y - DECK + 0.3, 8, H.dark, Placement([0, DECK - 0.3, DECK_GUN_Z]))


def draw_tail(p: EnemyParts) -> None:
    """Draw the cruciform tail: stern planes, rudders, the propeller shroud and its reactor.

    And the ice on the tail's back: the rear spines and a crystal cluster.
    """
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    for s in SIDES:
        # The tail flukes, flesh where the stern planes were.
        plane = STERN_PLANE if s > 0 else flip_x(STERN_PLANE)
        flesh.bevel_slab(plane, [4, 5, 6.5], [0.4, 0.8], ICE_FLESH.teal, None, ICE_FLESH.rime)
        edge_strips(
            neon,
            STERN_PLANE[0:2] if s > 0 else flip_x(STERN_PLANE[0:2]),
            0.8,
            [5.6, 6.6],
            N,
        )
        crystals(flesh, [s * 22, 6, -60], 3, 2)
    flesh.bevel_slab(
        RUDDER,
        [-0.8, 0, 0.8],
        [0.2, 0.4],
        ICE_FLESH.sinew,
        Placement([0, 9, 0], 0, 0, QUARTER),
    )
    flesh.bevel_slab(
        RUDDER,
        [-0.8, 0, 0.8],
        [0.2, 0.4],
        ICE_FLESH.sinew,
        Placement([0, 1, 0], 0, 0, -QUARTER),
    )
    organ(flesh, 6.5, 7, ICE_FLESH.graphite, Placement([0, 5, -72], 0, QUARTER), 0.6)
    hull.lathe(SHROUD, 8, H.dark, Placement([0, 5, -73], 0, QUARTER), False)
    neon.ring(7.2, 0.8, 8, N, Placement([0, 5, -70], 0, QUARTER))
    p.reactor([0, 5, -67], 3.6)
    glow_vein(p, [0, 10, -66], [0, 14, -44], 1.2, N)
    # Rooted in the tail's back, which slopes down towards the propeller (BOSS-52).
    spine_row(flesh, [0, 13.4, -50], [0, 14.3, -43.5], 2, 3.5)
    crystals(flesh, [-9, 12, -48], 3)


def deck_gun(p: EnemyParts, at: list[float]) -> None:
    """Add the deck gun on the forward deck (the core's turret, FB-NARWHAL-03).

    Drawn around its pivot `at`, on its pedestal.
    """
    p.hull.cylinder(6.5, 2, 8, H.dark, Placement(shift(at, [0, DECK_GUN_Y, 0])))
    turret(p, shift(at, [0, DECK_GUN_Y + 1.5, 0]), 7, [2, N])


def draw_core(p: EnemyParts) -> None:
    """Draw the core body: hull, tail and the hull dressing; the emitter's muzzles on the hump."""
    draw_hull(p)
    draw_tail(p)
    hull_dressing(p, N)
    for at in NARWHAL_EMITTER:
        p.muzzle(boss_point(at[0], at[1], at[2]), "ring")


def draw_lance(p: EnemyParts, at: list[float]) -> None:
    """Draw the horn lance, a part."""
    horn_lance(p, at, N)


def draw_tube(p: EnemyParts, at: list[float]) -> None:
    """Draw a torpedo tube on a flank, a part (both flanks)."""
    torpedo_tube(p, at, N)


def draw_pod(p: EnemyParts, at: list[float]) -> None:
    """Draw a ballast pod on its pylon, a part (both sides)."""
    ballast_pod(p, at, N)


def boss_drawing(core: Any, parts: Any, turrets: Any, armour: Any) -> Any:
    """Return the `BossDrawing` of a boss model: what the model is drawn from."""
    return record({
        "core": core,
        "parts": parts,
        "turrets": turrets,
        "limbs": None,
        "ring": None,
        "armour": armour,
    })


def build_narwhal(scene: Any) -> BuiltEnemyModel:
    """FB-NARWHAL-01, FB-NARWHAL-04: the Narwhal.

    A long flying submarine 5 L from its tail to the tip of its spiral horn, teal neon along its
    back; its horn lance, two torpedo tubes on its flanks and two ballast pods on pylons are its
    parts, its deck gun and the emitter on its hump the core's guns.

    FB-NARWHAL-02: now a living cyber-narwhal, a whale of cold flesh, ribbed, with fins and flukes,
    its horn of bone; its torpedo tubes and ballast sacs swell from its flanks, metal grafted on.
    FB-NARWHAL-06: the plating of its back and of its spine (the hump on it) is armour of its own.
    """
    parts = record({
        "lance": draw_lance,
        "tube-left": draw_tube,
        "tube-right": draw_tube,
        "pod-left": draw_pod,
        "pod-right": draw_pod,
    })
    turrets = record({"core": deck_gun})
    armour = record({"back": {"whole": back_armour}, "spine": {"whole": spine_armour}})
    return build_boss_model(
        NARWHAL,
        scene,
        N,
        boss_drawing(draw_core, parts, turrets, armour),
    )
