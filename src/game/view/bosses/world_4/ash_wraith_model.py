"""P10-R11, 4-2: the Ash Wraith. Ported from `bosses/world-4/ash-wraith-model.ts`. Logical pixels,
nose +Z, Y up (towards the camera). A ragged stealth flying wing: a thin faceted wing, its trailing
edge torn into tatters, a low fuselage with a dark canopy, the two shroud pods on the wings, the eye
cannon on the nose. P16-R05: a living ash ray, its wing a scorched membrane veined with cyan, its
body flesh under ribs, a great eye on its brow, metal only on its grafts (vents, plates, guns,
reactors).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.world_4.ash_wraith import ASH_WRAITH, WRAITH_VENT  # noqa: E402
from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.bosses.boss_model import build_boss_model  # noqa: E402
from game.view.bosses.final_boss_shapes import edge_strips, mirrored, strip  # noqa: E402
from game.view.bosses.mini_boss_greebles import vent  # noqa: E402
from game.view.bosses.mini_boss_shapes import WHITE, H, offset, socket  # noqa: E402
from game.view.bosses.world_4.ash_plains_soot import (  # noqa: E402
    ASH,
    ASH_THIN,
    SCORCH,
    ash_drift,
    molten_seam,
    soot_streaks,
)
from game.view.bosses.world_4.ash_wraith_parts import (  # noqa: E402
    WRAITH_CYAN,
    eye_mount,
    eye_turret,
    shroud_pod,
)
from game.view.bosses.world_4.living_forge import (  # noqa: E402
    SKIN,
    back_ribs,
    glands,
    magma_vein,
    reactor_sacs,
)
from game.view.enemies.enemy_shapes import FIGHTER_SECTION, SIDES, canopy_paint  # noqa: E402
from render.geometry.organic import RibSpec  # noqa: E402
from render.geometry.solids import LoftOptions, Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Vec3 = list[float]
__pragma__("noskip")

# The wing seen from above (right half, nose to tail): a sharp delta, its trailing edge torn into
# ragged points, as if it had flown through fire.
WING_HALF = [
    [0.0, 44.0],
    [7.0, 34.0],
    [20.0, 14.0],
    [34.0, 1.0],
    [47.0, -9.0],
    [51.0, -15.0],
    [45.0, -17.0],
    [41.0, -25.0],
    [35.0, -19.0],
    [29.0, -28.0],
    [23.0, -21.0],
    [17.0, -31.0],
    [11.0, -24.0],
    [6.0, -36.0],
    [0.0, -30.0],
]
WING = mirrored(WING_HALF)

# The fuselage along the centre line, tail to nose (loft stations: z, half width, bottom, top).
FUSELAGE = [
    [-33.0, 4.0, 0.0, 3.5],
    [-22.0, 9.0, -1.0, 7.5],
    [-6.0, 12.0, -1.5, 10.0],
    [10.0, 10.0, -1.0, 9.0],
    [24.0, 5.0, 0.0, 4.6],
]
# The dark glass of its canopy, on the back of the fuselage's front bands.
CANOPY_GLASS = [0.03, 0.05, 0.06]


def _wing_veins(p: Any, s: float) -> None:
    """P16-R05, P16-R06: its living flesh: veins, glands and ribs."""
    magma_vein(
        p,
        [
            [s * 8, 3.2, 12],
            [s * 24, 3.1, 2],
            [s * 40, 3, -8],
        ],
        0.9,
        WRAITH_CYAN,
    )
    magma_vein(
        p,
        [
            [s * 9, 3.2, 0],
            [s * 22, 3.1, -14],
        ],
        0.8,
        WRAITH_CYAN,
    )


def _draw_wing(p: Any) -> None:
    """The wing: grey, bevelled plates, pale cyan neon along its leading edges, ash and soot on
    it."""
    hull = p.hull
    neon = p.neon
    p.flesh.bevel_slab(WING, [-1, 0.6, 3], [0.8, 1], SKIN.dark, None, SKIN.base)
    for s in SIDES:
        _wing_veins(p, s)
        edge_strips(
            neon,
            [
                [s * 8.5, 30],
                [s * 20.5, 11.5],
                [s * 34, -1.5],
                [s * 44, -9],
            ],
            0.8,
            [2.7, 3.2],
            WRAITH_CYAN,
        )
        edge_strips(
            neon,
            [
                [s * 47, -12],
                [s * 43, -15],
            ],
            0.7,
            [2.4, 2.9],
            WRAITH_CYAN,
        )
        soot_streaks(
            hull,
            [
                [
                    [s * 8, -20],
                    [s * 14, -30],
                ],
                [
                    [s * 20, -12],
                    [s * 27, -24],
                ],
                [
                    [s * 44, -4],
                    [s * 46, -14],
                ],
            ],
            3,
        )
        molten_seam(p, [s * 14, 4], [s * 22, -10], 3)
        ash_drift(hull, [s * 22, 3, 10], 3.6, s * 1.3)
        ash_drift(hull, [s * 46, 2.6, -10], 2.4, s * 2.2)


def _canopy_glass_paint() -> Any:
    """The canopy's dark glass, painted on the back of the front bands of the fuselage."""
    paint: Any = canopy_paint([2, 3], CANOPY_GLASS)
    return paint


