"""Living trees for the green section (Phase 4 review), ported from `props/green-tree-props.ts`.
Sizes in world units, standing on Y = 0."""

from game.config.prop_look import PROP_COLORS as C
from render.geometry.solids import Placement, SolidBuilder
from render.scenery.scenery_look import PropGeometry


def build_conifer() -> PropGeometry:
    """Conifer: a short trunk under three stacked cones."""
    s = SolidBuilder()
    s.cylinder(0.7, 3, 5, C.bark, Placement(), 0.5)
    tiers = [
        [4.2, 2.5, 7],
        [3.4, 5.5, 6.5],
        [2.4, 8.5, 6],
    ]
    for i, tier in enumerate(tiers):
        radius = tier[0]
        y = tier[1]
        height = tier[2]
        s.lathe(
            [
                [radius, y],
                [0, y + height],
            ],
            6,
            C.leaf if i == 1 else C.leafDark,
        )
    return PropGeometry(s.geometry)


def build_broadleaf_tree() -> PropGeometry:
    """Broadleaf tree: a trunk under a faceted round crown."""
    s = SolidBuilder()
    s.cylinder(0.9, 5, 5, C.bark, Placement(), 0.6)
    s.lathe(
        [
            [0, 3.8],
            [4.2, 5.5],
            [5.2, 8.5],
            [3.8, 11.5],
            [0, 12.8],
        ],
        7,
        C.leaf,
    )
    return PropGeometry(s.geometry)


def build_bush() -> PropGeometry:
    """A low, round bush in two tones."""
    s = SolidBuilder()
    s.lathe(
        [
            [3.2, 0],
            [3.4, 1.6],
            [2.2, 3.4],
            [0, 4],
        ],
        6,
        C.leafLight,
    )
    s.lathe(
        [
            [2, 0],
            [2.1, 1.2],
            [1.2, 2.6],
            [0, 3],
        ],
        5,
        C.leafDark,
        Placement([2.6, 0, 1.2], 0, 0, 0),
    )
    return PropGeometry(s.geometry)
