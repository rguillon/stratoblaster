"""Farms of the green land (P06-R06, reviewer 2026-10-26), ported from `props/farm-props.ts`.
Sizes in world units, on Y = 0."""

import math

from game.config.prop_look import PROP_COLORS as C
from game.config.prop_look import PROP_LIGHTS as L
from render.geometry.solids import Placement, SolidBuilder
from render.scenery.scenery_look import PropGeometry


def gable_roof(s: SolidBuilder, size: list[float], rise: float) -> None:
    """A pitched roof over a block `w × d` whose walls are `h` high, the ridge along X."""
    w = size[0]
    h = size[1]
    d = size[2]
    slope = math.atan2(rise, d / 2)
    run = math.sqrt(rise * rise + (d / 2) * (d / 2)) + 0.6
    s.box([w + 0.8, 0.5, run], C.farmRoof, Placement([0, h + rise / 2, -d / 4], 0, -slope, 0))
    s.box([w + 0.8, 0.5, run], C.farmRoof, Placement([0, h + rise / 2, d / 4], 0, slope, 0))
    # The gable ends, wound like the box's side faces at -X and +X.
    x0 = -w / 2
    x1 = w / 2
    s.face(
        [
            [x0, h, d / 2],
            [x0, h + rise, 0],
            [x0, h, -d / 2],
        ],
        C.farmWall,
    )
    s.face(
        [
            [x1, h, -d / 2],
            [x1, h + rise, 0],
            [x1, h, d / 2],
        ],
        C.farmWall,
    )


def build_farmhouse() -> PropGeometry:
    """A long barn under a dark pitched roof, a lower wing, and a cyan neon line along the ridge."""
    s = SolidBuilder(True)
    lights = SolidBuilder()
    s.box([14, 5, 9], C.farmWall)
    gable_roof(s, [14, 5, 9], 3.5)
    s.box([6, 3.5, 6], C.farmWall, Placement([-3, 0, 6.5], 0, 0, 0), C.roof)
    lights.box([14.6, 0.35, 0.35], L.cyan, Placement([0, 8.6, 0], 0, 0, 0))
    lights.box([3, 2.6, 0.3], L.window, Placement([3, 0.2, -4.6], 0, 0, 0))
    lights.box([1.8, 1.2, 0.3], L.window, Placement([-4, 2, -4.6], 0, 0, 0))
    return PropGeometry(s.geometry, lights.geometry)


def build_greenhouse() -> PropGeometry:
    """A long glass greenhouse on a low wall, its grow lights glowing pink through the roof."""
    s = SolidBuilder(True)
    lights = SolidBuilder()
    s.box([16, 1, 7], C.concrete)
    s.box([16, 2.5, 7], C.glassGreen, Placement([0, 1, 0], 0, 0, 0), C.glassGreen)
    gable_roof(s, [15.2, 3.5, 7], 2)
    for x in [-8, 0, 8]:
        s.box([0.5, 5.5, 7.2], C.metalDark, Placement([x, 0, 0], 0, 0, 0))
    lights.box([15, 0.3, 0.6], L.pink, Placement([0, 3.2, -1.6], 0, 0, 0))
    lights.box([15, 0.3, 0.6], L.pink, Placement([0, 3.2, 1.6], 0, 0, 0))
    return PropGeometry(s.geometry, lights.geometry)


def build_grain_silos() -> PropGeometry:
    """Three grain silos with domed tops on a concrete pad, an auger tower and a red light."""
    s = SolidBuilder()
    lights = SolidBuilder()
    s.box([15, 0.6, 7], C.concrete)
    for x in [-5, 0, 5]:
        s.cylinder(2.3, 11, 8, C.silver, Placement([x, 0.6, 0], 0, 0, 0))
        s.lathe(
            [
                [2.4, 11.6],
                [1.4, 13],
                [0, 13.6],
            ],
            8,
            C.metal,
            Placement([x, 0, 0], 0, 0, 0),
        )
    s.box([1.6, 16, 1.6], C.metalDark, Placement([6.5, 0, -3], 0, 0, 0))
    s.box([12, 0.6, 0.6], C.metalDark, Placement([0.5, 14.5, -3], 0, 0, 0))
    lights.ring(2.35, 0.4, 8, L.yellow, Placement([0, 9, 0], 0, 0, 0))
    lights.box([0.8, 0.8, 0.8], L.red, Placement([6.5, 16, -3], 0, 0, 0))
    return PropGeometry(s.geometry, lights.geometry)
