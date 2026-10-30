"""P10-R11, 4-4: the Foundry Ark's yard, the heavy industry on its deck around the furnace: casting
sheds with lit windows, ore wagons on their rails, pipe runs, molten seams between the plates. Model
space: logical pixels, nose +Z, Y up; drawn for the
right side (+X) and mirrored.
"""

from org.transcrypt.stubs.browser import __pragma__

from game.view.bosses.final_boss_greebles import rod  # noqa: E402
from game.view.bosses.mini_boss_greebles import seam  # noqa: E402
from game.view.bosses.mini_boss_shapes import SHADE, H  # noqa: E402
from game.view.bosses.world_4.foundry_ark_parts import (  # noqa: E402
    ARK_ORANGE,
    DECK_TOP,
    MOLTEN,
    SOOT,
)
from game.view.bosses.world_4.living_forge import SKIN  # noqa: E402
from game.view.enemies.enemy_shapes import SIDES  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Vec3 = list[float]
__pragma__("noskip")

# The casting sheds along the deck's sides (right side): centre, width, length, height.
SHEDS = [
    [38.0, -62.0, 14.0, 22.0, 9.0],
    [42.0, 0.0, 10.0, 20.0, 7.0],
]
# The ore wagons on the rails between the furnace and the battery (centre along Z).
WAGONS = [42.0, 56.0]
# The deck plates' molten seams (right side): glowing cracks where the plates meet.
SEAMS = [
    [
        [22.0, 30.0],
        [46.0, 52.0],
    ],
    [
        [20.0, -36.0],
        [26.0, -84.0],
    ],
    [
        [50.0, -30.0],
        [56.0, 6.0],
    ],
]
# The pipe runs from the furnace to the chimney row (right side): from, bend, to.
PIPE = [
    [14.0, DECK_TOP + 8.0, 14.0],
    [20.0, DECK_TOP + 6.0, 28.0],
    [17.0, DECK_TOP + 6.0, 42.0],
]


def _shed(p: Any, s: float, spec: list[float]) -> None:
    """A casting shed: a long block with a sawtooth roof, a row of furnace-lit windows."""
    hull = p.hull
    neon = p.neon
    flesh = p.flesh
    x = spec[0]
    z = spec[1]
    w = spec[2]
    d = spec[3]
    h = spec[4]
    # P16-R06: a swollen flesh growth, metal ribs across its top.
    flesh.box([w, h, d], SKIN.base, Placement([s * x, DECK_TOP, z]), SKIN.panel)
    for dz in [-d / 3, 0, d / 3]:
        hull.box([w * 0.9, 2, 2], H.panel, Placement([s * x, DECK_TOP + h, z + dz], 0, 0, s * 0.35))
    neon.box(
        [0.4, 1.2, d * 0.8],
        ARK_ORANGE,
        Placement([s * (x - w / 2 - 0.2), DECK_TOP + h / 2, z]),
    )


def _wagon(p: Any, z: float) -> None:
    """An ore wagon on the rails, heaped with glowing ore."""
    hull = p.hull
    neon = p.neon
    hull.box([7, 3.2, 10], H.dark, Placement([0, DECK_TOP + 0.6, z]), SHADE["edge"])
    neon.box([5, 0.6, 7.6], MOLTEN, Placement([0, DECK_TOP + 3.6, z]))
    hull.box([5.4, 1, 3], SOOT, Placement([0, DECK_TOP + 4, z]))


def draw_yard(p: Any) -> None:
    """The yard on the deck: sheds, wagons, pipe runs and glowing seams between the plates."""
    flesh = p.flesh
    neon = p.neon
    for s in SIDES:
        for spec in SHEDS:
            _shed(p, s, spec)
        for pair in SEAMS:
            a = pair[0]
            b = pair[1]
            seam(neon, [s * a[0], a[1]], [s * b[0], b[1]], [DECK_TOP, 0.5, 0.15], MOLTEN)
        side = [[s * q[0], q[1], q[2]] for q in PIPE]
        for i in range(1, len(side)):
            rod(flesh, side[i - 1], side[i], 1.3, SKIN.panel)
    for z in WAGONS:
        _wagon(p, z)
