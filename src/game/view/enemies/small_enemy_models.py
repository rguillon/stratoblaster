"""P05-R01..R05, P16-R03: the lighter enemies, Cyber-Organic (P16-R01), ported from
`enemies/small-enemy-models.ts`: swollen flesh bodies, membrane wings that flutter, metal only where
grafted on (ducts, stingers, guns, nozzles). Logical pixels, nose +Z, Y up (towards the camera).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.view.enemies.basic_parts import (  # noqa: E402
    eye_pair,
    gun_barrel,
    sinew,
    wing_pair,
)
from game.view.enemies.enemy_mesh import build_enemy_model  # noqa: E402
from game.view.enemies.enemy_shapes import (  # noqa: E402
    LOBE_SECTION,  # noqa: E402
    SIDES,
    around,
    radial,
)
from game.view.enemies.organic_parts import reactor_sac  # noqa: E402
from render.geometry.organic import (  # noqa: E402
    SegmentedBody,
    curve,
    organ,
    segmented_body,
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
QUARTER = math.pi / 2

# P05-R01: the duct around each of the Gnat's fans (a metal graft, lathe profile).
GNAT_DUCT = [[2.3, -0.6], [3, 0], [2.3, 0.6], [2.3, -0.6]]  # type: list[list[float]]


def build_gnat(scene: Any) -> Any:
    """P05-R01, P16-R03: a small insect drone: a swollen flesh bulb with a head and two eyes, three
    metal-ducted fans on sinews at 120 degrees, a neon ring around its middle and a feeler on its
    back."""

    def draw(p: Any) -> None:
        flesh = p.flesh
        hull = p.hull
        neon = p.neon
        reactor = p.reactor
        rotor = p.rotor
        organ(flesh, 3.6, 6, F.purple, Placement([0, -1.2, -0.4]), 0.42)
        organ(flesh, 1.5, 4, F.sinew, Placement([0, -0.2, 3.3]), 0.55)
        eye_pair(p, [0, 0.6, 4.2], 0.6, 0.45, N.gnat)
        neon.ring(3.5, 0.5, 6, N.gnat, Placement([0, -0.4, -0.4]))
        for a in around(3):
            duct = radial(a, 6, 0)
            sinew(p, radial(a, 2.6, 0), radial(a, 4, 0), [0, 0.4, 0], 0.6)
            hull.lathe(GNAT_DUCT, 5, H.panel, Placement(duct), False)
            rotor([duct[0], 0, duct[2]], 2.1)
        tendril(
            flesh, curve([-0.8, 1, -1.6], [-1.6, 2.6, -3], [0, 0.4, 0], 2), [0.25, 0], 3, F.bone
        )
        reactor([0, 0, -4.4], 0.9)

    return build_enemy_model("gnat", scene, N.gnat, draw)


def build_hornet(scene: Any) -> Any:
    """P05-R02, P16-R03: a stinger diver: a wasp of three swollen segments, a metal stinger at its
    nose under a single red eye, and swept, serrated membrane wings that flutter."""

    def draw(p: Any) -> None:
        flesh = p.flesh
        hull = p.hull
        neon = p.neon
        body = SegmentedBody(-9, 10.5, 3, 2.6, -1.3, 2.4)
        segmented_body(flesh, body, F.crimson, None, LOBE_SECTION)
        hull.cylinder(0.9, 3.2, 4, H.panel, Placement([0, 0.4, 9.3], 0, QUARTER), 0)
        vein_tube(p.vein, curve([0, 2.3, -7], [0, 2.4, 6], [0, 0.6, 0], 3), 0.6, N.hornet)
        wing_pair(
            p,
            {
                "root": [1.6, 2],
                "tips": [[11.5, -11], [8, -11], [3, -7]],
                "y": 1.6,
                "strut": 0.45,
            },
            N.hornet,
        )
        reactor_sac(p, [0, 0.1, -9], 1.2, N.hornet, F.sinew, 3)
        eye = [[0, -0.5], [0.9, 0], [0, 0.6]]
        neon.lathe(eye, 5, N.hornet, Placement([0, 1.4, 7.4]))

    return build_enemy_model("hornet", scene, N.hornet, draw)


# P05-R03: the Scout's neon strip along each tail boom.
SCOUT_STRIP = [[-0.35, -14], [0.35, -14], [0.35, -5], [-0.35, -5]]  # type: list[list[float]]


def build_scout(scene: Any) -> Any:
    """P05-R03, P16-R03: a light winged scout: a slim flesh body, broad membrane wings that flutter,
    two bone tail booms with a cyan neon strip and a reactor each, and a nose gun grafted on."""

    def draw(p: Any) -> None:
        flesh = p.flesh
        neon = p.neon
        reactor = p.reactor
        body = SegmentedBody(-9, 12.5, 2, 2.5, -1, 2.3)
        segmented_body(flesh, body, F.teal, None, LOBE_SECTION)
        eye_pair(p, [0, 1.6, 8], 0.8, 0.4, N.scout)
        wing_pair(
            p,
            {
                "root": [1.8, 6],
                "tips": [[13, -8], [10, -9], [5, -6]],
                "y": 0.6,
                "strut": 0.5,
            },
            N.scout,
        )
        for s in SIDES:
            tendril(
                flesh,
                curve([s * 2, 0.4, 2], [s * 7, 0.6, -15], [s * 1.5, 0, 0], 3),
                [1.3, 1],
                4,
                F.bone,
            )
            neon.slab(SCOUT_STRIP, [1.3, 1.7], N.scout, Placement([s * 7, 0, 0]))
            reactor([s * 7, 0.3, -15], 1.1)
        # Its nose gun (phase 7 review).
        gun_barrel(p, [0, 1.3, 6], 6.5)

    return build_enemy_model("scout", scene, N.scout, draw)


def edge_light(
    a: list[float], b: list[float], t: float, inward: float, span: list[float]
) -> list[list[float]]:
    """A light along an edge from `a` to `b`, `inward` away from it, `length` long at `t` of it."""
    length = span[0]
    width = span[1]
    dx = b[0] - a[0]
    dz = b[1] - a[1]
    d = math.hypot(dx, dz)
    ux = dx / d
    uz = dz / d
    # The side of the edge behind it, towards the trailing edge.
    if ux < 0:
        nx = -uz
        nz = ux
    else:
        nx = uz
        nz = -ux
    cx = a[0] + dx * t + nx * inward
    cz = a[1] + dz * t + nz * inward

    def along(k: float, w: float) -> list[float]:
        return [cx + (ux * (k * length)) / 2 + nx * w, cz + (uz * (k * length)) / 2 + nz * w]

    return [along(-1, 0), along(1, 0), along(1, width), along(-1, width)]


# The strafer's reactors at this distance out sit a little further back (P05-R04).
STRAFER_INNER_X = 4


def build_strafer(scene: Any) -> Any:
    """P05-R04, P16-R03: a fan shooter: a wide pair of membrane wings out of a squat flesh body, a
    row of magenta neon glands along each leading edge, four reactors and a gun on each flank."""

    def draw(p: Any) -> None:
        flesh = p.flesh
        reactor = p.reactor
        body = SegmentedBody(-6.5, 10.5, 2, 4.2, -1.3, 2.3)
        segmented_body(flesh, body, F.purple, None, LOBE_SECTION)
        eye_pair(p, [0, 1.5, 7], 1, 0.5, N.strafer)
        lights = [edge_light([3, 6], [20.5, -1.5], k / 4, 1.6, [2.4, 0.7]) for k in [1, 2, 3]]
        wing_pair(
            p,
            {
                "root": [3, 4],
                "tips": [[20.5, -1.5], [20.5, -5], [7, -4]],
                "y": 0.2,
                "strut": 0.6,
                "lights": lights,
            },
            N.strafer,
        )
        for x in [-12, -4, 4, 12]:
            reactor([x, 0, -4.3 if abs(x) == STRAFER_INNER_X else -4.1], 1)
        for s in SIDES:
            # A gun on each side of the body, pointing out sideways: it flies across the screen
            # and fires down it from the one facing down (phase 7 review).
            gun_barrel(p, [s * 4.6, 1.5, 1.5], 3.6, s * QUARTER)

    return build_enemy_model("strafer", scene, N.strafer, draw)


# P05-R05: the Weaver's web of sinew between its two serpents, under the neon bar.
WEAVER_WEB = [  # type: list[list[float]]
    [-9, 0.5],
    [0, 2.5],
    [9, 0.5],
    [9, -3],
    [0, -1.5],
    [-9, -3],
]


def build_weaver(scene: Any) -> Any:
    """P05-R05, P16-R03: a sine flyer: two serpents side by side, each a swollen head and a wavy
    tail, joined by a web of flesh under a glowing green neon bar, a gun grafted on each snout."""

    def draw(p: Any) -> None:
        flesh = p.flesh
        neon = p.neon
        reactor = p.reactor
        flesh.bevel_slab(WEAVER_WEB, [-1, -0.4, 0.2], [0.3, 0.6], F.membrane)
        for s in SIDES:
            at: list[float] = [s * 10, 0, 0]
            head = SegmentedBody(-6, 15.5, 2, 2.6, -1.5, 2.6)
            segmented_body(flesh, head, F.teal, Placement(at), LOBE_SECTION)
            tail = [
                [s * 10 + s * math.sin(i * 1.8) * 1.4, 0.4, z]
                for i, z in enumerate([-6, -9, -12, -15])
            ]
            tendril(flesh, tail, [2, 1.2], 4, F.sinew)
            eye_pair(p, [s * 10, 2, 11], 0.9, 0.4, N.weaver)
            reactor([s * 10, 0, -15], 1.5)
            # A gun along each serpent's snout (phase 7 review).
            gun_barrel(p, [s * 10, 1.9, 8], 7)
        neon.slab(
            [[pt[0] * 0.88, pt[1] * 0.4 - 0.3] for pt in WEAVER_WEB],
            [0.2, 0.7],
            N.weaver,
        )

    return build_enemy_model("weaver", scene, N.weaver, draw)
