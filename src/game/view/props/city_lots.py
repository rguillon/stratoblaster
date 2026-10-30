"""The lots a city building is made of (Phase 4 review): each
one a different kind of volume (a stepped tower, a round tower, a low slab, a courtyard block or
an L-shaped block), so the city centre reads as varied as the industrial zone."""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

from core.math.rng import pick, random_in  # noqa: E402
from game.config.prop_look import PROP_COLORS as C  # noqa: E402
from game.config.prop_look import PROP_LIGHTS as L  # noqa: E402
from game.view.props.city_props import window_bands  # noqa: E402
from game.view.props.tile_facades import FaceKit, face_lights  # noqa: E402
from render.geometry.solids import Placement, SolidBuilder  # noqa: E402


class LotKit:
    """The structure and lights a lot is drawn into, with its facade and window colours. `faces`
    (Phase 15, reviewer 2026-10-28): each face lit in its own pattern (`tile_facades.py`)."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        s: SolidBuilder,
        lights: SolidBuilder,
        facade: list[float],
        windows: list[float],
        roof: list[float],
        random: Any,  # noqa: ANN401 (a seeded generator)
        faces: bool = False,  # noqa: FBT001, FBT002
    ) -> None:
        self.s = s
        self.lights = lights
        self.facade = facade
        self.windows = windows
        self.roof = roof
        self.random = random
        self.faces = faces


def volume(
    kit: LotKit,
    lot: list[float],
    y: float,
    h: float,
    facade: list[float] | None = None,
) -> None:
    """A box with rows of lit windows, from `y` up to `y + h`."""
    if facade == None:  # noqa: E711 (the default: the kit's facade)
        facade = kit.facade
    x = lot[0]
    z = lot[1]
    w = lot[2]
    d = lot[3]
    kit.s.box([w, h, d], facade, Placement([x, y, z], 0, 0, 0), kit.roof)
    # Few rows, and none on low volumes, to keep the triangle count down (review).
    if h < 8:  # noqa: PLR2004 (a geometry constant)
        return
    if kit.faces:
        face_lights(FaceKit(kit.lights, kit.random, kit.windows), [x, z, w, d], [y + 3, y + h - 2])
    else:
        window_bands(kit.lights, [w, d], [y + 3, y + h - 2], 10, 2, kit.windows, [x, z])


def crown(kit: LotKit, at: list[float], size: float) -> None:
    """Something on top of a tower at (x, y, z): a spire, a mast, a pyramid or roof units."""
    s = kit.s
    lights = kit.lights
    random = kit.random
    x = at[0]
    y = at[1]
    z = at[2]
    style = math.floor(random() * 4)
    if style == 0:
        s.lathe(
            [
                [size * 0.25, y],
                [0, y + random_in(random, 8, 16)],
            ],
            4,
            C.metal,
            Placement([x, 0, z], 0, 0, 0),
        )
    elif style == 1:
        h = random_in(random, 8, 14)
        s.cylinder(0.4, h, 4, C.metal, Placement([x, y, z], 0, 0, 0))
        lights.box([1, 1, 1], L.red, Placement([x, y + h, z], 0, 0, 0))
    elif style == 2:  # noqa: PLR2004 (a geometry constant)
        s.lathe(
            [
                [size * 0.6, y],
                [0, y + size * 0.4],
            ],
            4,
            C.roof,
            Placement([x, 0, z], math.pi / 4, 0, 0),
        )
    else:
        s.box([size * 0.4, 2, size * 0.3], C.metalDark, Placement([x - size * 0.2, y, z], 0, 0, 0))
        s.box(
            [size * 0.2, 1.4, size * 0.2],
            C.metal,
            Placement([x + size * 0.25, y, z + size * 0.2], 0, 0, 0),
        )


def plinth(kit: LotKit, lot: list[float]) -> float:
    """A low base covering the whole lot, so no bare ground shows around a tower; its height."""
    x = lot[0]
    z = lot[1]
    w = lot[2]
    d = lot[3]
    # At least 3 high, so the uneven ground of a block never shows through it (review).
    h = random_in(kit.random, 3, 6)
    kit.s.box(
        [w, h, d],
        pick(kit.random, [C.concreteDark, C.brick, C.concrete]),
        Placement([x, 0, z], 0, 0, 0),
        kit.roof,
    )
    return h


def stepped_tower(kit: LotKit, lot: list[float]) -> None:
    """A tower in 1 to 3 tiers stepping back, on a base covering its lot."""
    random = kit.random
    x = lot[0]
    z = lot[1]
    w = lot[2]
    d = lot[3]
    tiers = 1 + math.floor(random() * 3)
    tw = w * random_in(random, 0.55, 0.9)
    td = d * random_in(random, 0.55, 0.9)
    y = plinth(kit, lot)
    for t in range(tiers):
        h = random_in(random, 12, 30)
        volume(kit, [x, z, tw, td], y, h)
        y += h
        shrink = random_in(random, 0.6, 0.8)
        if t < tiers - 1:
            tw = tw * shrink
            td = td * shrink
    crown(kit, [x, y, z], min(tw, td))


def round_tower(kit: LotKit, lot: list[float]) -> None:
    """A round tower in octagonal facets, with lit rings around it."""
    s = kit.s
    lights = kit.lights
    random = kit.random
    x = lot[0]
    z = lot[1]
    w = lot[2]
    d = lot[3]
    radius = (min(w, d) / 2) * random_in(random, 0.6, 0.85)
    base = plinth(kit, lot)
    h = base + random_in(random, 25, 60)
    s.cylinder(
        radius,
        h - base,
        6,
        kit.facade,
        Placement([x, base, z], 0, 0, 0),
        radius * random_in(random, 0.7, 1),
    )
    y = base + 4
    while y + 2 < h - 4:
        lights.ring(radius * 1.02, 2, 6, kit.windows, Placement([x, y, z], 0, 0, 0))
        y += 12
    crown(kit, [x, h, z], radius)


def slab(kit: LotKit, lot: list[float]) -> None:
    """A low slab filling its lot, with roof units and now and then a neon sign."""
    s = kit.s
    lights = kit.lights
    random = kit.random
    x = lot[0]
    z = lot[1]
    w = lot[2]
    d = lot[3]
    h = random_in(random, 6, 14)
    volume(kit, lot, 0, h, pick(random, [C.concrete, C.concreteDark, C.brick]))
    s.box([w * 0.3, 1.5, d * 0.25], C.metalDark, Placement([x - w * 0.15, h, z + d * 0.1], 0, 0, 0))
    if random() < 0.5:  # noqa: PLR2004 (a geometry constant)
        lights.box([w * 0.5, 1.4, 0.3], L.pinkDim, Placement([x, 3, z - d / 2 - 0.3], 0, 0, 0))


def courtyard(kit: LotKit, lot: list[float]) -> None:
    """A block of four wings around a courtyard."""
    x = lot[0]
    z = lot[1]
    w = lot[2]
    d = lot[3]
    t = min(w, d) * random_in(kit.random, 0.25, 0.35)
    h = random_in(kit.random, 10, 24)
    volume(kit, [x, z - d / 2 + t / 2, w, t], 0, h)
    volume(kit, [x, z + d / 2 - t / 2, w, t], 0, h)
    volume(kit, [x - w / 2 + t / 2, z, t, d - 2 * t], 0, h)
    volume(kit, [x + w / 2 - t / 2, z, t, d - 2 * t], 0, h)


def l_block(kit: LotKit, lot: list[float]) -> None:
    """An L-shaped block along two sides of its lot, with a taller wing at the corner."""
    random = kit.random
    x = lot[0]
    z = lot[1]
    w = lot[2]
    d = lot[3]
    t = min(w, d) * random_in(random, 0.35, 0.5)
    h = random_in(random, 10, 20)
    volume(kit, [x, z + d / 2 - t / 2, w, t], 0, h)
    volume(kit, [x - w / 2 + t / 2, z - t / 2, t, d - t], 0, h)
    volume(kit, [x - w / 2 + t / 2, z + d / 2 - t / 2, t, t], h, random_in(random, 10, 30))


# The plain kinds of lots; courtyards and L-shaped blocks need room for their wings.
LOTS = [stepped_tower, round_tower, slab, courtyard, l_block]
WIDE_LOTS = [courtyard, l_block]
