# Copyright (c) 2026 Renaud Guillon
"""The geometry of a tree prop (D-212, D-214): its solid, and a stand-in for its shadow.

GFX-PROP-12.
"""

from render.geometry.solids import SolidBuilder
from render.scenery.scenery_look import PropGeometry


def tree_geometry(s: SolidBuilder, shadow: SolidBuilder) -> PropGeometry:
    """Return the tree built into `s`, with `shadow` as the stand-in that casts its shadow.

    `shadow` is a few low-poly solids.
    """
    return PropGeometry(s.geometry, SolidBuilder().geometry, None, None, shadow.geometry)
