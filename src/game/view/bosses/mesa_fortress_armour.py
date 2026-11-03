# Copyright (c) 2026 Renaud Guillon
"""FB-MESA-FORTRESS-05 (D-254): the Mesa Fortress's armour and roof, drawn as pieces of their own.

Its skirt of hide is a slab in two layers: the lower one (the core's, up to `PLATE_Y[0]`) runs the
whole skirt; the upper one (up to `BASE_TOP`) is split into a centre strip (the core's,
`draw_centre`) and the flank plates (the armour): the front flanks either side of the head
(`wings`, shed first, the rim's neon on them) and the rear flanks with the forelimbs' scaly sinews
(`flanks`, shed second). Its keep (the upper shell, on the flat top of the lower one) is drawn as
two halves cut along its ridge (`roof-right`, `roof-left`), each a half-section loft carrying a
ridge vein, a gland and grafted plates: they slide apart at the second transformation. Logical
pixels, nose +Z, Y up (towards the camera); outlines are the right side's (+X), the left side is
their mirror image.
"""

from game.config.boss_look import BOSS_LOOK
from game.view.bosses.final_boss_mesa import BASE_TOP
from game.view.bosses.final_boss_shapes import edge_strips, mirrored, sided
from game.view.bosses.world_1_organic_kit import F, M, gland, graft, polygon, spine, tentacle
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.organic import (
    ROUND_SECTION,
    SHELL_SECTION,
    SegmentedBody,
    segment_stations,
    vein,
)
from render.geometry.solids import LoftOptions

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


N = BOSS_LOOK.neon["mesa-fortress"]

# Heights of the skirt's upper layer (the plating) on the lower one, up to the skirt's top.
PLATE_Y = [5, BASE_TOP]
# The skirt of hide (right half, front to back): the silos stand on its rear, the batteries rise
# at its front shoulders.
BASE_HALF = [
    [0, 48],
    [22, 46],
    [38, 38],
    [46, 28],
    [46, -36],
    [34, -50],
    [0, -54],
]
BASE = mirrored(BASE_HALF)
# The upper layer's centre strip, between the flank plates.
CENTRE = mirrored([
    [0, 48],
    [16, 46.5],
    [16, 3.5],
    [34, 3.5],
    [34, -50],
    [0, -54],
])
# The right front flank plate (either side of the head, out to the rim) and rear flank plate.
WING_PLATE = [
    [16, 46.5],
    [22, 46],
    [38, 38],
    [46, 28],
    [46, 3.5],
    [16, 3.5],
]
FLANK_PLATE = [
    [34, 3.5],
    [46, 3.5],
    [46, -36],
    [34, -50],
]
# The rim's neon on the right front flank (the middle length, across the head, is the core's).
WING_RIM = [
    [19, 41.5],
    [34, 28.5],
]
# The keep: the upper shell along the ridge, standing on the lower shell's flat top (`KEEP_Y[0]`),
# as `world_1_organic_kit.hide` draws a body (its belly to the middle, its carapace over it).
KEEP_Z = [-36, 18]
KEEP_WIDTH = 22
KEEP_Y = [17, 30]
KEEP_MID = (KEEP_Y[0] + KEEP_Y[1]) / 2
KEEP_BELLY = SegmentedBody(KEEP_Z[0], KEEP_Z[1], 3, KEEP_WIDTH, KEEP_Y[0], KEEP_MID, 0.15)
KEEP_SHELL = SegmentedBody(
    KEEP_Z[0], KEEP_Z[1], 3, KEEP_WIDTH * 0.92, KEEP_MID - 1, KEEP_Y[1], 0.12
)
KEEP_COLORS = [F.sinew, F.slate]
# Grafted armour plates on each roof half (x, z, radius) and their heights, sunk in its shell.
ROOF_PLATES = [
    [8, -14, 6, [27.6, 29]],
    [9, 4, 5, [27, 28.4]],
]


def half_section(section: list[Any], s: float) -> list[Any]:
    """Return the half of a loft `section` on side `s`, closed along its axis.

    The half keeps the section's winding: from the axis at the bottom, out and up to the ridge.
    """
    half = [q for q in section if q[0] * s > 0]
    result: list[Any] = [[0, 0]]
    if s > 0:
        result.extend(half)
        result.append([0, 1])
    else:
        result.append([0, 1])
        result.extend(half)
    return result


