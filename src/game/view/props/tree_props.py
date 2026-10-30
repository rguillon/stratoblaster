"""Dead trees, a leafless trunk with a few bare branches (P04-R04), ported from
`props/tree-props.ts`. Sizes in world units."""

from game.config.prop_look import PROP_COLORS as C
from render.geometry.solids import Placement, SolidBuilder
from render.scenery.scenery_look import PropGeometry


def branch(s: SolidBuilder, y: float, length: float, lean: float, yaw: float) -> None:
    """Branch: a thin tapered cylinder leaning `lean` radians from vertical, turned by `yaw`."""
    s.cylinder(0.5, length, 4, C.woodDark, Placement([0, y, 0], yaw, 0, lean), 0.12)


def build_dead_tree() -> PropGeometry:
    """Tall dead tree with three branches."""
    s = SolidBuilder()
    s.cylinder(1.2, 16, 5, C.wood, Placement(), 0.45)
    branch(s, 7, 7, 0.9, 0.3)
    branch(s, 10, 6, 0.8, 2.4)
    branch(s, 12.5, 5, 0.7, 4.3)
    return PropGeometry(s.geometry)


def build_forked_tree() -> PropGeometry:
    """Short dead tree with a bent trunk forking at the top."""
    s = SolidBuilder()
    s.cylinder(1.1, 7, 5, C.wood, Placement(None, 0, 0, 0.15), 0.8)
    s.cylinder(0.8, 6, 5, C.wood, Placement([-1, 6.8, 0], 0, 0, 0.5), 0.2)
    s.cylinder(0.7, 5, 5, C.wood, Placement([-1, 6.8, 0], 0.6, 0, -0.55), 0.15)
    branch(s, 4, 4, 1.1, 3.6)
    return PropGeometry(s.geometry)
