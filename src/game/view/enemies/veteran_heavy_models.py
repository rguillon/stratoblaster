"""P05-R15, P05-R18, P16-R04: the heavier veteran kinds Logical pixels, nose +Z, Y up (to the
camera)."""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.enemies_veteran import VETERAN_CONFIG  # noqa: E402
from game.config.enemies_veteran import VETERAN_NEON as N  # noqa: E402
from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.view.enemies.enemy_mesh import build_enemy_model  # noqa: E402
from game.view.enemies.enemy_shapes import SIDES, flip_x  # noqa: E402
from game.view.enemies.organic_parts import eyes  # noqa: E402
from game.view.enemies.vetelite_organic import LEAN_SECTION  # noqa: E402
from render.geometry.organic import (  # noqa: E402
    SegmentedBody,
    carapace,
    curve,
    organ,
    segmented_body,
)
from render.geometry.organic import (
    vein as vein_tube,
)
from render.geometry.solids import Placement  # noqa: E402

__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

H = ENEMY_LOOK.hull
F = ENEMY_LOOK.flesh
WHITE = [1, 1, 1]  # type: list[float]
QUARTER = math.pi / 2


def _mortar_girth(t: float) -> float:
    return 0.55 + 0.45 * math.sin(math.pi * t)


def _minelayer_girth(t: float) -> float:
    return 0.6 + 0.4 * math.sin(math.pi * t)


# P05-R15, P16-R04: the Mortar's squat, ridged shell, wider than long (tail to front).
MORTAR_SHELL = SegmentedBody(-14, 12, 3, 17.5, -2.2, 3.4, None, _mortar_girth, [False, False])
# The armour plates grafted on its front shoulders (right side).
MORTAR_PLATE = [[6, 11], [12, 8], [12.5, 4], [7, 6]]  # type: list[list[float]]


def mortar_sac(p: Any, s: float) -> None:
    """A side sac on side `s`, swollen with shells, a running light along it."""
    organ(p.flesh, 3, 5, F.crimson, Placement([s * 18, 0.6, -9], 0, QUARTER), 0.95)
    p.neon.box([0.8, 0.3, 4], N.mortar, Placement([s * 18.2, 3.6, -4]))


def build_mortar(scene: Any) -> Any:
    """P05-R15, P16-R04: a squat, armoured beetle with a short, wide barrel grafted on a raised
    mount in its middle, shell sacs on its flanks and olive-green neon. The barrel's mouth glows
    as the next shell charges."""
    muzzle_cfg = VETERAN_CONFIG.mortar.muzzles[0]
    mouth_height = muzzle_cfg[2]
    mouth = -muzzle_cfg[1]

    def draw(p: Any) -> None:
        hull = p.hull
        flesh = p.flesh
        neon = p.neon
        charge = p.charge
        muzzle = p.muzzle
        carapace(flesh, MORTAR_SHELL, [F.sinew, F.crimson])
        # The raised mount: a squat drum, a cradle on it, then the barrel.
        hull.cylinder(7, 3, 8, H.panel, Placement([0, 2.4, 0]), 6)
        hull.box([6, 2.6, 9], H.dark, Placement([0, 5.4, 1.5]))
        neon.ring(6.6, 0.5, 8, N.mortar, Placement([0, 3.6, 0]))
        hull.cylinder(2.6, mouth - 4.3, 8, H.dark, Placement([0, mouth_height, 4], 0, QUARTER), 2.4)
        hull.ring(2.9, 1.5, 8, H.panel, Placement([0, mouth_height, mouth - 3], 0, QUARTER))
        charge.ring(2, 0.3, 8, WHITE, Placement([0, mouth_height, mouth - 0.3], 0, QUARTER))
        muzzle([0, mouth_height, mouth], "gun")
        eyes(p, [0, 1.6, 11.4], {"count": 2, "size": 0.6, "spacing": 3}, N.mortar)
        for s in SIDES:
            p.reactor([s * 8, 0, -14], 1.6)
            plate = MORTAR_PLATE if s == 1 else flip_x(MORTAR_PLATE)
            hull.bevel_slab(plate, [2, 2.6, 3.6], [0, 0.4], H.panel)
            mortar_sac(p, s)

    return build_enemy_model("mortar", scene, N.mortar, draw)


# P05-R18, P16-R04: the Minelayer's long, flat, segmented body, tail to nose.
MINELAYER_BODY = SegmentedBody(-21, 22, 4, 6.8, -1.8, 2.5, 0.2, _minelayer_girth)
# A mine's egg, a lathe profile bottom to top.
MINE = [[0, -1.6], [1.6, -0.8], [1.6, 0.8], [0, 1.6]]  # type: list[list[float]]
# Its tail fins (right side).
MINELAYER_FIN = [[5, -12], [9.8, -17], [9.8, -20.5], [4.5, -18.5]]  # type: list[list[float]]


def build_minelayer(scene: Any) -> Any:
    """P05-R18, P16-R04: a long, flat, segmented grub with a rack of egg-mines along its belly (each
    lit as the next drop charges), metal tail fins and red-orange neon running lights."""
    hatches = VETERAN_CONFIG.minelayer.muzzles

    def draw(p: Any) -> None:
        hull = p.hull
        flesh = p.flesh
        neon = p.neon
        charge = p.charge
        vein = p.vein
        muzzle = p.muzzle
        segmented_body(flesh, MINELAYER_BODY, F.purple, None, LEAN_SECTION)
        # The egg rack along its belly, a metal graft.
        hull.box([4, 1, 26], H.dark, Placement([0, -2.6, 0]))
        for hatch in hatches:
            y = hatch[1]
            height = hatch[2]
            # An egg-mine hanging from the rack, its cap a charge light.
            flesh.lathe(MINE, 6, F.membrane, Placement([0, height, -y]))
            neon.ring(1.65, 0.4, 6, N.minelayer, Placement([0, height - 0.2, -y]))
            muzzle([0, height, -y], "gun")
            # The hatch's glands on the back, lit as the next drop charges.
            for s in SIDES:
                charge.box([1.2, 0.3, 1.6], WHITE, Placement([s * 2.2, 2.6, -y]))
        vein_tube(vein, curve([0, 2.6, -18], [0, 2.6, 17], [0, 0.4, 0], 2), 0.8, N.minelayer)
        neon.box([0.8, 0.25, 6], N.minelayer, Placement([0, 2.2, 18]))
        for s in SIDES:
            for z in [-14, -4, 6]:
                neon.box([0.8, 0.4, 2.2], N.minelayer, Placement([s * 5.4, 1.4, z]))
            fin = MINELAYER_FIN if s == 1 else flip_x(MINELAYER_FIN)
            hull.bevel_slab(fin, [-0.5, 0, 0.6], [0.3, 0.5], H.base, None, H.panel)
            p.reactor([s * 2.4, 0.2, -21], 1.3)

    return build_enemy_model("minelayer", scene, N.minelayer, draw)
