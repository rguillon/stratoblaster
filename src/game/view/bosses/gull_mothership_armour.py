# Copyright (c) 2026 Renaud Guillon
"""FB-GULL-MOTHERSHIP-05 (D-254): the Gull Mothership's armour, drawn as pieces of its own.

Its mantle is a teal slab in two layers: the lower one (the core's, up to `PLATE_Y[0]`) runs the
whole mantle; the upper one (up to `DECK_TOP`), with the graphite fold on it, is split into a
centre strip (the core's, `draw_centre`) and the flank plates (the armour): the rear flanks, behind
the middle, with the swim bladders on them (`flanks`, shed first), and the front flanks with their
grafted plates (`wings`, shed second). The veins across the mantle lie on the plates they cross.
Logical pixels, nose +Z, Y up (towards the camera); the outlines are the right side's (+X), the
left side is their mirror image.
"""

from game.config.boss_look import BOSS_LOOK
from game.view.bosses.final_boss_shapes import mirrored, sided
from game.view.bosses.world_1_organic_kit import F, graft, polygon, vein_line
from game.view.enemies.enemy_shapes import SIDES
from game.view.enemies.organic_parts import reactor_sac
from render.geometry.organic import SegmentedBody, segmented_body, vein
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


N = BOSS_LOOK.neon["gull-mothership"]

# Height of the mantle's top, and of its upper layer (the plating) on the lower one.
DECK_TOP = 4
PLATE_Y = [1.9, DECK_TOP]
# The graphite fold on the mantle: its heights, and its bevel (as `world_1_organic_kit.mantle`).
FOLD_Y = [3, 4.3, 5.6]
FOLD_INSETS = [1.5, 2.5]
# The mantle seen from above (right half, front to back); the pouches sit on its flat sides.
DECK_HALF = [
    [0, 50],
    [24, 46],
    [40, 32],
    [47, 20],
    [47, -30],
    [34, -48],
    [14, -56],
    [0, -56],
]
DECK = mirrored(DECK_HALF)
# The upper layer's centre strip: the mantle between the flank plates, and its front.
CENTRE = mirrored([
    [0, 50],
    [24, 46],
    [33.1, 38],
    [22, 38],
    [22, -6],
    [18, -6],
    [18, -54.4],
    [14, -56],
    [0, -56],
])
# The fold's centre strip (the fold is the mantle at 0.72, moved 4 px back, cut at the plates).
FOLD_CENTRE = mirrored([
    [0, 32],
    [17.3, 29.1],
    [22, 25],
    [22, -6],
    [18, -6],
    [18, -41.2],
    [10.1, -44.3],
    [0, -44.3],
])
# The right rear flank plate (x 18 out to the rim, behind z -6) and the fold on it.
FLANK_PLATE = [
    [18, -6],
    [47, -6],
    [47, -30],
    [34, -48],
    [18, -54.4],
]
FLANK_FOLD = [
    [18, -6],
    [33.8, -6],
    [33.8, -25.6],
    [24.5, -38.6],
    [18, -41.2],
]
# The right front flank plate (x 22 out to the rim, z -6 to 38) and the fold on it.
WING_PLATE = [
    [22, -6],
    [47, -6],
    [47, 20],
    [40, 32],
    [33.1, 38],
    [22, 38],
]
WING_FOLD = [
    [22, -6],
    [33.8, -6],
    [33.8, 10.4],
    [28.8, 19],
    [22, 25],
]
# Where the veins across the mantle run (Z at the body), by the plate they lie on.
FLANK_VEINS = [-34, -14]
WING_VEINS = [6, 26]


def draw_plating(p: Any, outline: list[Any]) -> None:
    """Draw a length of the mantle's upper layer in `outline`: teal, bevelled to the top."""
    p.flesh.bevel_slab(outline, [PLATE_Y[0], PLATE_Y[0], PLATE_Y[1]], [0, 2.5], F.teal)


def draw_fold(p: Any, outline: list[Any]) -> None:
    """Draw a length of the graphite fold in `outline`, on the upper layer."""
    p.flesh.bevel_slab(outline, FOLD_Y, FOLD_INSETS, F.graphite)


def draw_mantle(p: Any) -> None:
    """Draw the mantle's lower layer (FB-GULL-MOTHERSHIP-02): teal, its rim lined by a vein."""
    p.flesh.bevel_slab(DECK, [-5, -0.5, PLATE_Y[0]], [1.5, 0], F.teal)
    ring: list[Any] = []
    ring.extend(DECK)
    ring.append(DECK[0])
    vein(p.vein, [[q[0] * 1.005, -0.3, q[1] * 1.005] for q in ring], 0.9, N)


def draw_centre(p: Any) -> None:
    """Draw the upper layer's centre strip and the fold's, between the flank plates."""
    draw_plating(p, CENTRE)
    draw_fold(p, FOLD_CENTRE)


def _vein_across(p: Any, s: float, z: float) -> None:
    """Draw a vein across the mantle on side `s`, from the body's flank out at `z`."""
    vein_line(p, [s * 15, DECK_TOP + 6, z], [s * 40, DECK_TOP + 1, z - 8], [0, 3, 0], 1.1, N)


def _flank(p: Any, s: float) -> None:
    """Draw a rear flank plate on side `s`: the swim bladder on it, its reactor in a sac."""
    draw_plating(p, sided(FLANK_PLATE, s))
    draw_fold(p, sided(FLANK_FOLD, s))
    segmented_body(
        p.flesh,
        SegmentedBody(-51, -24, 2, 5.5, 0, 9.5),
        F.slate,
        Placement([s * 30, DECK_TOP - 1, 0]),
    )
    reactor_sac(p, [s * 30, DECK_TOP + 3, -50], 3.4, N)
    for z in FLANK_VEINS:
        _vein_across(p, s, z)


def _wing(p: Any, s: float) -> None:
    """Draw a front flank plate on side `s`: a grafted plate on it."""
    draw_plating(p, sided(WING_PLATE, s))
    draw_fold(p, sided(WING_FOLD, s))
    graft(p, polygon(4, 5, [1.6, 0.9]), [DECK_TOP + 1.4, DECK_TOP + 2.4], [s * 30, 0, 22])
    for z in WING_VEINS:
        _vein_across(p, s, z)


def draw_flanks(p: Any) -> None:
    """Draw the rear flank plates, both sides (the `flanks` armour, FB-GULL-MOTHERSHIP-05).

    The mantle's upper layer behind the middle (1.9 to 4 px) with the fold on it, the swim bladders
    (up to 12.5 px) and their reactors, the two rear veins. The lances lie folded under them.
    """
    for s in SIDES:
        _flank(p, s)


def draw_wings(p: Any) -> None:
    """Draw the front flank plates, both sides (the `wings` armour, FB-GULL-MOTHERSHIP-05).

    The mantle's upper layer in front of the middle (1.9 to 4 px) with the fold and a grafted
    plate on it, the two front veins. The orbs lie folded under them.
    """
    for s in SIDES:
        _wing(p, s)


def gull_armour() -> Any:
    """Return the Gull Mothership's armour drawings by region id (`drawing.armour`, D-254)."""
    return {"flanks": {"whole": draw_flanks}, "wings": {"whole": draw_wings}}
