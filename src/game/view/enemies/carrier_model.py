"""P05-R12, P16-R03: the Carrier, Cyber-Organic (P16-R01)

Logical pixels, nose +Z, Y up (towards the camera).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Vec3 = list[float]
__pragma__("noskip")

from game.config.enemies import ENEMY_CONFIG  # noqa: E402
from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.view.enemies.enemy_mesh import build_enemy_model  # noqa: E402
from game.view.enemies.enemy_shapes import LOBE_SECTION, SIDES, decal, flip_x, shift_x  # noqa: E402
from render.geometry.organic import (  # noqa: E402
    SegmentedBody,
    curve,
    organ,
    segmented_body,
    tendril,
    vein,
)

H = ENEMY_LOOK.hull
F = ENEMY_LOOK.flesh
N = ENEMY_LOOK.neon
WHITE = [1, 1, 1]  # type: list[float]
QUARTER = math.pi / 2

# The right sponson along the hull's side. Its outer wall slopes from `SPONSON_EDGE` at the waist
# up to its top, inset `SPONSON_SLOPE`, so the launch ports in it face out and up, to the camera.
CARRIER_SPONSON = [  # type: list[list[float]]
    [12, 16],
    [21, 12],
    [24, 6],
    [24, -14],
    [21, -19],
    [12, -22],
]
SPONSON_EDGE = 24
SPONSON_SLOPE = [5.5, 5]  # type: list[float]
# A port's frame and its glowing mouth: across the slope and along the side.
PORT_FRAME = [5.2, 7]  # type: list[float]
PORT_MOUTH = [3.4, 5.2]  # type: list[float]

# P16-R03: the brood sac's ribs, arched over its back.
CARRIER_RIBS = [-10, 10]  # type: list[float]
# A larva glowing through the sac (8 triangles), and the neon band along each side of its spine.
LARVA = [[0, -0.6], [1.4, 0], [0, 0.8]]  # type: list[list[float]]
CARRIER_BAND = [[-0.4, -13], [0.4, -13], [0.4, 13], [-0.4, 13]]  # type: list[list[float]]
CARRIER_LARVAE = [[-5, 8.6, -9], [5, 8.6, -4], [-4, 9, 5], [4, 8.6, 10]]  # type: list[list[float]]


def port_quad(side: float, z: float, span: list[float], lift: float) -> list[Vec3]:
    """A quad `[across, along]` big on the right sponson's sloped wall, centred on the port at `z`,
    `lift` off the wall; `side` -1 mirrors it to the left."""
    inset = SPONSON_SLOPE[0]
    rise = SPONSON_SLOPE[1]
    length = math.sqrt(inset * inset + rise * rise)
    # The wall's outward normal (n) and the direction down it (d), on the right side.
    nx = rise / length
    ny = inset / length
    dx = ny
    dy = -nx
    cx = SPONSON_EDGE - inset / 2 + nx * lift
    cy = rise / 2 + ny * lift

    def corner(u: float, v: float) -> Vec3:
        return [side * (cx + dx * u), cy + dy * u, z + v]

    u = span[0] / 2
    v = span[1] / 2
    quad = [corner(-u, -v), corner(-u, v), corner(u, v), corner(u, -v)]
    # Mirrored, the corners turn the other way round: keep the face towards the outside.
    if side > 0:
        return quad
    return [quad[3], quad[2], quad[1], quad[0]]


def port(hull: Any, charge: Any, side: float, z: float) -> None:
    """A launch port: a dark frame on the sponson's wall and a mouth glowing as a launch comes."""
    hull.face(port_quad(side, z, PORT_FRAME, 0.08), H.dark)
    charge.face(port_quad(side, z, PORT_MOUTH, 0.16), WHITE)


def draw_carrier(p: Any) -> None:
    """The parts of the Carrier: its brood sac, ribs, larvae, sponsons, ports and reactors."""
    flesh = p.flesh
    hull = p.hull
    neon = p.neon
    charge = p.charge
    segmented_body(flesh, SegmentedBody(-28, 30, 3, 19, -4.5, 9), F.purple, None, LOBE_SECTION)
    for z in CARRIER_RIBS:
        arch = curve([-16, 1, z], [16, 1, z], [0, 10, 0], 4)
        tendril(flesh, arch, [0.9, 0.9], 3, F.bone)
    for at in CARRIER_LARVAE:
        p.vein.lathe(LARVA, 4, N.carrier, Placement(at))
    for s in SIDES:
        decal(neon, shift_x(CARRIER_BAND, s * 3.5), 9.1, N.carrier)
        outline = CARRIER_SPONSON if s > 0 else flip_x(CARRIER_SPONSON)
        inset = SPONSON_SLOPE[0]
        hull.bevel_slab(
            outline,
            [-3, 0, SPONSON_SLOPE[1]],
            [1, inset],
            H.base,
            {},
            H.panel,
        )
        # Model Z is down the screen's Y: a port `py` up the screen sits at Z = -py.
        for entry in ENEMY_CONFIG.carrier.ports:
            port(hull, charge, s, -entry[1])
        # Its reactor, set in a flesh sac with a vein running into the body (P16-R01).
        nozzle = [s * 7, 0.5, -28.5]
        organ(flesh, 3.2, 4, F.crimson, Placement([s * 7, 0.5, -28], 0, QUARTER), 0.9)
        p.reactor(nozzle, 2.4)
        vein(p.vein, curve([s * 7, 3, -25], [s * 5, 6, -17], [0, 1, 0], 2), 1, N.carrier)


def build_carrier(scene: Any) -> Any:
    """P05-R12, P16-R03: a brood sac that releases Gnats: a fat swollen sac of three segments under
    bone ribs, larvae glowing through its back, a metal sponson grafted on each flank with two
    launch ports, amber neon bands along its spine, its reactors set in flesh sacs."""
    return build_enemy_model("carrier", scene, N.carrier, draw_carrier)
