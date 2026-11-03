# Copyright (c) 2026 Renaud Guillon
"""FB-OVERLORD-05 (D-254): the Overlord's armour, drawn as pieces of its own.

Its mantle (the deck) is a slab in two layers: the lower one (the core's, up to `PLATE_Y[0]`) runs
the whole deck, its neon rim on it; the upper one (up to the deck's top) is split into a centre
strip (the core's, `draw_centre`), the flank plates out to the deck's edge with the city standing
on them (`flanks`, shed first) and the front plate before the citadel with the front of the
boulevard (`spine`, shed second). The raised boulevard is cut in two the same way at `FRONT_Z`.
Logical pixels, nose +Z, Y up (towards the camera); outlines are the right side's (+X), the left
side is their mirror image.
"""

from game.config.boss_look import BOSS_LOOK
from game.view.bosses.boss_armour import plate_pieces
from game.view.bosses.final_boss_shapes import sided
from game.view.bosses.overlord_city import OVERLORD_DECK, OVERLORD_NEON, symmetric
from game.view.bosses.overlord_skyline import draw_flank_city, draw_front_towers
from game.view.bosses.world_1_organic_kit import F, M, barbs, graft, polygon, rib_cage, vein_line
from game.view.enemies.enemy_shapes import SIDES, flip_x
from render.geometry.organic import vein
from render.geometry.outline import reversed_copy

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


N = OVERLORD_NEON
TOP = OVERLORD_DECK["top"]
BOULEVARD_Y = [TOP - 1, OVERLORD_DECK["boulevard"]]
# Heights of the deck's upper layer (the plating) on the lower one, up to the deck's top.
PLATE_Y = [3, TOP]
# Where the front plate begins (model Z), before the citadel's weapon array.
FRONT_Z = 34

# The deck (right half, front to tail).
DECK = symmetric(
    [
        [26, 60],
        [52, 42],
        [64, 18],
        [64, -30],
        [52, -50],
        [36, -60],
    ],
    64,
)
# The upper layer's centre strip: between the flank plates, behind the front plate.
CENTRE = symmetric(
    [
        [32, FRONT_Z],
        [32, -32],
        [62.8, -32],
        [52, -50],
        [36, -60],
    ],
)
# The right flank plate, from the city's edge out to the deck's.
FLANK_PLATE = [
    [32, 42],
    [52, 42],
    [64, 18],
    [64, -30],
    [62.8, -32],
    [32, -32],
]
# The front plate, before the citadel, out to the deck's edge in front of the flank plates.
FRONT_PLATE = symmetric(
    [
        [26, 60],
        [52, 42],
        [32, 42],
        [32, FRONT_Z],
    ],
    64,
)
# The raised boulevard's right side: behind the cut (from the cut back) and before it.
BOULEVARD_EDGE = 18 - (FRONT_Z - 26) / 28 * 4
BOULEVARD_BACK = [
    [BOULEVARD_EDGE, FRONT_Z],
    [18, 26],
    [26, -10],
    [26, -46],
    [16, -54],
]
BOULEVARD_FRONT = [
    [14, 54],
    [BOULEVARD_EDGE, FRONT_Z],
]
# The veins across the flank plates (their Z on the boulevard).
FLANK_VEINS = [-6, 30]


def draw_plating(p: Any, outline: list[Any]) -> None:
    """Draw a length of the deck's upper layer in `outline`: dark flesh, bevelled to the top."""
    p.flesh.bevel_slab(outline, [PLATE_Y[0], PLATE_Y[0], PLATE_Y[1]], [0, 2.5], F.graphite)


def draw_lower_deck(p: Any) -> None:
    """Draw the deck's lower layer (FB-OVERLORD-02), under the whole of its plating."""
    p.flesh.bevel_slab(DECK, [-8, -1, PLATE_Y[0]], [1.5, 0], F.graphite)


def _boulevard(p: Any, half: list[Any], closed: bool) -> None:
    """Draw a length of the raised boulevard from its right side `half`, its rim lit.

    `closed`: the length is closed across the nose (the front one) rather than along the cut.
    """
    outline = symmetric(half, 56) if closed else symmetric(half)
    p.flesh.bevel_slab(outline, [BOULEVARD_Y[0], 7.5, BOULEVARD_Y[1]], [1.5, 2.5], F.slate)
    rim: list[Any] = []
    if closed:
        rim.extend(reversed_copy(flip_x(half)))
        rim.append([0, 56])
        rim.extend(half)
    else:
        rim.extend(half)
        rim.extend(reversed_copy(flip_x(half)))
    y = 7.5 + 0.2
    vein(p.vein, [[q[0] * 1.005, y, q[1] * 1.005] for q in rim], 0.9, N)


def draw_centre(p: Any) -> None:
    """Draw the upper layer's centre strip and the boulevard behind the cut (the core's)."""
    draw_plating(p, CENTRE)
    _boulevard(p, BOULEVARD_BACK, False)


def draw_flanks(p: Any) -> None:
    """Draw the flank plates, both sides (the `flanks` armour, FB-OVERLORD-05).

    The deck's upper layer out to its edge (3 to 6 px), the veins across it from the boulevard
    and the city standing on it: towers, the broadcast spire, the billboard and the command stalk.
    The lances lie folded under them.
    """
    boulevard = BOULEVARD_Y[1]
    for s in SIDES:
        draw_plating(p, sided(FLANK_PLATE, s))
        for z in FLANK_VEINS:
            vein_line(p, [s * 24, boulevard, z], [s * 60, TOP + 0.2, z + 6], [0, 2, 0], 1.3, N)
    draw_flank_city(p)


def draw_front(p: Any) -> None:
    """Draw the front plate (the `spine` armour, FB-OVERLORD-05).

    The deck's upper layer before the citadel (3 to 6 px), the boulevard's front (5 to 10 px), the
    front rib, grafted plates, the barbs at its nose and the two towers there. The mortars lie
    folded under it.
    """
    draw_plating(p, FRONT_PLATE)
    _boulevard(p, BOULEVARD_FRONT, True)
    rib_cage(p, [44], {"halfWidth": 30, "y": TOP - 1, "height": 7, "thickness": 1.3})
    for s in SIDES:
        graft(
            p, polygon(5, 6, [1.4, 1]), [TOP - 0.4, TOP + 0.8], [s * 30, 0, 44], {"color": M.base}
        )
    barbs(p, [0, TOP, 58], {"count": 5, "spacing": 8, "size": 4, "dir": [0, -0.2, 1]})
    draw_front_towers(p)


def overlord_armour() -> Any:
    """Return the Overlord's armour drawings by region id (`drawing.armour`, D-254)."""
    return {
        "flanks": {"whole": draw_flanks, "pieces": _flank_pieces()},
        "spine": {"whole": draw_front},
    }


def _flank_pieces() -> list[Any]:
    """Return the plates the flank plating bursts into, at its own height (3 to 6 px).

    The towers on it would put the default plates up at their roofs.
    """
    outlines = [sided(FLANK_PLATE, s) for s in SIDES]
    most: int = BOSS_LOOK.armour.chunks
    heights = [float(PLATE_Y[0]), float(PLATE_Y[1])]
    return [piece[0] for piece in plate_pieces(outlines, heights, F.graphite, most)]
