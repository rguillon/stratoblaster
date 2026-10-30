"""The Floe Breaker's dressing (phase 7 review: detail and some asymmetry) P16-R05: glands down its
flanks, an egg sac to port, a
coiled tow sinew to starboard. Logical pixels, nose +Z, Y up.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.view.bosses.world_2.w2_organic import ICE_FLESH, crystals, gland, sinew
from game.view.enemies.enemy_shapes import SIDES
from render.geometry.organic import organ
from render.geometry.solids import Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402

type Rgb = list[float]
__pragma__("noskip")


def floe_dressing(p: EnemyParts, n: Rgb) -> None:
    """Along the hump: glands lit `n` down its sides, an egg sac to port (+X), a coiled tow sinew
    on the stern to starboard."""
    for s in SIDES:
        for z in [-12, -24]:
            gland(p, [s * 12.6, 6.4, z], 0.8, n)
        crystals(p.flesh, [s * 12, 10, -7], 2.4, 2)
    organ(p.flesh, 3.4, 6, ICE_FLESH.membrane, Placement([17.5, 4, -18], 0, math.pi / 2), 1.4)
    sinew(p.flesh, [15, 5, -22], [17.5, 7, -14], 0.6)
    organ(p.flesh, 2.6, 5, ICE_FLESH.sinew, Placement([-9, 4, -40]), 0.8)
    sinew(p.flesh, [-12, 4, -40], [-5, 3, -44], 0.8, ICE_FLESH.sinew, [0, 0, -3])
