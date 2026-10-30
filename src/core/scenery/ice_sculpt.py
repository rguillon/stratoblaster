"""Sculpt operations of the frozen lands (phase 8, P08-R03, P08-R07): frozen lakes and the
crevasses of a glacier. Pure and deterministic for a given seed."""

import math

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from core.math.noise import Noise2D  # noqa: E402
from core.scenery.scenery_level import Crevasses, Lakes  # noqa: E402

__pragma__("noskip")

from core.math.noise import hash_2d, smoothstep  # noqa: E402

# Hash streams of a lake's square: whether it has one, where, how big.
LAKE_HAS = 0
LAKE_X = 1
LAKE_Z = 2
LAKE_RADIUS = 3
# Scale (in spacings) of the noise that breaks the crevasse lines into pieces.
CREVASSE_PIECES = 1.3
# Share of a crevasse's half width that is its flat-bottomed floor.
CREVASSE_FLOOR = 0.35


def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t


class Lake:
    """One square's lake: its centre and radius."""

    def __init__(self, cx: float, cz: float, radius: float) -> None:
        self.cx = cx
        self.cz = cz
        self.radius = radius


class LakeField:
    """The frozen lakes of `lakes`, each square's lake worked out once when first needed."""

    def __init__(self, lakes: Lakes, seed: int) -> None:
        self._lakes = lakes
        self._seed = seed
        self._squares: dict[str, Lake | None] = {}

    def apply(self, x: float, z: float, h: float) -> float:
        """`h` with the lakes flattened into it at (`x`, `z`)."""
        spacing = self._lakes.spacing
        edge = self._lakes.edge
        level = self._lakes.level
        i0 = math.floor(x / spacing)
        j0 = math.floor(z / spacing)
        height = h
        for j in range(j0 - 1, j0 + 2):
            for i in range(i0 - 1, i0 + 2):
                lake = self._lake(i, j)
                if lake is None:
                    continue
                d = math.hypot(x - lake.cx, z - lake.cz)
                if d < lake.radius + edge:
                    height = _lerp(
                        level,
                        height,
                        smoothstep(lake.radius, lake.radius + edge, d),
                    )
        return height

    def _lake(self, i: int, j: int) -> Lake | None:
        """The lake of square (`i`, `j`), if it has one (|j| stays far below a million)."""
        key = str(i * 1000003 + j)
        if key not in self._squares:
            self._squares[key] = _square_lake(self._lakes, self._seed, i, j)
        return self._squares[key]


def _square_lake(lakes: Lakes, seed: int, i: int, j: int) -> Lake | None:
    """The lake of square (`i`, `j`) of `lakes`, or None."""
    spacing = lakes.spacing
    edge = lakes.edge

    def r(draw: int) -> float:
        return hash_2d(i, j, seed * 41 + draw)

    if r(LAKE_HAS) >= lakes.chance:
        return None
    # Kept within its square, so a lake never reaches past the squares around it.
    radius = _lerp(lakes.radius[0], lakes.radius[1], r(LAKE_RADIUS))
    room = max(0, spacing / 2 - radius - edge)
    cx = (i + 0.5) * spacing + (r(LAKE_X) * 2 - 1) * room
    cz = (j + 0.5) * spacing + (r(LAKE_Z) * 2 - 1) * room
    return Lake(cx, cz, radius)


def with_lakes(lakes: Lakes, seed: int, x: float, z: float, h: float) -> float:
    """`h` with the frozen lakes of `lakes` flattened into it at (`x`, `z`): each square of
    `spacing` may hold one lake, round, at its level within `radius`, its shore rising back to the
    ground over `edge`."""
    return LakeField(lakes, seed).apply(x, z, h)


def crevasse_depth(crevasses: Crevasses, noise: Noise2D, x: float, z: float) -> float:
    """How deep the crevasses of `crevasses` cut the ground at (`x`, `z`): 0 between them, up to
    `depth` at the bottom of one. The lines run at `angle_deg`, bent by `noise`, and are broken
    into pieces by it."""
    spacing = crevasses.spacing
    width = crevasses.width
    depth = crevasses.depth
    angle = (crevasses.angle_deg * math.pi) / 180
    scale = spacing * CREVASSE_PIECES
    across = (x * math.sin(angle) + z * math.cos(angle)) / spacing
    phase = across + crevasses.warp * noise(x / (spacing * 3), z / (spacing * 3))
    t = phase - math.floor(phase)
    distance = min(t, 1 - t) * spacing
    half = width / 2
    cut = 1 - smoothstep(half * CREVASSE_FLOOR, half, distance)
    if cut <= 0 or crevasses.share <= 0:
        return 0
    if crevasses.share >= 1:
        return depth * cut
    # Pieces: the line is cut where a second noise is above a threshold set by `share`.
    piece = noise(x / scale + 23, z / scale - 11) * 0.5 + 0.5
    threshold = 1 - crevasses.share
    return depth * cut * smoothstep(threshold - 0.05, threshold + 0.05, piece)
