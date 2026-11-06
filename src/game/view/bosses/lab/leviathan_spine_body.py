# Copyright (c) 2026 Renaud Guillon
"""FB-LEVIATHAN-SPINE-02, FB-LEVIATHAN-SPINE-05: the Leviathan Spine's body and its armour.

A very long sea-serpent body along Z, its segmented shell drawn in lengths (`final_boss_shells`):
the core draws the lengths it keeps, its armour the lengths it sheds (its flanks, its back, the
crown of its skull, D-254). Logical pixels, nose +Z, Y up (towards the camera); a config point
`(x, y)` is model `(-x, -y)`.
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.lab.leviathan_spine import BACK_Y, CROWN_Y, FLANKS_Y, ROTOR_AT, TAIL
from game.view.bosses.final_boss_shells import shell_length
from game.view.bosses.world_1_organic_kit import F, M, barbs, graft, polygon, spine, vein_line
from render.geometry.organic import SegmentedBody, segmented_body
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


N = BOSS_LOOK.neon["leviathan-spine"]

# Its body along Z (model): from the tip of its tail to its neck, inside the back of its skull.
BODY_TAIL = -TAIL
BODY_NOSE = 66
SEGMENTS = 9
WIDTH = 15
BOTTOM = -3
TOP = 13
MID = (BOTTOM + TOP) / 2


def girth(t: float) -> float:
    """Its girth from its tail (0) to its neck (1): a long taper to the tail, full from midway."""
    return 0.38 + 0.62 * min(1.0, t * 2.4)


BODY = SegmentedBody(BODY_TAIL, BODY_NOSE, SEGMENTS, WIDTH, BOTTOM, MID, 0.12, girth)
SHELL = SegmentedBody(BODY_TAIL, BODY_NOSE, SEGMENTS, WIDTH * 0.92, MID - 1, TOP, 0.18, girth)
SHELL_COLORS = [F.slate, F.graphite]
# The lengths of shell it sheds (model Z, from tail to nose).
FLANKS_Z = [-FLANKS_Y[1], -FLANKS_Y[0]]
BACK_Z = [-BACK_Y[1], -BACK_Y[0]]
# Its skull's crown plate (the `crown` armour), over the skull from `SKULL_TOP` up.
CROWN_Z = [-CROWN_Y[1], -CROWN_Y[0]]
SKULL_TOP = 7


def top_at(z: float) -> float:
    """Return about how high its shell's ridge is at `z` (model)."""
    t = (z - BODY_TAIL) / (BODY_NOSE - BODY_TAIL)
    return float(MID - 1 + (TOP - MID + 1) * girth(max(0.0, min(1.0, t))))


def draw_shell(b: Any, z0: float, z1: float) -> None:
    """Draw its shell from `z0` to `z1` in `b`: a carapace, its plates seamed."""
    shell_length(b, SHELL, SHELL_COLORS, z0, z1)


def _ridge(p: Any, z0: float, z1: float) -> None:
    """Add the glowing spine vein and the bone spikes of its ridge from `z0` to `z1`."""
    spine(p, [0, top_at(z0) + 0.2, z0], [0, top_at(z1) + 0.2, z1], {"color": N, "width": 1.3})
    count = max(1, math.floor((z1 - z0) / 9))
    for k in range(count):
        z = z0 + (k + 0.5) * (z1 - z0) / count
        barbs(
            p, [0, top_at(z) - 0.6, z], {"count": 1, "spacing": 0, "size": 4, "dir": [0, 1, -0.6]}
        )


def _band(p: Any, z: float, plates: bool) -> None:
    """Add a grafted metal band across its back at `z`, riveted plates on its flanks if `plates`."""
    w = WIDTH * 0.92 * girth((z - BODY_TAIL) / (BODY_NOSE - BODY_TAIL))
    p.hull.cylinder(w * 0.62, 2, 10, M.panel, Placement([0, MID + 1, z - 1], 0, math.pi / 2))
    if plates:
        for s in [-1, 1]:
            graft(p, polygon(4, 3, [0.7, 1.4]), [MID + 2.6, MID + 3.6], [s * w * 0.7, 0, z])


