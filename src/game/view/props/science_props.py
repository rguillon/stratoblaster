"""Technical and scientific installations (P04-R04), ported from `props/science-props.ts`.
Sizes in world units, standing on Y = 0."""

import math

from game.config.prop_look import PROP_COLORS as C
from game.config.prop_look import PROP_LIGHTS as L
from render.geometry.solids import Placement, SolidBuilder
from render.scenery.scenery_look import PropGeometry


def build_antenna_mast() -> PropGeometry:
    """Tall lattice-like antenna mast with crossbars and red aviation lights."""
    s = SolidBuilder()
    lights = SolidBuilder()
    s.box([7, 4, 5], C.concreteDark, Placement([5, 0, 0], 0, 0, 0), C.roof)
    s.cylinder(3, 52, 4, C.metal, Placement(None, math.pi / 4, 0, 0), 0.5)
    for y, w in [[22, 10], [38, 7]]:
        s.box([w, 0.8, 0.8], C.metalDark, Placement([0, y, 0], 0, 0, 0))
        s.box([0.8, 0.8, w], C.metalDark, Placement([0, y, 0], 0, 0, 0))
    for y in [30, 52]:
        lights.box([1.4, 1.4, 1.4], L.red, Placement([0, y, 0], 0, 0, 0))
    return PropGeometry(s.geometry, lights.geometry)
