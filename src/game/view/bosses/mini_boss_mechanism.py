"""P07-R05 (phase 7 review: fat armour over a complex mechanism): the machinery seen through the
gaps between the World 1 mini bosses' armour plates
Logical pixels, nose +Z, Y up. Darker than the armour, and set a little lower, so it reads in the
gaps under the ~35° camera.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.view.bosses.mini_boss_shapes import SHADE, H  # noqa: E402
from render.geometry.outline import hypot3  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Rgb = list[Any]
type Vec3 = list[Any]
__pragma__("noskip")

# Gear metal: darker than the hull's panels, lighter than its shadows.
GEAR = [0.07, 0.07, 0.085]


def cog(hull: Any, at: Vec3, radius: float, teeth: int, yaw: float = 0) -> None:
    """A cog lying flat at `at`: a toothed disc `radius` wide with `teeth` teeth, and its hub."""
    outline: list[Any] = []
    for k in range(teeth * 2):
        a = (math.pi * k) / teeth
        r = radius if k % 2 == 0 else radius * 0.78
        outline.append([math.sin(a) * r, math.cos(a) * r])
    hull.slab(outline, [0, radius * 0.3], GEAR, Placement(at, yaw), H.panel)
    hull.cylinder(radius * 0.32, radius * 0.5, 6, SHADE["edge"], Placement(at))


def aim(a: Vec3, b: Vec3) -> list[Any]:
    """The length, and the pitch and yaw that turn a solid's +Y axis along `a` -> `b`."""
    dx = b[0] - a[0]
    dy = b[1] - a[1]
    dz = b[2] - a[2]
    length = hypot3(dx, dy, dz)
    return [length, math.acos(dy / length), math.atan2(dx, dz)]


def ram(hull: Any, start: Vec3, end: Vec3, radius: float) -> None:
    """A hydraulic ram from `start` to `end`: a fat dark cylinder, then its bright piston rod."""
    aimed = aim(start, end)
    length = aimed[0]
    pitch = aimed[1]
    yaw = aimed[2]
    hull.cylinder(radius, length * 0.55, 6, GEAR, Placement(start, yaw, pitch))
    hull.cylinder(radius * 0.45, length, 4, SHADE["edge"], Placement(start, yaw, pitch))
    hull.cylinder(radius * 1.2, radius * 1.2, 6, H.dark, Placement(end, yaw, pitch))


def conduit(hull: Any, start: Vec3, end: Vec3, radius: float, ribs: int) -> None:
    """A ribbed conduit from `start` to `end`: a pipe with `ribs` collars along it."""
    aimed = aim(start, end)
    length = aimed[0]
    pitch = aimed[1]
    yaw = aimed[2]
    hull.cylinder(radius, length, 4, H.dark, Placement(start, yaw, pitch))
    for i in range(1, ribs + 1):
        t = i / (ribs + 1)
        at = [
            start[0] + (end[0] - start[0]) * t,
            start[1] + (end[1] - start[1]) * t,
            start[2] + (end[2] - start[2]) * t,
        ]
        hull.cylinder(radius * 1.5, radius * 0.7, 6, GEAR, Placement(at, yaw, pitch))


def glow_line(neon: Any, start: Vec3, end: Vec3, width: float, color: Rgb) -> None:
    """A glowing line deep in a gap, from `start` to `end`: a lit coolant or power conduit."""
    aimed = aim(start, end)
    neon.cylinder(width / 2, aimed[0], 4, color, Placement(start, aimed[2], aimed[1]))
