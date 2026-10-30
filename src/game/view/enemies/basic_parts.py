"""P16-R03: the pieces the basic kinds share (grafted gun barrels, a pair of fluttering membrane
wings, sinews and eyes) Logical pixels, nose +Z, Y up."""

import math

from org.transcrypt.stubs.browser import __pragma__

from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Vec3 = list[float]
type Rgb = list[float]
__pragma__("noskip")

from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.view.enemies.enemy_shapes import SIDES, decal  # noqa: E402
from game.view.enemies.organic_parts import opt  # noqa: E402
from render.geometry.organic import curve, tendril, vein  # noqa: E402

H = ENEMY_LOOK.hull
F = ENEMY_LOOK.flesh
WHITE = [1, 1, 1]  # type: list[float]
QUARTER = math.pi / 2


def gun_barrel(parts: Any, at: Vec3, length: float, yaw: float = 0) -> None:  # noqa: PLR0917
    """A small gun barrel grafted on (P16-R01: metal), from `at` along `yaw` (0: to the nose),
    `length` long, a charge light at its muzzle (phase 7 review), marked there."""

    def along(d: float) -> list[float]:
        return [at[0] + math.sin(yaw) * d, at[1], at[2] + math.cos(yaw) * d]

    parts.hull.cylinder(
        0.55, length, 5, H.dark, Placement([at[0], at[1], at[2]], yaw, QUARTER), 0.45
    )
    parts.charge.cylinder(0.6, 0.8, 5, WHITE, Placement(along(length), yaw, QUARTER))
    parts.muzzle(along(length + 0.8), "gun")


def mirror(outline: Any, s: float) -> list[list[float]]:
    """The outline mirrored by `s` across (x times `s`)."""
    return [[s * p[0], p[1]] for p in outline]


def wing_draw(  # noqa: PLR0917
    r: list[float], ts: list[list[float]], y: float, strut: float, lights: Any, glow: Rgb, s: int
) -> Any:
    """What a membrane wing draws in its model space (factory: no loop closure)."""

    def draw(w: Any) -> None:
        w.flesh.slab([r] + ts, [y - 0.25, y + 0.25], F.membrane)
        for t in ts:
            path = curve([r[0], y, r[1]], [t[0], y, t[1]], [0, 0.6, 0], 2)
            tendril(w.flesh, path, [strut, 0], 3, F.bone)
        tip = ts[0] if len(ts) > 0 else r
        mid = [(r[0] + tip[0]) / 2, y + 0.5, (r[1] + tip[1]) / 2]
        for light in lights if lights != None else []:  # noqa: E711
            decal(w.neon, mirror(light, s), y + 0.3, glow)
        if lights == None:  # noqa: E711
            vein(w.vein, [[r[0], y + 0.5, r[1]], mid], 0.5, glow)

    return draw


def wing_pair(parts: Any, shape: Any, glow: Rgb) -> None:
    """P16-R01, P16-R07: a pair of membrane wings, each fluttering from its root: a `membrane` skin
    spread from the root to its tips, a lean `bone` strut out to each tip, and either a steady
    neon light on it or a vein along its leading strut."""
    root = shape["root"]
    tips = shape["tips"]
    y = shape["y"]
    strut = shape["strut"]
    lights = opt(shape, "lights", None)
    for s in SIDES:
        r = [s * root[0], root[1]]
        ts = mirror(tips, s)
        span = max([abs(p[0] - root[0]) for p in tips])
        parts.flap([r[0], y, r[1]], s, span, wing_draw(r, ts, y, strut, lights, glow, s))


def sinew(parts: Any, start: Vec3, end: Vec3, bow: Vec3, radius: float) -> None:
    """A sinew from `start` to `end`, bowed by `bow`: three facets, thinning out."""
    tendril(parts.flesh, curve(start, end, bow, 2), [radius, radius * 0.5], 3, F.sinew)


def eye_pair(parts: Any, at: Vec3, gap: float, size: float, glow: Rgb) -> None:
    """A pair of small glowing eyes, `gap` apart across `at` (P16-R01: lit as veins): 8 triangles
    each."""
    bead = [[0, -size * 0.5], [size, 0], [0, size * 0.5]]
    for s in SIDES:
        parts.vein.lathe(bead, 4, glow, Placement([at[0] + s * gap, at[1], at[2]]))
