"""Futuristic homes (P04-R04) Sizes in world units, standing
on Y = 0."""

from game.config.prop_look import PROP_COLORS as C
from game.config.prop_look import PROP_LIGHTS as L
from render.geometry.solids import Placement, SolidBuilder
from render.scenery.scenery_look import PropGeometry


def build_cube_home() -> PropGeometry:
    """Two offset slabs with a cantilevered upper floor and lit window strips."""
    s = SolidBuilder()
    lights = SolidBuilder()
    s.box([16, 6, 12], C.white, Placement(), C.concreteDark)
    s.box([12, 5, 10], C.concreteDark, Placement([3, 6, 2], 0, 0, 0), C.roof)
    lights.box([10, 1.4, 0.4], L.window, Placement([-2, 2.6, -6.2], 0, 0, 0))
    lights.box([8, 1.2, 0.4], L.window, Placement([3, 8.2, -3.2], 0, 0, 0))
    lights.box([12.4, 0.4, 0.4], L.cyan, Placement([3, 11, -3.2], 0, 0, 0))
    return PropGeometry(s.geometry, lights.geometry)


def build_dome_home() -> PropGeometry:
    """A low faceted dome with a ring of windows."""
    s = SolidBuilder()
    lights = SolidBuilder()
    s.lathe(
        [
            [9, 0],
            [8.6, 3],
            [6.6, 6.4],
            [3.5, 8.5],
            [0, 9.2],
        ],
        10,
        C.white,
    )
    s.box([3, 4, 3], C.concreteDark, Placement([0, 0, -8.6], 0, 0, 0))
    lights.ring(8.75, 0.8, 10, L.cyan, Placement([0, 2.2, 0], 0, 0, 0))
    lights.box([1.6, 2.6, 0.4], L.window, Placement([0, 0.4, -10.2], 0, 0, 0))
    return PropGeometry(s.geometry, lights.geometry)
