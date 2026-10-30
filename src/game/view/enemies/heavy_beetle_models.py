"""P05-R09, P05-R10, P16-R03: the Bulwark and the Splitter, Cyber-Organic (P16-R01), ported from
`enemies/heavy-beetle-models.ts`. Logical pixels, nose +Z, Y up.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.enemies import ENEMY_CONFIG  # noqa: E402
from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.view.enemies.enemy_mesh import build_enemy_model  # noqa: E402
from game.view.enemies.enemy_shapes import SIDES, around, radial  # noqa: E402
from render.geometry.organic import (  # noqa: E402
    SegmentedBody,
    carapace,
    curve,
    organ,
    tendril,
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
N = ENEMY_LOOK.neon
WHITE = [1, 1, 1]  # type: list[float]
QUARTER = math.pi / 2

# P05-R09: the Bulwark's armour band along the front of its shell, and the visor.
BULWARK_ARMOUR = [
    [0, 13],
    [12.5, 10.3],
    [23, 1],
    [19.5, -1],
    [10.5, 6.5],
    [0, 9],
    [-10.5, 6.5],
    [-19.5, -1],
    [-23, 1],
    [-12.5, 10.3],
]
BULWARK_VISOR = [  # type: list[list[float]]
    [-7, 0.2],
    [0, 3.3],
    [7, 0.2],
    [7, -0.6],
    [0, 2.5],
    [-7, -0.6],
]


def build_bulwark(scene: Any) -> Any:
    """P05-R09, P16-R03: a heavy armoured beetle: a wide ridged carapace, a metal armour band across
    its front with a blue neon visor slit, mandibles, short legs, twin cannon grafted on its
    head."""

    def draw(p: Any) -> None:
        flesh = p.flesh
        hull = p.hull
        neon = p.neon
        charge = p.charge
        reactor = p.reactor
        muzzle = p.muzzle
        veins = p.vein
        shell = SegmentedBody(-17, 15, 2, 27, -3, 5.4)
        carapace(flesh, shell, [F.teal, F.sinew])
        hull.bevel_slab(BULWARK_ARMOUR, [2.5, 2.5, 3.9], [0, 1.1], H.panel, None, H.base)
        neon.slab(BULWARK_VISOR, [5.1, 5.8], N.bulwark, None)
        vein_tube(veins, [[0, 5.6, -2], [0, 5, -12], [0, 3.6, -16]], 1.2, N.bulwark)
        for s in SIDES:
            tendril(
                flesh,
                curve([s * 6, 0, 13], [s * 2, 0.5, 18], [s * 4, 0, 1], 2),
                [1.6, 0],
                3,
                F.bone,
            )
            for z in [4, -8]:
                tendril(
                    flesh,
                    [[s * 22, -0.5, z], [s * 26.5, -1.5, z - 3]],
                    [1.3, 0.6],
                    3,
                    F.sinew,
                )
            reactor([s * 12, -0.5, -20.5], 1.3)
            # The twin cannon on its head, over the armour (phase 7 review).
            hull.cylinder(0.9, 11, 5, H.dark, Placement([s * 3, 4.2, 2], 0, QUARTER), 0.75)
            charge.cylinder(0.95, 1, 5, WHITE, Placement([s * 3, 4.2, 13], 0, QUARTER))
            muzzle([s * 3, 4.2, 14], "gun")
        reactor([0, 0, -17], 2.2)

    return build_enemy_model("bulwark", scene, N.bulwark, draw)


def splitter_pod_outline(offset: float, inner: float, outer: float) -> list[list[float]]:
    """A Splitter pod: a wedge fitted around the core, `inner` to `outer` from the core's centre,
    outwards along +Z, around its own centre `offset` out."""

    def rim(a: float) -> list[float]:
        return [outer * math.sin(a), outer * math.cos(a) - offset]

    return [[-4, inner - offset], rim(-0.42), rim(-0.21), rim(0.21), rim(0.42), [4, inner - offset]]


def pod(flesh: Any, hull: Any, neon: Any, veins: Any, place: Any) -> None:
    """P16-R03: a pod of the Splitter, a curled flesh grub: a swollen body, a metal plate grafted
    on its back, a neon seam along its inner side and a vein across it."""
    offset = ENEMY_CONFIG.splitter.podOffset
    inner = 8.3
    body = splitter_pod_outline(offset, inner, 16.4)
    flesh.bevel_slab(body, [-2.2, 0.4, 2.4], [0.8, 1.6], F.crimson, place, F.purple)
    hull.bevel_slab(
        splitter_pod_outline(offset, 10.4, 14.4), [2.2, 2.2, 3], [0, 0.6], H.panel, place
    )
    z0 = inner - offset - 0.45
    seam = [[-4.3, z0], [4.3, z0], [4.3, z0 + 0.4], [-4.3, z0 + 0.4]]
    neon.slab(seam, [-1.6, 1.8], N.splitter, place)
    z = 15.6 - offset
    vein_tube(
        veins,
        [[-5, 2.4, z - 1], [0, 2.6, z], [5, 2.4, z - 1]],
        0.8,
        N.splitter,
        place,
    )


def build_splitter(scene: Any) -> Any:
    """P05-R10, P16-R03: a body visibly made of the three grubs it splits into, curled around a
    small flesh heart with a purple neon ring, its eye charging before it fires."""
    offset = ENEMY_CONFIG.splitter.podOffset

    def draw(p: Any) -> None:
        flesh = p.flesh
        hull = p.hull
        neon = p.neon
        charge = p.charge
        reactor = p.reactor
        muzzle = p.muzzle
        organ(flesh, 8.6, 6, F.purple, Placement([0, -3, 0]), 0.4)
        neon.ring(8.4, 0.7, 6, N.splitter, Placement([0, 0.6, 0]))
        for a in around(3):
            pod(flesh, hull, neon, p.vein, Placement(radial(a, offset, 0), a))
        eye = [[0, 0], [2.2, 0.4], [0, 1.4]]
        charge.lathe(eye, 6, WHITE, Placement([0, 4, 0]))
        muzzle([0, 5.4, 0], "gun")
        reactor([0, 0, -7.8], 1.6)

    return build_enemy_model("splitter", scene, N.splitter, draw)


def build_splitter_pod(scene: Any) -> Any:
    """P05-R10, P16-R03: a grub broken off a Splitter, diving outer side first."""
    pod_offset = ENEMY_CONFIG.splitter.podOffset

    def draw(p: Any) -> None:
        pod(p.flesh, p.hull, p.neon, p.vein, None)
        p.reactor([0, 0, 8.3 - pod_offset], 1)

    return build_enemy_model("splitter-pod", scene, N.splitter, draw)
