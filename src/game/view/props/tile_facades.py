"""Each face of a volume gets its own pattern of lights (Phase 15, reviewer 2026-10-28: "make all
buildings from offices, towers, downtown and skyscrapers asymmetrical, with a different light
pattern on each side")"""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from core.math.rng import pick, random_in  # noqa: E402
from game.config.prop_look import PROP_LIGHTS as L  # noqa: E402
from game.view.props.tile_kit import NEON  # noqa: E402

# Most lit panels a face may have, and a building, to keep the triangle count down.
MAX_PANELS = 30
BUILDING_PANELS = 220
# How far off its face a lit panel stands.
OFF = 0.06


class FaceKit:
    """What the lights of a volume are drawn with: the lights builder, the random generator and
    the colour of the panels (`Omit<Painter, 'room'>`)."""

    def __init__(self, lights: Any, random: Any, color: list[float]) -> None:  # noqa: ANN401
        self.lights = lights
        self.random = random
        self.color = color


class Room:
    """The panels a face may still have."""

    def __init__(self, n: float) -> None:
        self.n = n


class Painter:
    """What a pattern draws with: the lights builder, the random generator, the colour and the
    panels the face may still have."""

    def __init__(self, lights: Any, random: Any, color: list[float], room: Room) -> None:  # noqa: ANN401
        self.lights = lights
        self.random = random
        self.color = color
        self.room = room


class Face:
    """One face of a box: its middle, the direction along it, its width and its outward sign."""

    def __init__(self, x: float, z: float, along_x: bool, length: float, out: float) -> None:
        self.x = x
        self.z = z
        # Along X (the front and back), else along Z.
        self.along_x = along_x
        self.len = length
        # Outwards, the sign of the face's normal on its axis.
        self.out = out


# The lights builders' panels left, by builder.
def panels_left(lights: Any) -> float:  # noqa: ANN401
    """The panels a building (by its lights builder) has left."""
    if hasattr(lights, "panels_left"):
        left: float = lights.panels_left
        return left
    return BUILDING_PANELS


def panel(p: Painter, face: Face, span: list[float], color: list[float] | None = None) -> None:
    """A lit panel on `face`, `a` along it from its middle, from `y`, `w` wide and `h` high."""
    a = span[0]
    y = span[1]
    w = span[2]
    h = span[3]
    if color == None:  # noqa: E711 (the default: the painter's colour)
        color = p.color
    if p.room.n <= 0:
        return
    p.room.n -= 1
    p.lights.panels_left = panels_left(p.lights) - 1
    # One quad facing out (2 triangles, not a box's 12), so a face can have many.
    s = (-face.out if face.along_x else face.out) * (w / 2)

    def point(along: float, height: float) -> list[float]:
        if face.along_x:
            return [face.x + a + along, height, face.z + face.out * OFF]
        return [face.x + face.out * OFF, height, face.z + a + along]

    p.lights.face([point(-s, y), point(-s, y + h), point(s, y + h), point(s, y)], color)


def rows(p: Painter, f: Face, span: list[float]) -> None:
    """Thin horizontal bands across the face, every few floors."""
    y0 = span[0]
    y1 = span[1]
    # Spread over the whole height, however few the panels.
    gap = max(pick(p.random, [2.5, 3, 3.5]), (y1 - y0) / p.room.n)
    y = y0 + 1
    while y < y1:
        panel(p, f, [0, y, f.len * 0.85, 0.35])
        y += gap


def ribbons(p: Painter, f: Face, span: list[float]) -> None:
    """Short horizontal ribbons, staggered from floor to floor."""
    y0 = span[0]
    y1 = span[1]
    gap = max(2.5, (y1 - y0) / p.room.n)
    i = 0
    y = y0 + 1.5
    while y < y1:
        panel(p, f, [(-0.2 if i % 2 == 0 else 0.2) * f.len, y, f.len * 0.4, 0.3])
        y += gap
        i += 1


def grid(p: Painter, f: Face, span: list[float]) -> None:
    """A loose grid of small lit windows, some dark."""
    y0 = span[0]
    y1 = span[1]
    cw = max(2.5, f.len / 8)
    ch = 2.5
    # Spread over the whole height, a floor every so often, so every face is lit.
    gap = max(ch, (y1 - y0) / max(1, math.ceil(p.room.n / 2)))
    y = y0 + 1
    while y + 1 < y1:
        lit = False
        a = -f.len / 2 + cw / 2
        while a < f.len / 2:
            if p.random() < 0.55 or (not lit and a + cw >= f.len / 2):  # noqa: PLR2004 (a geometry constant)
                panel(p, f, [a, y, cw * 0.6, 0.6])
                lit = True
            a += cw
        y += gap


def bands(p: Painter, f: Face, span: list[float]) -> None:
    """A thin neon band at the top, a lit one at the bottom, dim rows between."""
    y0 = span[0]
    y1 = span[1]
    panel(p, f, [0, y1 - 2, f.len * 0.9, 0.5], pick(p.random, NEON))
    panel(p, f, [0, y0 + 0.5, f.len * 0.9, 0.4])
    gap = max(3, (y1 - y0) / p.room.n)
    y = y0 + 3
    while y < y1 - 4:
        panel(p, f, [0, y, f.len * 0.7, 0.3], L.windowDim)
        y += gap


def sign(p: Painter, f: Face, span: list[float]) -> None:
    """A neon sign high up the face, thin rows under it."""
    y0 = span[0]
    y1 = span[1]
    h = min(4, (y1 - y0) * 0.12)
    panel(
        p,
        f,
        [random_in(p.random, -0.2, 0.2) * f.len, y1 - h - 2, f.len * 0.5, h],
        pick(p.random, NEON),
    )
    y = y0 + 1
    while y < y1 - h - 4:
        panel(p, f, [0, y, f.len * 0.75, 0.3], L.windowDim)
        y += max(3, (y1 - y0) / p.room.n)


PATTERNS = [rows, ribbons, grid, bands, sign]


def face_lights(kit: FaceKit, lot: list[float], span: list[float]) -> None:
    """The lights of a `w` × `d` volume at (x, z), from `y0` to `y1`: each face its own pattern,
    no two of the four the same, so the building looks different from each side."""
    x = lot[0]
    z = lot[1]
    w = lot[2]
    d = lot[3]
    y0 = span[0]
    y1 = span[1]
    faces = [
        Face(x, z - d / 2, True, w, -1),
        Face(x + w / 2, z, False, d, 1),
        Face(x, z + d / 2, True, w, 1),
        Face(x - w / 2, z, False, d, -1),
    ]
    # The patterns shuffled, so the four faces all differ.
    order = [rows, ribbons, grid, bands, sign]
    for i in range(len(order) - 1, 0, -1):
        j = math.floor(kit.random() * (i + 1))
        order[i], order[j] = order[j], order[i]
    # Each face its share of what the building has left, a few panels at least, so none is dark.
    share = min(MAX_PANELS, max(6, math.floor(panels_left(kit.lights) / 8)))
    for i, face in enumerate(faces):
        pattern = order[i]
        pattern(Painter(kit.lights, kit.random, kit.color, Room(share)), face, [y0, y1])
