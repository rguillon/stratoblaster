"""The wind turbine of the farms of Worlds 1 and 2 (P08-R07), ported from
`props/wind-turbine.ts`: the one World 2 prop still placed (moved out of the removed polar
outposts, D-163). Sizes in world units, standing on Y = 0."""

import math

from game.config.prop_look import PROP_COLORS as C
from game.config.prop_look import PROP_LIGHTS as L
from render.geometry.solids import Placement, SolidBuilder
from render.scenery.scenery_look import PropGeometry

BLADES = [0, (2 * math.pi) / 3, (4 * math.pi) / 3]


def build_wind_turbine() -> PropGeometry:
    """A wind turbine: a tall tapering mast on a pad, a nacelle at the top, and three long blades
    facing the road, one pointing up; a red light on the nacelle."""
    s = SolidBuilder()
    lights = SolidBuilder()
    s.box([5, 1, 5], C.concrete, Placement(), C.snow)
    s.cylinder(1, 30, 6, C.white, Placement([0, 1, 0], 0, 0, 0), 0.55)
    s.box([1.8, 2, 5], C.white, Placement([0, 30.4, 0.6], 0, 0, 0), C.snow)
    hub = [0, 31.4, -2.2]
    s.lathe(
        [
            [0.9, 0],
            [0, 1.4],
        ],
        5,
        C.white,
        Placement(hub, 0, -math.pi / 2, 0),
    )
    for roll in BLADES:
        s.box([0.9, 8.2, 0.3], C.white, Placement([0, 31.4, -2.4], 0, 0, roll))
    lights.box([0.5, 0.5, 0.5], L.red, Placement([0, 32.4, 2.4], 0, 0, 0))
    return PropGeometry(s.geometry, lights.geometry)
