"""Futuristic desert homes and outposts (P06-R06), ported from `props/desert-props.ts`. Sizes in
world units, standing on Y = 0."""

import math

from game.config.prop_look import PROP_COLORS as C
from game.config.prop_look import PROP_LIGHTS as L
from render.geometry.solids import Placement, SolidBuilder
from render.scenery.scenery_look import PropGeometry


def parapet(s: SolidBuilder, size: list[float], at: float = 0) -> None:
    """A low wall around the edge of a flat roof, `w × d`, on top of a block `h` high."""
    w = size[0]
    h = size[1]
    d = size[2]
    t = 0.8
    s.box([w, 1, t], C.adobeDark, Placement([at, h, -d / 2 + t / 2], 0, 0, 0))
    s.box([w, 1, t], C.adobeDark, Placement([at, h, d / 2 - t / 2], 0, 0, 0))
    s.box([t, 1, d - 2 * t], C.adobeDark, Placement([at - w / 2 + t / 2, h, 0], 0, 0, 0))
    s.box([t, 1, d - 2 * t], C.adobeDark, Placement([at + w / 2 - t / 2, h, 0], 0, 0, 0))


def build_desert_home() -> PropGeometry:
    """A thick-walled, flat-roofed block with a smaller upper floor, a row of tilted solar panels
    on the roof and a cyan neon trim along the front."""
    s = SolidBuilder(True)
    lights = SolidBuilder()
    s.box([15, 6, 12], C.adobe, Placement(), C.adobeRoof)
    parapet(s, [15, 6, 12])
    s.box([7, 4, 6], C.adobe, Placement([-3, 6, 2], 0, 0, 0), C.adobeRoof)
    for x in [2.5, 5.5]:
        s.box([2.6, 0.3, 4], C.solar, Placement([x, 7, -2], 0, -0.45, 0))
    lights.box([15.2, 0.4, 0.4], L.cyan, Placement([0, 5.2, -6.2], 0, 0, 0))
    lights.box([2.4, 1.4, 0.4], L.window, Placement([-4, 2, -6.2], 0, 0, 0))
    lights.box([1.6, 1.2, 0.4], L.window, Placement([-3, 7.6, -1.2], 0, 0, 0))
    return PropGeometry(s.geometry, lights.geometry)


def build_beach_hut() -> PropGeometry:
    """A hut on short stilts under a pyramid thatch roof, with a lit window (islands, coast)."""
    s = SolidBuilder()
    lights = SolidBuilder()
    for x, z in [[-3, -3], [3, -3], [-3, 3], [3, 3]]:
        s.box([0.6, 2, 0.6], C.woodDark, Placement([x, 0, z], 0, 0, 0))
    s.box([8, 4, 8], C.wood, Placement([0, 2, 0], 0, 0, 0), C.thatch)
    s.lathe(
        [
            [7.2, 6],
            [0, 10],
        ],
        4,
        C.thatch,
        Placement(None, math.pi / 4, 0, 0),
    )
    lights.box([2, 1.2, 0.3], L.window, Placement([0, 3.4, -4.1], 0, 0, 0))
    return PropGeometry(s.geometry, lights.geometry)
