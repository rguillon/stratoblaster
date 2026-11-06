# Copyright (c) 2026 Renaud Guillon
"""FB-GULL-MOTHERSHIP-01 to FB-GULL-MOTHERSHIP-04: the Gull Mothership, the final boss of 1-2.

Logical pixels, nose +Z, Y up (towards the camera). A brood-mother of the sea: a wide fleshy mantle,
a shelled body along its middle ending in a huge glowing eye (its laser), a brood pouch at each
flank and two flak growths on its front. The mantle's flank plates, with the swim bladders on the
rear ones, are its armour, drawn apart (`gull_mothership_armour`, D-254).
"""

import math

from game.config.boss_look import BOSS_LOOK
from game.config.bosses.final_bosses import GULL_MOTHERSHIP
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_gull import DECK_TOP, draw_flak, draw_hangar
from game.view.bosses.final_boss_shapes import shift
from game.view.bosses.gull_mothership_armour import draw_centre, draw_mantle, gull_armour
from game.view.bosses.world_1_organic_kit import (
    F,
    M,
    barbs,
    gland,
    graft,
    hide,
    polygon,
    rib_cage,
    spine,
    tentacle,
)
from game.view.enemies.enemy_shapes import SIDES
from game.view.enemies.organic_parts import eyes, reactor_sac
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


N = BOSS_LOOK.neon["gull-mothership"]
QUARTER = math.pi / 2


def _draw_hull(p: Any) -> None:
    """Draw the body (FB-GULL-MOTHERSHIP-02): a teal mantle lined with a green vein.

    Its upper layer and the second fold on it drawn only along the middle (their flanks are the
    armour, drawn apart), a shelled body along its middle with ribs over its back and glands down
    its spine.
    """
    draw_mantle(p)
    draw_centre(p)
    hide(
        p,
        {
            "tail": -61,
            "nose": 58,
            "width": 16,
            "bottom": DECK_TOP - 1,
            "top": 22,
            "segments": 6,
            "shell": [F.slate, F.membrane],
            "belly": F.sinew,
        },
    )
    rib_cage(
        p,
        [-36, -24, -12, 0, 12],
        {"halfWidth": 20, "y": DECK_TOP, "height": 15, "thickness": 1.2},
    )
    spine(p, [0, 22.5, -50], [0, 22.5, 40], {"color": N, "width": 1.6, "bow": 3})
    # The core's turret stands on the graft, its two rotors down the spine behind it (its mounts,
    # BOSS-58); a gland between the turret and the rotors.
    gland(p, [0, 22, 18], 1.8, N)
    graft(p, polygon(6, 7, [1, 1.6]), [20.5, 22], [0, 0, 30])
    barbs(p, [0, 21, -44], {"count": 3, "spacing": 0.1, "size": 4, "dir": [0, 1, -0.4]})
    for s in SIDES:
        tentacle(p, [s * 10, 0, -52], [s * 18, -1, -60], [s * 4, 0, 0], [3, 0.4], F.teal)
        reactor_sac(p, [s * 6, DECK_TOP + 2.5, -60], 2.8, N)


def _draw_emitter(p: Any) -> None:
    """Draw the laser eye's socket at the nose (FB-GULL-MOTHERSHIP-03): flesh, a grafted ring.

    The eye's emitter, its lens glowing as it charges, is its laser mount set in it (BOSS-58).
    """
    at = [0, DECK_TOP + 3, 58]
    p.flesh.cylinder(8, 6, 8, F.graphite, Placement(at, 0, QUARTER), 6.5)  # type: ignore[arg-type]  # the argument does not match the parameter type mypy expects
    p.hull.ring(7.3, 1.4, 8, M.dark, Placement(shift(at, [0, 0, 5.4]), 0, QUARTER))
    for z in [1.5, 5]:
        p.neon.ring(7.6 - z * 0.15, 1, 8, N, Placement(shift(at, [0, 0, z]), 0, QUARTER))
    eyes(p, shift(at, [0, 9, -6]), {"count": 4, "size": 1.1, "spacing": 3}, N)


def build_gull_mothership(scene: Any) -> Any:
    """FB-GULL-MOTHERSHIP-01, FB-GULL-MOTHERSHIP-04: the Gull Mothership.

    A brood-mother of the sea 5 L across: green veins and glands, a brood pouch on each flank (they
    launch the Gnats), two flak growths on its front, and a huge laser eye at the nose of its body
    (the core). Its flank plates are its armour, drawn apart (FB-GULL-MOTHERSHIP-05).
    """

    def core(p: Any) -> None:
        _draw_hull(p)
        _draw_emitter(p)

    return build_boss_model(
        GULL_MOTHERSHIP,
        scene,
        N,
        {
            "core": core,
            "parts": {
                "hangar-left": draw_hangar,
                "hangar-right": draw_hangar,
                "flak-left": draw_flak,
                "flak-right": draw_flak,
            },
            "armour": gull_armour(),
        },
    )
