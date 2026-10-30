"""Desert and coast vegetation (P06-R06), ported from `props/desert-plants.ts`. Sizes in world
units, standing on Y = 0."""

import math

from game.config.prop_look import PROP_COLORS as C
from render.geometry.solids import Placement, SolidBuilder
from render.scenery.scenery_look import PropGeometry


def fronds(s: SolidBuilder, top: list[float], count: int) -> None:
    """Fronds of a palm: `count` long thin leaves leaning out and down from the crown."""
    for i in range(count):
        yaw = (2 * math.pi * i) / count + 0.3
        color = C.palmLeaf if i % 2 == 0 else C.leafDark
        s.box([1.6, 0.25, 7], color, Placement(top, yaw, 0.35, 0))


def build_palm_tree() -> PropGeometry:
    """A palm tree: a slightly bent ringed trunk with a crown of drooping fronds."""
    s = SolidBuilder()
    s.cylinder(0.8, 6, 5, C.palmTrunk, Placement(None, 0, 0, 0.08), 0.65)
    s.cylinder(0.65, 6, 5, C.palmTrunk, Placement([-0.45, 5.9, 0], 0, 0, 0.18), 0.5)
    fronds(s, [-1.5, 11.6, 0], 7)
    return PropGeometry(s.geometry)


def build_dry_bush() -> PropGeometry:
    """A dry, scraggly bush: two low olive and straw-coloured mounds."""
    s = SolidBuilder()
    s.lathe(
        [
            [2.6, 0],
            [2.4, 1.4],
            [1.2, 2.8],
            [0, 3.4],
        ],
        5,
        C.dryLeaf,
    )
    s.lathe(
        [
            [1.6, 0],
            [1.4, 1],
            [0, 1.8],
        ],
        4,
        C.dryLeafDark,
        Placement([2.2, 0, -1.4], 0, 0, 0),
    )
    return PropGeometry(s.geometry)


def build_cactus() -> PropGeometry:
    """A cactus-like plant: a tall ribbed column with two raised arms."""
    s = SolidBuilder()
    s.cylinder(1.1, 10, 6, C.cactus, Placement(), 0.8)
    s.box([3, 0.9, 0.9], C.cactus, Placement([1.6, 4, 0], 0, 0, 0))
    s.cylinder(0.6, 4, 5, C.cactus, Placement([3, 4, 0], 0, 0, 0), 0.45)
    s.box([2.4, 0.8, 0.8], C.cactus, Placement([-1.4, 6, 0], 0, 0, 0))
    s.cylinder(0.55, 3, 5, C.cactus, Placement([-2.5, 6, 0], 0, 0, 0), 0.4)
    return PropGeometry(s.geometry)
