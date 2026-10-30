"""Trees of the green land (D-212), drawn as imposters

Sizes in model units, standing on Y = 0. The levels draw a picture of each tree baked from these
models (`imposter_bake_visual`), so their triangles cost nothing in play: crowns are clumps of rough
balls, pines tiers of rough cones, each facet its own shade of green.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.prop_look import PROP_COLORS as C
from game.config.trees import TREE_IDS
from render.geometry.rough import Roughness, rough_ball, rough_lathe
from render.geometry.solids import Placement, SolidBuilder
from render.scenery.scenery_look import PropGeometry

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402

Build = Callable[[list[float]], PropGeometry]
__pragma__("noskip")

# A pale bark for the birches, and the leaves: lighter than the props' (seen from above, packed in
# woods, darker ones turned black).
BIRCH_BARK = [0.72, 0.7, 0.64]
LEAF = [0.3, 0.5, 0.18]
LEAF_LIGHT = [0.46, 0.62, 0.24]
LEAF_DARK = [0.24, 0.42, 0.17]
NEEDLES = [0.23, 0.43, 0.25]
COPPER = [0.5, 0.32, 0.2]
# How rough the crowns are.
LEAVES = [0.22, 0.14, 0.25]
TIERS = [0.12, 0.1, 0.3]


def _rough(look: list[float], seed: int) -> Roughness:
    return Roughness(look[0], look[1], look[2], seed)


def trunk(s: SolidBuilder, height: float, radius: float, color: list[float]) -> None:
    """A tapering trunk."""
    s.cylinder(radius, height, 6, color, Placement([0, 0, 0]), radius * 0.6)


def crown(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    s: SolidBuilder,
    middle: list[float],
    size: list[float],
    clumps: int,
    color: list[float],
    seed: int,
) -> None:
    """A crown round `middle`: a big ball `size` (radius across, radius up), and `clumps` smaller
    ones round it, high and low, so its outline is lumpy."""
    across = size[0]
    up = size[1]
    rough_ball(s, middle, [across, up, across], color, _rough(LEAVES, seed))
    for k in range(clumps):
        a = (k / clumps) * math.pi * 2 + seed
        high = 0.35 if k % 2 == 0 else -0.25
        r = across * (0.55 if k % 2 == 0 else 0.5)
        at = [
            middle[0] + math.cos(a) * across * 0.7,
            middle[1] + high * up,
            middle[2] + math.sin(a) * across * 0.7,
        ]
        rough_ball(s, at, [r, r * 0.85, r], color, _rough(LEAVES, seed * 13 + k + 1))


def oak(leaves: list[float]) -> PropGeometry:
    """A broad tree: a short trunk under a wide lumpy crown."""
    s = SolidBuilder(True)
    trunk(s, 4, 0.45, C.bark)
    crown(s, [0, 5.6, 0], [2.4, 2], 6, leaves, 3)
    return PropGeometry(s.geometry, SolidBuilder().geometry)


def birch(_: list[float]) -> PropGeometry:
    """A slim pale-barked tree with a light, open crown."""
    s = SolidBuilder(True)
    trunk(s, 4.6, 0.28, BIRCH_BARK)
    crown(s, [0, 5.4, 0], [1.6, 1.8], 4, LEAF_LIGHT, 11)
    return PropGeometry(s.geometry, SolidBuilder().geometry)


def poplar(_: list[float]) -> PropGeometry:
    """A tall narrow tree."""
    s = SolidBuilder(True)
    trunk(s, 2, 0.35, C.bark)
    rough_ball(s, [0, 5.6, 0], [1.4, 4.4, 1.4], LEAF, _rough(LEAVES, 17))
    rough_ball(s, [0.5, 4, 0.3], [1, 2.2, 1], LEAF, _rough(LEAVES, 18))
    return PropGeometry(s.geometry, SolidBuilder().geometry)


def pine(_: list[float]) -> PropGeometry:
    """A conifer: tiers of rough cones, narrower going up."""
    s = SolidBuilder(True)
    trunk(s, 2.4, 0.32, C.bark)
    tiers = 4
    for k in range(tiers):
        t = k / tiers
        r = 2.4 * (1 - t * 0.7)
        y = 1.6 + k * 1.75
        h = 3.4 - t * 1
        profile = [[0, y], [r, y + 0.3], [r * 0.5, y + h * 0.55], [0, y + h]]
        rough_lathe(s, profile, 10, NEEDLES, _rough(TIERS, 23 + k), Placement([0, 0, 0]))
    return PropGeometry(s.geometry, SolidBuilder().geometry)


def bush(_: list[float]) -> PropGeometry:
    """A low clump of leaves."""
    s = SolidBuilder(True)
    rough_ball(s, [0, 0.9, 0], [1.4, 1, 1.4], LEAF_DARK, _rough(LEAVES, 31))
    rough_ball(s, [0.9, 0.7, 0.4], [0.9, 0.75, 0.9], LEAF, _rough(LEAVES, 32))
    rough_ball(s, [-0.6, 0.6, -0.7], [0.8, 0.65, 0.8], LEAF_DARK, _rough(LEAVES, 33))
    return PropGeometry(s.geometry, SolidBuilder().geometry)


def _model(build: Build, leaves: list[float]) -> Callable[[], PropGeometry]:
    """A factory of the tree `build` makes with `leaves`."""
    return lambda: build(leaves)


TREE_MODELS = {
    TREE_IDS.oak: _model(oak, LEAF),
    TREE_IDS.copper: _model(oak, COPPER),
    TREE_IDS.birch: _model(birch, LEAF_LIGHT),
    TREE_IDS.poplar: _model(poplar, LEAF),
    TREE_IDS.pine: _model(pine, NEEDLES),
    TREE_IDS.bush: _model(bush, LEAF_DARK),
}
