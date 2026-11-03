# Copyright (c) 2026 Renaud Guillon
"""FB-REFINERY-TITAN-05 (D-254): the Refinery Titan's armour, drawn as pieces of its own.

Its abdomen's shell is one carapace drawn in lengths along Z (`final_boss_shells`): the core keeps
the length over its tail (behind `BACK_Z[0]`); the `back` armour is the middle length, with the
plated skull over the core riding it (its eyes, spiracles and twin cannon), and the `spine` armour
is the front length out to its nose, with its front rib and eyes. Under them the core is its belly
(up to about 5 px) between the two lobes of its apron. Logical pixels, nose +Z, Y up (towards the
camera).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.view.bosses.boss_armour import plate_pieces
from game.view.bosses.final_boss_shells import shell_body, shell_length
from game.view.bosses.refinery_titan_parts import TITAN_NEON
from game.view.bosses.world_1_organic_kit import F, M, graft, polygon, rib_cage, spine, vein_line
from game.view.enemies.enemy_shapes import SIDES
from game.view.enemies.organic_parts import eyes
from render.geometry.organic import organ
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


WHITE = [1, 1, 1]
QUARTER = math.pi / 2

# The abdomen: from its tail to its nose, `WIDTH` half-wide, its belly from `BOTTOM` to `MID` and
# its shell from `MID` - 1 to `TOP` (as `world_1_organic_kit.hide` draws a body).
TAIL = -62
NOSE = 68
SEGMENTS = 6
WIDTH = 36
BOTTOM = -8
TOP = 18
MID = (BOTTOM + TOP) / 2
SHELL = shell_body(TAIL, NOSE, SEGMENTS, WIDTH, BOTTOM, TOP)
SHELL_COLORS = [F.sinew, F.slate]
# Where the back plating and the spine plating lie along the abdomen (model Z).
BACK_Z = [-20, 24]
SPINE_Z = [24, NOSE]


def draw_rear_shell(p: Any) -> None:
    """Draw the length of shell the core keeps, over the tail, and the spine vein along it."""
    shell_length(p.flesh, SHELL, SHELL_COLORS, TAIL, BACK_Z[0])
    spine(p, [0, 14.6, -50], [0, 16.4, -22], {"color": TITAN_NEON, "width": 1.8, "bow": 0.6})


def _draw_skull(p: Any) -> None:
    """Draw the plated skull over the core: clustered eyes, two smoking spiracles, a mantlet."""
    organ(p.flesh, 17, 8, F.slate, Placement([0, 12, 2], math.pi / 8), 0.38)
    graft(p, polygon(6, 11, [1, 1.3]), [23, 24.5], [0, 0, 0])
    eyes(p, [0, 22, 15], {"count": 4, "size": 1.2, "spacing": 3.4}, TITAN_NEON)
    for s in SIDES:
        p.flesh.cylinder(3.2, 8, 6, F.sinew, Placement([s * 9, 22, -14]), 2.6)
        p.neon.ring(2.7, 0.8, 6, TITAN_NEON, Placement([s * 9, 29.5, -14]))
    p.hull.box([15, 4, 7], M.base, Placement([0, 17, 21]), M.panel)


def _draw_cannon(p: Any) -> None:
    """Draw the twin cannon's barrels out of the skull's mantlet (FB-REFINERY-TITAN-03).

    Their muzzles are marked by the core (`draw_cannon_muzzles`): the core keeps firing from them.
    """
    for s in SIDES:
        p.hull.cylinder(1.8, 14, 6, M.dark, Placement([s * 4.5, 19, 20], 0, QUARTER))
        p.charge.cylinder(2.2, 1.8, 6, WHITE, Placement([s * 4.5, 19, 34], 0, QUARTER))


def draw_cannon_muzzles(p: Any) -> None:
    """Mark the twin cannon's muzzles, at its barrels' tips (the core's gun)."""
    for s in SIDES:
        p.muzzle([s * 4.5, 19, 35.8], None)


def draw_back(p: Any) -> None:
    """Draw the back plating (the `back` armour, FB-REFINERY-TITAN-05).

    The middle length of the shell (from about 4 px up to its ridge, 18 px), the spine vein, the
    veins and grafted plates on it, and the plated skull riding it with the twin cannon. The
    gatlings lie folded under it.
    """
    shell_length(p.flesh, SHELL, SHELL_COLORS, BACK_Z[0], BACK_Z[1])
    spine(p, [0, 17, -18], [0, 17.4, 23], {"color": TITAN_NEON, "width": 1.8, "bow": 0.6})
    for s in SIDES:
        graft(p, polygon(6, 6, [1.2, 1.8]), [13, 14.6], [s * 20, 0, 8], {"color": M.base})
        vein_line(p, [s * 12, 17, -14], [s * 28, 8, -8], [s * 3, 3, 0], 1.4, TITAN_NEON)
    _draw_skull(p)
    _draw_cannon(p)


def draw_spine(p: Any) -> None:
    """Draw the spine plating (the `spine` armour, FB-REFINERY-TITAN-05).

    The front length of the shell out to its nose (from about 5 px up to 17 px), its front rib and
    the eyes at its front. The orbs lie folded under it.
    """
    shell_length(p.flesh, SHELL, SHELL_COLORS, SPINE_Z[0], SPINE_Z[1])
    rib_cage(p, [50], {"halfWidth": 30, "y": 4, "height": 11, "thickness": 1.5})
    eyes(p, [0, 6.5, 60], {"count": 2, "size": 1.2, "spacing": 6}, TITAN_NEON)


# The back plating's top view in model space (the `back` region's outline, X and Y negated).
BACK_PLAN = [[27, -20], [-27, -20], [-32, -8], [-32, 14], [-27, 24], [27, 24], [32, 14], [32, -8]]


def _back_pieces() -> list[Any]:
    """Return the plates the back plating bursts into, at the shell's ridge (15.5 to 18 px).

    The skull riding it would put the default plates up at its crown.
    """
    most: int = BOSS_LOOK.armour.chunks
    plates = plate_pieces([BACK_PLAN], [TOP - BOSS_LOOK.armour.plate, TOP], F.slate, most)
    return [piece[0] for piece in plates]


def titan_armour() -> Any:
    """Return the Refinery Titan's armour drawings by region id (`drawing.armour`, D-254)."""
    return {
        "back": {"whole": draw_back, "pieces": _back_pieces()},
        "spine": {"whole": draw_spine},
    }
