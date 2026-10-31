"""Trees of the green land (D-212), drawn as imposters

Sizes in model units, standing on Y = 0. The levels draw a picture of each tree baked from these
models (`imposter_bake_visual`), so their triangles cost nothing in play: crowns are clouds of
hundreds of small leaf tufts, each turned its own way and shaded its own green, darker inside the
crown and under it, round a dark core that fills the gaps; pines are tiers of drooping needle tufts.
Each tree also has a stand-in of a few low-poly solids that only casts its shadow (its picture, a
quad facing the camera, would cast a wrong one).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.prop_look import PROP_COLORS as C
from game.config.trees import TREE_IDS
from game.view.props.dead_tree_props import dead_bush, dead_oak, dead_pine, snag
from game.view.props.tree_geometry import tree_geometry
from render.geometry.rough import Leaves, Roughness, leaf_cloud, leaf_cone, rough_ball, rough_lathe
from render.geometry.solids import Placement, SolidBuilder
from render.scenery.scenery_look import PropGeometry

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402

Palette = list[list[float]]
__pragma__("noskip")

BIRCH_BARK = [0.72, 0.7, 0.64]
# The leaves' greens, a few per tree (yellower, bluer, lighter, darker), so a crown is not one
# colour.
OAK = [[0.36, 0.56, 0.2], [0.43, 0.62, 0.22], [0.3, 0.5, 0.19], [0.5, 0.64, 0.24]]
BIRCH = [[0.54, 0.7, 0.3], [0.62, 0.74, 0.35], [0.47, 0.65, 0.27]]
POPLAR = [[0.36, 0.58, 0.23], [0.43, 0.62, 0.26], [0.31, 0.52, 0.22]]
NEEDLES = [[0.25, 0.47, 0.29], [0.29, 0.52, 0.31], [0.21, 0.42, 0.27]]
BUSH = [[0.34, 0.54, 0.2], [0.4, 0.58, 0.22], [0.29, 0.48, 0.19]]
COPPER = [[0.6, 0.36, 0.23], [0.52, 0.29, 0.2], [0.66, 0.42, 0.27]]
# How dark the core inside a crown is, next to its leaves.
CORE = 0.55


def _leaves(palette: Palette, count: int, size: float) -> Leaves:
    """Leaves of `palette`: `count` tufts about `size` across, in the outer 35 % of the crown."""
    return Leaves(palette, count, size, 0.35, 0.3, 0.2, 0.12)


def _core(palette: Palette) -> list[float]:
    c = palette[0]
    return [c[0] * CORE, c[1] * CORE, c[2] * CORE]


def trunk(s: SolidBuilder, height: float, radius: float, color: list[float]) -> None:
    """A tapering trunk."""
    s.cylinder(radius, height, 6, color, Placement([0, 0, 0]), radius * 0.6)


def clump(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    s: SolidBuilder,
    centre: list[float],
    radii: list[float],
    palette: Palette,
    density: float,
    seed: int,
) -> None:
    """A clump of leaves round `centre`: a dark core and a cloud of tufts over it, `density` tufts
    per unit of its surface."""
    core = [radii[0] * 0.8, radii[1] * 0.8, radii[2] * 0.8]
    rough_ball(s, centre, core, _core(palette), Roughness(0.15, 0.1, 0.3, seed))
    area = 4 * math.pi * (radii[0] * radii[1] + radii[1] * radii[2] + radii[0] * radii[2]) / 3
    leaf_cloud(s, centre, radii, _leaves(palette, math.floor(area * density), 0.75), seed + 1)


def crown(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    s: SolidBuilder,
    middle: list[float],
    size: list[float],
    lobes: int,
    palette: Palette,
    seed: int,
) -> None:
    """A lumpy crown round `middle`: a big clump `size` (radius across, radius up) and `lobes`
    smaller ones round it, high and low."""
    across = size[0]
    up = size[1]
    parts = [[middle, [across, up, across]]]
    for k in range(lobes):
        a = (k / lobes) * math.pi * 2 + seed
        high = 0.35 if k % 2 == 0 else -0.2
        r = across * (0.55 if k % 2 == 0 else 0.5)
        at = [
            middle[0] + math.cos(a) * across * 0.7,
            middle[1] + high * up,
            middle[2] + math.sin(a) * across * 0.7,
        ]
        parts.append([at, [r, r * 0.85, r]])
    for k in range(len(parts)):
        clump(s, parts[k][0], parts[k][1], palette, 9, seed * 17 + k * 3)


def stand_in(centre: list[float], radii: list[float]) -> SolidBuilder:
    """The shadow's stand-in: one low-poly ball round the whole crown (`centre`, `radii`), 20
    triangles (thousands of trees cast it; the trunk's thin shadow is left out)."""
    s = SolidBuilder()
    profile: list[list[float]] = [[0, -1], [0.9, -0.45], [0.9, 0.45], [0, 1]]
    stretched = [[p[0] * radii[0], p[1] * radii[1]] for p in profile]
    s.lathe(stretched, 5, [0, 0, 0], Placement(centre))
    return s


def broadleaf(palette: Palette) -> PropGeometry:
    """A broad tree (an oak, a copper beech): a short trunk under a wide lumpy crown."""
    s = SolidBuilder(True)
    trunk(s, 4, 0.45, C.bark)
    crown(s, [0, 5.6, 0], [2.4, 2], 6, palette, 3)
    return tree_geometry(s, stand_in([0, 5.6, 0], [3.2, 2.4, 3.2]))


def birch(palette: Palette) -> PropGeometry:
    """A slim pale-barked tree with a light, open crown on a few branches."""
    s = SolidBuilder(True)
    trunk(s, 5, 0.26, BIRCH_BARK)
    parts: list[list[list[float]]] = []
    for k in range(4):
        a = k * math.pi / 2 + 0.4
        tip = [math.cos(a) * 1.1, 4.4 + (k % 2) * 0.8, math.sin(a) * 1.1]
        s.cylinder(0.08, 1.6, 4, BIRCH_BARK, Placement([0, 3.2, 0], -a, 0, -0.7), 0.05)
        parts.append([tip, [1, 1.1, 1]])
    parts.append([[0, 5.6, 0], [1.2, 1.4, 1.2]])
    for k in range(len(parts)):
        clump(s, parts[k][0], parts[k][1], palette, 7, 40 + k)
    return tree_geometry(s, stand_in([0, 5.2, 0], [2, 1.9, 2]))


def poplar(palette: Palette) -> PropGeometry:
    """A tall narrow tree."""
    s = SolidBuilder(True)
    trunk(s, 2, 0.35, C.bark)
    parts = [[[0, 5.6, 0], [1.4, 4.4, 1.4]], [[0.5, 4, 0.3], [1, 2.2, 1]]]
    for k in range(len(parts)):
        clump(s, parts[k][0], parts[k][1], palette, 9, 17 + k * 5)
    return tree_geometry(s, stand_in([0, 5.4, 0], [1.6, 4.4, 1.6]))


def pine(palette: Palette) -> PropGeometry:
    """A conifer: tiers of drooping needle tufts round dark cones, narrower going up."""
    s = SolidBuilder(True)
    trunk(s, 2.4, 0.32, C.bark)
    shadow = SolidBuilder()
    tiers = 4
    for k in range(tiers):
        t = k / tiers
        r = 2.4 * (1 - t * 0.7)
        y = 1.6 + k * 1.75
        h = 3.4 - t * 1
        core = [[0, y + 0.2], [r * 0.85, y + 0.4], [0, y + h * 0.95]]
        rough_lathe(
            s, core, 8, _core(palette), Roughness(0.1, 0.1, 0.3, 23 + k), Placement([0, 0, 0])
        )
        count = math.floor(math.pi * r * math.sqrt(r * r + h * h) * 10)
        leaf_cone(s, [0, y, 0], [r, h], _leaves(palette, count, 0.6), 60 + k)
    # One cone over all the tiers.
    shadow.lathe([[0, 1.6], [2.4, 1.9], [0, 10.6]], 5, [0, 0, 0], Placement([0, 0, 0]))
    return tree_geometry(s, shadow)


def bush(palette: Palette) -> PropGeometry:
    """A low clump of leaves."""
    s = SolidBuilder(True)
    parts = [
        [[0, 0.9, 0], [1.4, 1, 1.4]],
        [[0.9, 0.7, 0.4], [0.9, 0.75, 0.9]],
        [[-0.6, 0.6, -0.7], [0.8, 0.65, 0.8]],
    ]
    for k in range(len(parts)):
        clump(s, parts[k][0], parts[k][1], palette, 10, 31 + k * 3)
    return tree_geometry(s, stand_in([0.1, 0.8, -0.1], [1.9, 1.1, 1.9]))


def _model(
    build: Callable[[Palette], PropGeometry], palette: Palette
) -> Callable[[], PropGeometry]:
    """A factory of the tree `build` makes with `palette`."""
    return lambda: build(palette)


TREE_MODELS = {
    TREE_IDS.oak: _model(broadleaf, OAK),
    TREE_IDS.copper: _model(broadleaf, COPPER),
    TREE_IDS.birch: _model(birch, BIRCH),
    TREE_IDS.poplar: _model(poplar, POPLAR),
    TREE_IDS.pine: _model(pine, NEEDLES),
    TREE_IDS.bush: _model(bush, BUSH),
    # D-214: the dead trees of the desert.
    TREE_IDS.deadOak: dead_oak,
    TREE_IDS.deadPine: dead_pine,
    TREE_IDS.snag: snag,
    TREE_IDS.deadBush: dead_bush,
}