def _draw_fuselage(p: Any) -> None:
    """The fuselage: a low faceted spine, its dark canopy, vents and scorched plates by the
    engines."""
    hull = p.hull
    neon = p.neon
    p.flesh.loft(
        FIGHTER_SECTION,
        FUSELAGE,
        SKIN.base,
        None,
        LoftOptions(False, _canopy_glass_paint()),
    )
    back_ribs(p, [-12, -4, 4], RibSpec(8, 3, 6.6, 0.7))
    glands(
        p,
        [
            [0, 8.6, -9],
            [0, 8.8, 0],
        ],
        1.2,
        WRAITH_CYAN,
    )
    strip(neon, [0, 21], [0, 14], 0.6, [9.4, 9.8], WRAITH_CYAN)
    for s in SIDES:
        vent(hull, [s * 7, 7.2, -16], [3, 6], 3, s * 0.15)
        hull.box([5, 1.4, 8], SCORCH, Placement([s * 6, 2.6, -30]), H.dark)
        strip(neon, [s * 10.6, 2], [s * 8.4, -18], 0.6, [5.6, 6.2], WRAITH_CYAN)
    reactor_sacs(
        p,
        [
            [5.5, 2.2, -34],
            [-5.5, 2.2, -34],
        ],
        2.6,
        WRAITH_CYAN,
    )


# Flakes of ash trailing off its torn wing (x, z, size, turn): it sheds ash as it flies.
ASH_TRAIL = [
    [41.0, -30.0, 2.2, 0.4],
    [29.0, -34.0, 1.8, 1.1],
    [17.0, -37.0, 2.0, 2.0],
    [6.0, -42.0, 1.6, 0.7],
    [36.0, -38.0, 1.4, 1.6],
]
# A flake of ash seen from above: a small ragged diamond.
FLAKE = [
    [0.0, 1.0],
    [0.7, 0.1],
    [0.2, -1.0],
    [-0.8, -0.2],
]


def _draw_ash_trail(p: Any) -> None:
    """The ash it sheds: grey flakes drifting behind the trailing edge, either side."""
    hull = p.hull
    for s in SIDES:
        for entry in ASH_TRAIL:
            x = entry[0]
            z = entry[1]
            size = entry[2]
            turn = entry[3]
            flake = [[f[0] * size, f[1] * size] for f in FLAKE]
            hull.slab(
                flake, [0, 0.3], ASH_THIN, Placement([s * x, 1 + size * 0.3, z], s * turn), ASH
            )


def _draw_vent(p: Any) -> None:
    """The ash vent on its back (the core's spirals): a squat stack, a cyan ring, a lit grate."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    if len(WRAITH_VENT) == 0:
        return
    m = WRAITH_VENT[0]
    top = boss_point(m[0], m[1], m[2])
    socket(hull, offset(top, 0, -5.6, 0), 4.6, 1.6)
    hull.cylinder(4, 4.4, 8, H.panel, Placement(offset(top, 0, -5, 0), math.pi / 8), 3.2)
    neon.ring(3.3, 0.5, 8, WRAITH_CYAN, Placement(offset(top, 0, -1.2, 0), math.pi / 8))
    hull.cylinder(2.6, 0.6, 8, ASH, Placement(offset(top, 0, -1.2, 0)))
    charge.cylinder(2, 0.6, 8, WHITE, Placement(offset(top, 0, -0.6, 0)))
    muzzle(top, "ring")


def build_ash_wraith(scene: Any) -> Any:
    """P10-R11: the Ash Wraith, a ragged grey stealth gunship trailing ash, pale cyan neon, soot and
    molten seams on its torn wing."""

    def core(p: Any) -> None:
        _draw_wing(p)
        _draw_fuselage(p)
        _draw_vent(p)
        _draw_ash_trail(p)

    return build_boss_model(
        ASH_WRAITH,
        scene,
        WRAITH_CYAN,
        {
            "core": core,
            "parts": {"pod-left": shroud_pod, "pod-right": shroud_pod, "eye": eye_mount},
            "turrets": {"eye": eye_turret},
        },
    )
