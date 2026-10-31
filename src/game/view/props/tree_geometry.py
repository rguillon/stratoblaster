"""The geometry of a tree prop (D-212, D-214): its solid, and a stand-in for its shadow."""

from render.geometry.solids import SolidBuilder
from render.scenery.scenery_look import PropGeometry


def tree_geometry(s: SolidBuilder, shadow: SolidBuilder) -> PropGeometry:
    """The tree built into `s`, with `shadow` (a few low-poly solids) as the stand-in that casts
    its shadow."""
    return PropGeometry(s.geometry, SolidBuilder().geometry, None, None, shadow.geometry)
