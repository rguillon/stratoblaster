# Copyright (c) 2026 Renaud Guillon
"""FB-STORM-PETREL-05 (D-254): the Storm Petrel's armour, drawn as pieces of its own.

Its body's shell is one carapace drawn in lengths along Z (`draw_shell`): the core draws it short
of the tail region, and the `tail` armour is the length over the tail, with the spine vein and the
barbs on it. Its wing roots (the `wing-roots` armour) and its outer wings (the `outer-wings`
moving pieces) are in `storm_petrel_wings`. Logical pixels, nose +Z, Y up (towards the camera).
"""

from game.config.boss_look import BOSS_LOOK
from game.view.bosses.final_boss_shells import shell_length
from game.view.bosses.storm_petrel_wings import outer_wing, wing_root
from game.view.bosses.world_1_organic_kit import F, barbs, spine
from render.geometry.organic import SegmentedBody

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


N = BOSS_LOOK.neon["storm-petrel"]

# The body: from its tail to its beak, `WIDTH` half-wide, its belly from `BOTTOM` to `MID` and its
# shell from `MID` - 1 to `TOP` (as `world_1_organic_kit.hide` draws a body).
TAIL = -64
NOSE = 56
SEGMENTS = 7
WIDTH = 14
BOTTOM = -4
TOP = 15
MID = (BOTTOM + TOP) / 2
# The shell's plates have a seam every other band (`carapace`).
SHELL_PINCH = 0.12
SHELL = SegmentedBody(TAIL, NOSE, SEGMENTS, WIDTH * 0.92, MID - 1, TOP, SHELL_PINCH)
SHELL_COLORS = [F.graphite, F.membrane]
# Where the tail plating lies along the body (model Z).
TAIL_Z = [-48, -18]


def draw_shell(b: Any, z0: float, z1: float) -> None:
    """Draw the body's shell from `z0` to `z1` in `b`: a carapace, its plates seamed."""
    shell_length(b, SHELL, SHELL_COLORS, z0, z1)


def draw_tail_plating(p: Any) -> None:
    """Draw the tail plating (FB-STORM-PETREL-05): the length of shell over the tail.

    From the shell's own bottom (about 5 px) up to its ridge (about 15 px), the magenta vein down
    its spine and the bone barbs on it. The cannon lies folded under it.
    """
    draw_shell(p.flesh, TAIL_Z[0], TAIL_Z[1])
    spine(p, [0, 13.4, -46], [0, 15.3, -20], {"color": N, "width": 1.4, "bow": 1.5})
    barbs(p, [0, 14, -32], {"count": 3, "spacing": 0.1, "size": 4, "dir": [0, 1, -0.5]})


def petrel_armour() -> Any:
    """Return the Storm Petrel's armour drawings by region id (`drawing.armour`, D-254).

    The config's right side (+X) is model -X.
    """
    return {
        "outer-wings-right": {"whole": outer_wing(-1)},
        "outer-wings-left": {"whole": outer_wing(1)},
        "tail": {"whole": draw_tail_plating},
        "wing-roots": {"whole": _wing_roots},
    }


def _wing_roots(p: Any) -> None:
    """Draw both wing roots: the `wing-roots` region is mirrored, one piece for both sides."""
    wing_root(-1)(p)
    wing_root(1)(p)
