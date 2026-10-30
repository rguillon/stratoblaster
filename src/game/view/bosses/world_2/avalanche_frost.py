"""The World 2 frost on the Avalanche and the Glacier Colossus (2-4), and the barrels drawn to
their muzzles, ported from `bosses/world-2/avalanche-frost.ts`. Logical pixels, nose +Z, Y up
(towards the camera).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.mini_boss_shapes import QUARTER, WHITE, H
from render.geometry.solids import Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Sequence  # noqa: E402

from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402
from render.geometry.outline import OutlinePoint  # noqa: E402
from render.geometry.solids import SolidBuilder  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
__pragma__("noskip")

# Snow and ice crust on the tops of the hull: pale blue-white.
FROST = [0.75, 0.82, 0.9]
# Old, packed snow, a little greyer.
PACKED = [0.58, 0.63, 0.7]
# Icicles and clear ice: a paler, bluer white.
ICE = [0.62, 0.78, 0.92]


def icicles(hull: SolidBuilder, points: list[Vec3], length: float) -> None:
    """Icicles hanging from each point, `length` long (each a thin four-sided spike)."""
    for i in range(len(points)):
        # Every other one shorter, so a row does not read as a comb.
        drop = length * (1 if i % 2 == 0 else 0.6)
        hull.cylinder(drop * 0.18, drop, 4, ICE, Placement(points[i], i * 0.7, math.pi), 0)


def snow_cap(
    hull: SolidBuilder,
    outline: list[OutlinePoint],
    y: float,
    thick: float,
    color: Rgb = FROST,
) -> None:
    """A snow cap: `outline` (seen from above) lying `thick` deep on a top surface at height `y`."""
    hull.bevel_slab(outline, [y - 0.3, y, y + thick], [0, thick * 0.8], color)


def barrel_to(
    parts: EnemyParts,
    tip: Sequence[float],
    dims: list[float],
    kind: str = "gun",
) -> None:
    """A gun barrel pointing down the screen (+Z), drawn back from its muzzle `tip` (a design's
    `Muzzle`): a dark barrel `length` long, a charge light at its mouth, and the muzzle's marker
    (phase 7 review, D-057), firing `kind`."""
    hull = parts.hull
    charge = parts.charge
    muzzle = parts.muzzle
    radius = dims[0]
    length = dims[1]
    x, y, z = boss_point(tip[0], tip[1], tip[2])
    light = radius * 1.2
    hull.cylinder(radius, length, 6, H.dark, Placement([x, y, z - light - length], 0, QUARTER))
    charge.cylinder(radius * 0.92, light, 6, WHITE, Placement([x, y, z - light], 0, QUARTER))
    muzzle([x, y, z], kind)