def draw_body(p: Any) -> None:
    """Draw its body (FB-LEVIATHAN-SPINE-02): a long serpent's belly, the shell it keeps.

    Its belly the whole length, the lengths of shell outside its armour, the spine vein and bone
    spikes along its ridge, the glowing lateral line down each flank, metal bands grafted round it.
    """
    segmented_body(p.flesh, BODY, F.graphite)
    keep = [[BODY_TAIL, BACK_Z[0]], [BACK_Z[1], FLANKS_Z[0]], [FLANKS_Z[1], BODY_NOSE]]
    for length in keep:
        draw_shell(p.flesh, length[0], length[1])
    _ridge(p, -88, -72)
    _ridge(p, -56, -40)
    _ridge(p, -14, -2)
    _ridge(p, 22, 34)
    _ridge(p, 50, 58)
    for s in [-1, 1]:
        for k in range(4):
            z0 = -84 + k * 38
            vein_line(p, [s * 11, MID, z0], [s * 13.6, MID, z0 + 34], [s * 1.2, 0, 0], 1.1, N)
    for z in [-66, 44]:
        _band(p, z, True)
    _band(p, -28, False)


def _draw_shell_armour(z: list[Any]) -> Any:
    """Return the drawing of a length of shell it sheds, from `z[0]` to `z[1]` (model)."""

    def draw(p: Any) -> None:
        draw_shell(p.flesh, z[0], z[1])
        mid = (z[0] + z[1]) / 2
        top = top_at(mid)
        spine(p, [0, top + 0.2, z[0] + 1], [0, top + 0.2, z[1] - 1], {"color": N, "width": 1.3})
        barbs(p, [0, top - 0.6, mid], {"count": 1, "spacing": 0, "size": 5, "dir": [0, 1, -0.6]})
        for s in [-1, 1]:
            graft(p, polygon(5, 3, [0.8, 1.5]), [top - 3.4, top - 1.8], [s * 7, 0, mid])

    return draw


def _draw_crown(p: Any) -> None:
    """Draw the crown plate over its skull (the `crown` armour): a horned, ridged bone plate."""
    z0 = CROWN_Z[0]
    z1 = CROWN_Z[1]
    outline = [[-11, z0], [11, z0], [9, z1], [-9, z1]]
    p.flesh.bevel_slab(
        outline, [SKULL_TOP - 0.4, SKULL_TOP + 1.6, SKULL_TOP + 3.6], [0, 1.6], F.bone
    )
    spine(p, [0, SKULL_TOP + 3.7, z0 + 1], [0, SKULL_TOP + 3.7, z1 - 1], {"color": N, "width": 1.2})
    for s in [-1, 1]:
        barbs(
            p,
            [s * 6, SKULL_TOP + 2.6, z0 + 3],
            {"count": 1, "spacing": 0, "size": 6, "dir": [s * 0.3, 0.7, -0.7]},
        )
        vein_line(
            p,
            [s * 3, SKULL_TOP + 3.4, z1 - 2],
            [s * 8, SKULL_TOP + 2.2, z0 + 2],
            [0, 0.4, 0],
            0.8,
            N,
        )


def _draw_hatch(p: Any) -> None:
    """Draw the hatch over its tail rotor (BOSS-58): an armoured cap, a seam of light round it."""
    z = -ROTOR_AT[1]
    p.hull.bevel_slab(polygon(8, 6), [10, 10, 11.6], [0, 0.8], M.panel, Placement([0, 0, z]))
    p.hull.bevel_slab(polygon(8, 4), [11.6, 11.6, 12.6], [0, 0.6], M.base, Placement([0, 0, z]))
    p.neon.ring(5.8, 0.25, 8, N, Placement([0, 11.2, z], math.pi / 8))


def _draw_hatch_frame(p: Any) -> None:
    """Draw what the hatch leaves (BOSS-44): a collar round the opening the rotor rises out of."""
    z = -ROTOR_AT[1]
    p.hull.ring(5.6, 1.4, 12, M.base, Placement([0, 9.6, z]))
    p.neon.ring(5.6, 0.3, 12, N, Placement([0, 10.8, z]))


def spine_armour() -> Any:
    """Return its armour drawings by region id (`drawing.armour`, D-254)."""
    return {
        "flanks": {"whole": _draw_shell_armour(FLANKS_Z)},
        "back": {"whole": _draw_shell_armour(BACK_Z)},
        "crown": {"whole": _draw_crown},
        "rotor-hatch": {"whole": _draw_hatch, "frame": _draw_hatch_frame},
    }