def half_body(b: Any, body: SegmentedBody, section: list[Any], color: Any, s: float) -> None:
    """Draw the half of `body` on side `s` in `b`: `section` cut along the axis, flat inside."""
    b.loft(half_section(section, s), segment_stations(body), color, None, None)


def half_shell(b: Any, body: SegmentedBody, colors: list[Any], s: float) -> None:
    """Draw the half of a carapace over `body` on side `s`, its plates seamed (as `carapace`)."""

    def paint(_side: int, band: int) -> Any:
        return colors[1] if band % 2 == 1 else None

    b.loft(
        half_section(SHELL_SECTION, s),
        segment_stations(body),
        colors[0],
        None,
        LoftOptions(False, paint),
    )


def draw_plating(p: Any, outline: list[Any]) -> None:
    """Draw a length of the skirt's upper layer in `outline`: hide, bevelled to the top."""
    p.flesh.bevel_slab(outline, [PLATE_Y[0], PLATE_Y[0], PLATE_Y[1]], [0, 2.5], F.sinew)


def draw_skirt(p: Any) -> None:
    """Draw the skirt's lower layer (FB-MESA-FORTRESS-02): hide, its rim lined by a vein."""
    p.flesh.bevel_slab(BASE, [-6, 0.5, PLATE_Y[0]], [1.5, 0], F.sinew)
    ring: list[Any] = []
    ring.extend(BASE)
    ring.append(BASE[0])
    vein(p.vein, [[q[0] * 1.005, 0.7, q[1] * 1.005] for q in ring], 0.9, N)


def draw_centre(p: Any) -> None:
    """Draw the upper layer's centre strip, between the flank plates, and the rim's neon across."""
    draw_plating(p, CENTRE)
    edge_strips(p.neon, [[-19, 41.5], [19, 41.5]], 1.2, [BASE_TOP - 0.2, BASE_TOP + 0.5], N)


def draw_wings(p: Any) -> None:
    """Draw the front flank plates, both sides (the `wings` armour, FB-MESA-FORTRESS-05).

    The skirt's upper layer either side of the head (5 to 7 px), the rim's neon along each. The
    batteries lie folded under them.
    """
    for s in SIDES:
        draw_plating(p, sided(WING_PLATE, s))
        edge_strips(p.neon, sided(WING_RIM, s), 1.2, [BASE_TOP - 0.2, BASE_TOP + 0.5], N)


def draw_flanks(p: Any) -> None:
    """Draw the rear flank plates, both sides (the `flanks` armour, FB-MESA-FORTRESS-05).

    The skirt's upper layer along each rear flank (5 to 7 px), and the forelimb's scaly sinew lying
    on the limb (5 to 13 px) with its grafted plate. The sweepers lie folded under the sinews.
    """
    for s in SIDES:
        draw_plating(p, sided(FLANK_PLATE, s))
        tentacle(p, [s * 36, 10, -15], [s * 76, 8.5, -14], [0, 3, 0], [5, 3.5], F.slate, 5)
        graft(p, polygon(4, 5, [2, 0.9]), [8.5, 9.6], [s * 56, 0, -16])


def roof_half(s: float) -> Any:
    """Return the drawing of the keep's roof half on side `s` (a `roof` moving piece).

    The upper shell cut along its ridge, from the lower shell's flat top (17 px) to the ridge
    (30 px): a vein along the ridge, a gland on its flank, two grafted plates sunk in it.
    """

    def draw(p: Any) -> None:
        half_body(p.flesh, KEEP_BELLY, ROUND_SECTION, F.slate, s)
        half_shell(p.flesh, KEEP_SHELL, KEEP_COLORS, s)
        spine(p, [s * 3, 29.6, -30], [s * 3, 29.6, 12], {"color": N, "width": 1.6, "bow": 1})
        gland(p, [s * 12, 27.4, 0], 2.2, N)
        roof_plates: list[Any] = ROOF_PLATES
        for plate in roof_plates:
            graft(
                p,
                polygon(6, plate[2], [1, 1.3]),
                plate[3],
                [s * plate[0], 0, plate[1]],
                {"color": M.base},
            )

    return draw


def mesa_armour() -> Any:
    """Return the Mesa Fortress's armour drawings by region id (`drawing.armour`, D-254).

    The config's right side (+X) is model -X.
    """
    return {
        "wings": {"whole": draw_wings},
        "roof-right": {"whole": roof_half(-1)},
        "roof-left": {"whole": roof_half(1)},
        "flanks": {"whole": draw_flanks},
    }
