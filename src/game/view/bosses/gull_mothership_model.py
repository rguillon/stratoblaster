"""P07-R05, P16-R06: the Gull Mothership, the final boss of 1-2, ported from
`bosses/gull-mothership-model.ts`. Logical pixels, nose +Z, Y up (towards the camera). A
brood-mother of the sea: a wide fleshy mantle, a shelled body along its middle ending in a huge
glowing eye (its laser), a brood pouch at each flank and two flak growths on its front.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK  # noqa: E402
from game.config.bosses.final_bosses import GULL_MOTHERSHIP  # noqa: E402
from game.view.bosses.boss_model import build_boss_model  # noqa: E402
from game.view.bosses.final_boss_gull import DECK_TOP, draw_flak, draw_hangar  # noqa: E402
from game.view.bosses.final_boss_shapes import mirrored, shift, turret  # noqa: E402
from game.view.bosses.world_1_organic_kit import (  # noqa: E402
    F,
    M,
    barbs,
    gland,
    graft,
    hide,
    mantle,
    polygon,
    rib_cage,
    scale_outline,
    spine,
    tentacle,
    vein_line,
)
from game.view.enemies.enemy_shapes import SIDES  # noqa: E402
from game.view.enemies.organic_parts import eyes, reactor_sac  # noqa: E402
from render.geometry.organic import SegmentedBody, segmented_body  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Vec3 = list[Any]
__pragma__("noskip")

N = BOSS_LOOK.neon["gull-mothership"]
WHITE = [1, 1, 1]
QUARTER = math.pi / 2

# The mantle seen from above (right half, front to back); the pouches sit on its flat sides.
DECK = mirrored(
    [
        [0, 50],
        [24, 46],
        [40, 32],
        [47, 20],
        [47, -30],
        [34, -48],
        [14, -56],
        [0, -56],
    ]
)
# The laser eye's lens (a lathe profile along its axis), at the body's nose.
LENS = [
    [0, 0],
    [5.5, 1.2],
    [4.6, 3.4],
    [0, 4.4],
]


def _draw_hull(p: Any) -> None:
    """The body (P16-R06): a teal mantle lined with a green vein, a second fold on it, a shelled
    body along its middle with ribs over its back and glands down its spine."""
    mantle(p, DECK, [-5, DECK_TOP], F.teal, N)
    mantle(p, scale_outline(DECK, 0.72, 0, -4), [DECK_TOP - 1, DECK_TOP + 1.6], F.purple)
    hide(
        p,
        {
            "tail": -61,
            "nose": 58,
            "width": 16,
            "bottom": DECK_TOP - 1,
            "top": 22,
            "segments": 6,
            "shell": [F.crimson, F.membrane],
            "belly": F.sinew,
        },
    )
    rib_cage(
        p,
        [-36, -24, -12, 0, 12],
        {"halfWidth": 20, "y": DECK_TOP, "height": 15, "thickness": 1.2},
    )
    spine(p, [0, 22.5, -50], [0, 22.5, 40], {"color": N, "width": 1.6, "bow": 3})
    for z in [-30, -6, 18]:
        gland(p, [0, 22, z], 1.8, N)
    p.neon.box([1, 0.8, 16], N, Placement([0, 24.4, -9]))
    graft(p, polygon(6, 7, [1, 1.6]), [20.5, 22], [0, 0, 30])
    barbs(p, [0, 21, -44], {"count": 3, "spacing": 0.1, "size": 4, "dir": [0, 1, -0.4]})
    for s in SIDES:
        for z in [-34, -14, 6, 26]:
            vein_line(
                p, [s * 15, DECK_TOP + 6, z], [s * 40, DECK_TOP + 1, z - 8], [0, 3, 0], 1.1, N
            )
        tentacle(p, [s * 10, 0, -52], [s * 18, -1, -60], [s * 4, 0, 0], [3, 0.4], F.teal)
        graft(p, polygon(4, 5, [1.6, 0.9]), [DECK_TOP + 1.4, DECK_TOP + 2.4], [s * 30, 0, 22])


def _draw_emitter(p: Any) -> None:
    """The laser eye at the nose: a socket of flesh, a grafted ring, the lens glowing as it
    charges."""
    at = [0, DECK_TOP + 3, 58]
    p.flesh.cylinder(8, 6, 8, F.purple, Placement(at, 0, QUARTER), 6.5)  # type: ignore[arg-type]
    p.hull.ring(7.3, 1.4, 8, M.dark, Placement(shift(at, [0, 0, 5.4]), 0, QUARTER))
    for z in [1.5, 5]:
        p.neon.ring(7.6 - z * 0.15, 1, 8, N, Placement(shift(at, [0, 0, z]), 0, QUARTER))
    p.charge.lathe(LENS, 8, WHITE, Placement(shift(at, [0, 0, 7.5]), 0, QUARTER))
    eyes(p, shift(at, [0, 9, -6]), {"count": 4, "size": 1.1, "spacing": 3}, N)
    # The core's laser and bullets leave from the lens's front.
    lens = shift(at, [0, 0, 11.9])
    p.muzzle(lens, "laser")
    p.muzzle(lens, None)


def _draw_engines(p: Any) -> None:
    """The swim bladders on the back of the mantle, their reactors in sacs."""
    for s in SIDES:
        segmented_body(
            p.flesh,
            SegmentedBody(-51, -24, 2, 5.5, 0, 9.5),
            F.crimson,
            Placement([s * 30, DECK_TOP - 1, 0]),
        )
        reactor_sac(p, [s * 30, DECK_TOP + 3, -50], 3.4, N)
        reactor_sac(p, [s * 6, DECK_TOP + 2.5, -60], 2.8, N)


def _flak_turret(p: Any, at: Vec3) -> None:
    """A flak growth's twin guns, on its crown."""
    turret(p, shift(at, [0, DECK_TOP + 2.5, 0]), 8.5, [2, N])


def build_gull_mothership(scene: Any) -> Any:
    """P07-R05, P16-R06: the Gull Mothership, a brood-mother of the sea 5 L across: green veins and
    glands, a brood pouch on each flank (they launch the Gnats), two flak growths on its front, and
    a huge laser eye at the nose of its body (the core)."""

    def core(p: Any) -> None:
        _draw_hull(p)
        _draw_emitter(p)
        _draw_engines(p)

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
            "turrets": {"flak-left": _flak_turret, "flak-right": _flak_turret},
        },
    )
