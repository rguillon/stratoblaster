"""P07-R05 (phase 7 review: more detail, not symmetrical), P16-R06: the Overlord's skyline, a city
grown out of its back, ported from `bosses/overlord-skyline.ts`: towers of flesh and bone lit with
window glands, a broadcast spire and a neon billboard on the left (+X, the screen's left), the
command stalk on the right. Model space: logical pixels, nose +Z, Y up.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.view.bosses.overlord_city import OVERLORD_DECK, OVERLORD_NEON  # noqa: E402
from game.view.bosses.world_1_organic_kit import F, graft, polygon  # noqa: E402
from game.view.enemies.organic_parts import opt  # noqa: E402
from render.geometry.organic import organ  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Vec3 = list[Any]
__pragma__("noskip")

H = ENEMY_LOOK.hull
WHITE = [1, 1, 1]
N = OVERLORD_NEON

# The towers, left and right: none mirrored, kept off the wing roots (|x| <= 54).
TOWERS = [
    # Left (+X).
    {"x": 35, "z": -9, "w": 7, "d": 8, "h": 19, "roof": "mast"},
    {"x": 50, "z": 7, "w": 7, "d": 10, "h": 12, "roof": "ac"},
    {"x": 51, "z": 24, "w": 6, "d": 6, "h": 8, "roof": "tank"},
    {"x": 31, "z": -53, "w": 8, "d": 6, "h": 13, "tier": [5, 3.5, 5]},
    {"x": 42, "z": -51, "w": 6, "d": 6, "h": 8, "roof": "ac"},
    {"x": 22, "z": 52, "w": 7, "d": 5, "h": 6},
    # Right (-X).
    {"x": -34, "z": -12, "w": 7, "d": 7, "h": 25, "tier": [4.5, 4, 5], "roof": "mast"},
    {"x": -51, "z": -11, "w": 6, "d": 9, "h": 14, "roof": "tank"},
    {"x": -33, "z": 15, "w": 7, "d": 7, "h": 10, "roof": "ac"},
    {"x": -51, "z": 16, "w": 6, "d": 9, "h": 7, "roof": "ac"},
    {"x": -52, "z": 27, "w": 5, "d": 5, "h": 12},
    {"x": -36, "z": -53, "w": 7, "d": 6, "h": 19, "roof": "mast"},
    {"x": -46, "z": -49, "w": 5, "d": 5, "h": 7},
    {"x": -25, "z": 51, "w": 6, "d": 6, "h": 11, "roof": "tank"},
]

# The spire's foot on the left, and its height.
SPIRE = {"x": 46, "z": -6, "top": 50}

# A tower's flesh shades, picked by its place (uneven, not mirrored).
SHADES = [F.purple, F.crimson, F.sinew, F.bone]


def _spire(p: Any, tower: Any) -> None:
    """A tower grown out of the back (P16-R06): a tapering spire of flesh or bone over the tower's
    footprint, bands of window glands up it, a grafted roof plate where it had a roof."""
    x = tower.x
    z = tower.z
    w = tower.w
    d = tower.d
    h = tower.h
    tier = opt(tower, "tier", None)
    roof = opt(tower, "roof", None)
    base = OVERLORD_DECK["top"] - 1
    r = max(w, d) * 0.6
    height = h + (tier[2] if tier != None else 0) + 1  # noqa: E711
    color = SHADES[abs(math.floor(x + z + 0.5)) % len(SHADES)]
    profile = [
        [r, 0],
        [r * 0.8, height * 0.55],
        [r * 0.45, height],
        [0, height + r * 0.3],
    ]
    p.flesh.lathe(profile, 5, color, Placement([x, base, z], x * 0.1))
    y = 4
    while y < height - 1:
        k = 1 - (y / height) * 0.5
        p.vein.ring(r * 0.86 * k + 0.1, 0.7, 5, N, Placement([x, base + y, z], x * 0.1))
        y += 7
    if roof != None:  # noqa: E711
        graft(p, polygon(4, r * 0.6), [base + height - 1, base + height], [x, 0, z])


def _draw_spire(parts: Any) -> None:
    """A broadcast spire on the left: a bulb, a tapered bone mast ringed with neon, a beacon on
    top."""
    flesh = parts.flesh
    neon = parts.neon
    charge = parts.charge
    x = SPIRE["x"]
    z = SPIRE["z"]
    top = SPIRE["top"]
    base = OVERLORD_DECK["top"]
    organ(flesh, 5.5, 6, F.crimson, Placement([x, base - 1, z]), 0.9)
    flesh.cylinder(2.8, top - base - 9, 4, F.bone, Placement([x, base + 9, z], math.pi / 4), 0.5)
    rings: list[Any] = [[24, 2], [34, 1.4], [43, 0.9]]
    for ring in rings:
        neon.ring(ring[1] + 0.3, 0.8, 4, N, Placement([x, ring[0], z], math.pi / 4))
    charge.lathe(
        [
            [1.2, 0],
            [0.9, 1.2],
            [0, 1.8],
        ],
        6,
        WHITE,
        Placement([x, top, z]),
    )


# The billboard's foot on the left: its board faces the nose, leaning back towards the camera.
BILLBOARD = {"x": 39, "z": 16, "y": 14, "w": 18, "h": 9, "lean": -0.5}
# The bars of its logo (x, height), and its strips of text lit by the charge (x0, y0, x1, y1).
LOGO = [
    [-6.5, 5],
    [-4.6, 3],
    [-2.7, 5.5],
]
TEXT = [
    [0.5, 5.2, 7, 6.4],
    [0.5, 2.6, 5.5, 3.6],
]


def _draw_billboard(parts: Any) -> None:
    """A neon billboard on stilts: a dark board, a lit frame, a logo, text flickering with the
    charge."""
    hull = parts.hull
    neon = parts.neon
    charge = parts.charge
    x = BILLBOARD["x"]
    z = BILLBOARD["z"]
    y = BILLBOARD["y"]
    w = BILLBOARD["w"]
    h = BILLBOARD["h"]
    lean = BILLBOARD["lean"]
    for dx in [-w / 3, w / 3]:
        hull.box(
            [1.2, y + 2 - OVERLORD_DECK["top"], 1.2],
            H.dark,
            Placement([x + dx, OVERLORD_DECK["top"], z - 1]),
        )
    hull.box([w, h, 1], H.dark, Placement([x, y, z], 0, lean))
    c = math.cos(lean)
    s = math.sin(lean)

    def on_face(dx: float, dy: float) -> Vec3:
        """A point (dx, dy) of the board's face, just out of it."""
        return [x + dx, y + dy * c - 0.6 * s, z + dy * s + 0.6 * c]

    def quad(lit: str, rect: list[Any]) -> None:
        corners = [
            on_face(rect[0], rect[1]),
            on_face(rect[2], rect[1]),
            on_face(rect[2], rect[3]),
            on_face(rect[0], rect[3]),
        ]
        if lit == "neon":
            neon.face(corners, N)
        else:
            charge.face(corners, WHITE)

    hw = w / 2
    bars = [
        [-hw, 0, hw, 0.7],
        [-hw, h - 0.7, hw, h],
        [-hw, 0, -hw + 0.7, h],
        [hw - 0.7, 0, hw, h],
    ]
    for bar in bars:
        quad("neon", bar)
    for logo in LOGO:
        quad("neon", [logo[0], 1.8, logo[0] + 1.3, 1.8 + logo[1]])
    for line in TEXT:
        quad("charge", line)


