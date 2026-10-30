"""P10-R11: the ash and heavy industry on the 4-2 bosses (the Ash Wraith and the Geyser Rig):
drifts of grey ash on their plates, soot streaks, glowing molten seams (GD-61, World 4: dark
metal with neon, plus soot, heat glow, molten seams). Ported from
`bosses/world-4/ash-plains-soot.ts`.
Logical pixels, nose +Z, Y up.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
type OutlinePoint = list[float]
__pragma__("noskip")

from game.view.bosses.final_boss_shapes import strip  # noqa: E402

# Ash: a pale grey, and a darker one where it lies thin over the metal.
ASH = [0.3, 0.29, 0.28]
ASH_THIN = [0.19, 0.185, 0.18]
# Soot: burnt black, a little warm.
SOOT = [0.03, 0.025, 0.025]
# The glow of hot metal in a seam (drawn on the neon builder: always lit).
EMBER = [1.0, 0.38, 0.06]
# A hot, rusty plate around a vent.
SCORCH = [0.17, 0.09, 0.05]


def _drift_point(k: int, radius: float, seed: float) -> OutlinePoint:
    a = (k * math.pi) / 3 + seed
    r = radius * (0.7 + 0.3 * math.sin(seed * 2.7 + k * 1.9))
    return [math.cos(a) * r, math.sin(a) * r]


def ash_drift(hull: Any, at: Vec3, radius: float, seed: float = 0) -> None:
    """A drift of ash `radius` wide lying at `at`: an uneven, low hexagon, paler on top. `seed`
    turns and bends its outline so no two drifts look alike."""
    outline = [_drift_point(k, radius, seed) for k in range(6)]
    hull.bevel_slab(outline, [-0.3, 0, 0.7], [0, radius * 0.3], ASH_THIN, Placement(at), ASH)


def soot_streaks(hull: Any, streaks: list[Any], y: float, width: float = 1.6) -> None:
    """Soot streaks at height `y`: a thin dark strip along each `[from, to]` (seen from above)."""
    for pair in streaks:
        strip(hull, pair[0], pair[1], width, [y, y + 0.15], SOOT)


def molten_seam(parts: Any, a: OutlinePoint, b: OutlinePoint, y: float, width: float = 1.4) -> None:
    """A molten seam from `a` to `b` (seen from above) at height `y`: a dark groove with a glowing
    line of hot metal in it. `parts` is the enemy's parts (its `hull` and `neon` builders)."""
    strip(parts.hull, a, b, width * 1.8, [y, y + 0.12], SOOT)
    strip(parts.neon, a, b, width * 0.6, [y + 0.12, y + 0.3], EMBER)