# The command tower's cab (lathe profile, bottom to top): wider than its shaft, windows all round.
CAB = [
    [6, 0],
    [8.6, 2.5],
    [8.8, 6.5],
    [6.5, 8.5],
]
COMMAND = {"x": -42, "z": 1, "shaft": 20}


def _draw_command_tower(p: Any) -> None:
    """The command stalk on the right: a sinew stalk, an eye of a cab ringed with lit glands,
    masts."""
    x = COMMAND["x"]
    z = COMMAND["z"]
    shaft = COMMAND["shaft"]
    base = OVERLORD_DECK["top"]
    top = base + shaft
    organ(p.flesh, 7, 6, F.purple, Placement([x, base - 1, z]), 0.6)
    p.flesh.cylinder(4.6, shaft, 6, F.sinew, Placement([x, base, z], math.pi / 6), 3.4)
    p.flesh.lathe(CAB, 8, F.crimson, Placement([x, top, z], math.pi / 8))
    p.neon.ring(8.85, 2, 8, N, Placement([x, top + 3.4, z], math.pi / 8))
    p.vein.ring(4.4, 1, 6, N, Placement([x, base + 9, z], math.pi / 6))
    roof = top + 8.5
    # A dish leaning towards the nose, an aerial with a light that charges: grafted metal.
    p.hull.cylinder(0.6, 2.4, 6, H.dark, Placement([x + 2, roof, z - 2], 0, 0.5), 4.2)
    p.hull.cylinder(0.5, 12, 4, H.dark, Placement([x - 3, roof, z + 1]), 0.2)
    p.charge.box([1.1, 1.1, 1.1], WHITE, Placement([x - 3, roof + 11.6, z + 1]))


def draw_skyline(parts: Any) -> None:
    """P07-R05, P16-R06: the Overlord's city, its living towers and landmarks."""
    for tower in TOWERS:
        _spire(parts, tower)
    _draw_spire(parts)
    _draw_billboard(parts)
    _draw_command_tower(parts)
