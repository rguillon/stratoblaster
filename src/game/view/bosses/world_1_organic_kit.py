"""P16-R05, P16-R06: the Cyber-Organic pieces of the World 1 boss models (living bodies with metal
grafts), ported from `bosses/world-1-organic-kit.ts`. Logical pixels, nose +Z, Y up.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.view.enemies.organic_parts import opt  # noqa: E402
from render.geometry.organic import (  # noqa: E402
    RibSpec,
    SegmentedBody,
    carapace,
    curve,
    organ,
    plate,
    ribs,
    segmented_body,
    tendril,
    vein,
)
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Rgb = list[Any]
type Vec3 = list[Any]
__pragma__("noskip")

# Flesh shades (P16-R01).
F = ENEMY_LOOK.flesh
# Hull shades of the grafts (P16-R01).
M = ENEMY_LOOK.hull
# Rivets on the grafted plates: worn metal.
RIVET = [0.24, 0.24, 0.27]


def _options(options: Any) -> Any:
    """An options object, or none: `{}` when the caller leaves it out."""
    return {} if options == None else options  # noqa: E711


def hide(parts: Any, h: Any) -> None:
    """Draws a creature's body along Z (`Hide` in the TypeScript): a swollen belly in flesh, a
    carapace over it, both in `flesh`."""
    flesh = parts.flesh
    at = opt(h, "at", [0, 0, 0])
    place = Placement(at)
    girth = opt(h, "girth", None)
    mid = (h.bottom + h.top) / 2
    segmented_body(
        flesh,
        SegmentedBody(h.tail, h.nose, h.segments, h.width, h.bottom, mid, 0.15, girth),
        h.belly,
        place,
    )
    carapace(
        flesh,
        SegmentedBody(h.tail, h.nose, h.segments, h.width * 0.92, mid - 1, h.top, None, girth),
        h.shell,
        place,
    )


def spine(parts: Any, start: Vec3, end: Vec3, options: Any) -> None:
    """A glowing vein along the back from `start` to `end`, bowed up by `bow`."""
    width = opt(options, "width", 1.2)
    bow = opt(options, "bow", 2)
    vein(parts.vein, curve(start, end, [0, bow, 0], 4), width, options["color"])


def vein_line(p: Any, start: Vec3, end: Vec3, bow: Vec3, width: float, color: Rgb) -> None:
    """A vein from `start` to `end`, bowed by `bow`."""
    vein(p.vein, curve(start, end, bow, 3), width, color)


def rib_cage(parts: Any, zs: list[Any], arch: Any, color: Any = None, place: Any = None) -> None:
    """Bone ribs arching over a back at each Z of `zs`."""
    flesh = parts.flesh
    the_color = F.bone if color == None else color  # noqa: E711
    the_place = Placement() if place == None else place  # noqa: E711
    ribs(
        flesh,
        zs,
        _rib_spec(arch),
        the_color,
        the_place,
    )


def _rib_spec(arch: Any) -> Any:
    """The `RibSpec` of an arch object `{halfWidth, y, height, thickness}`."""
    return RibSpec(arch.halfWidth, arch.y, arch.height, arch.thickness)


def tentacle(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
    parts: Any,
    start: Vec3,
    end: Vec3,
    bow: Vec3,
    radii: list[Any],
    color: Any = None,
    sides: Any = 4,
) -> None:
    """A tentacle, sinew or limb of flesh from `start` to `end`, bowed by `bow`, `radii[0]` thick
    at its root."""
    the_color = F.sinew if color == None else color  # noqa: E711
    tendril(parts.flesh, curve(start, end, bow, 4), [radii[0], radii[1]], sides, the_color)


def gland(p: Any, at: Vec3, r: float, glow: Rgb, bed: Any = None) -> None:
    """A gland: a lit bulb on a flesh bed, `r` across, at `at`."""
    the_bed = F.crimson if bed == None else bed  # noqa: E711
    organ(p.flesh, r * 1.5, 6, the_bed, Placement(at), 0.35)
    organ(p.vein, r, 5, glow, Placement([at[0], at[1] + r * 0.6, at[2]]), 0.6)


def sac(p: Any, at: Vec3, r: float, color: Rgb, options: Any = None) -> None:
    """A swollen organ of `r` at `at` (squashed by `stretch`), `sides` facets round."""
    opts = _options(options)
    stretch = opt(opts, "stretch", 0.6)
    sides = opt(opts, "sides", 7)
    yaw = opt(opts, "yaw", 0)
    organ(p.flesh, r, sides, color, Placement(at, yaw), stretch)


def graft(p: Any, outline: list[Any], heights: list[Any], at: Vec3, options: Any = None) -> None:
    """A grafted armour plate of `outline` (around `at`), `heights` thick, riveted."""
    opts = _options(options)
    color = opt(opts, "color", M.panel)
    yaw = opt(opts, "yaw", 0)
    plate(p.hull, outline, [heights[0], heights[1]], [color, RIVET], Placement(at, yaw))


def polygon(n: int, r: float, scale: Any = None) -> list[Any]:
    """A regular polygon of `n` corners and radius `r` (a plate outline), stretched by `scale`
    (`[sx, sz]`)."""
    sx = 1 if scale == None else scale[0]  # noqa: E711
    sz = 1 if scale == None else scale[1]  # noqa: E711
    result: list[Any] = []
    for k in range(n):
        a = (2 * math.pi * (k + 0.5)) / n
        result.append([math.sin(a) * r * sx, math.cos(a) * r * sz])
    return result


def growth(p: Any, at: Vec3, r: float, glow: Rgb, options: Any = None) -> None:
    """An armoured growth (P16-R05): a swollen flesh mound of `r` around `at`, a vein ring at its
    foot and grafted armour on its crown, so it reads as one clear target."""
    opts = _options(options)
    flesh = opt(opts, "flesh", F.crimson)
    height = opt(opts, "height", 0.45)
    armour = opt(opts, "armour", True)
    organ(p.flesh, r, 8, flesh, Placement(at, math.pi / 8), height)
    p.vein.ring(
        r * 0.9,
        r * 0.06,
        8,
        glow,
        Placement([at[0], at[1] + r * 0.15, at[2]], math.pi / 8),
    )
    if armour:
        graft(
            p,
            polygon(6, r * 0.62),
            [r * height * 0.75, r * height * 0.95],
            at,
            {"color": M.base},
        )


def mantle(p: Any, outline: list[Any], heights: list[Any], color: Rgb, rim: Any = None) -> None:
    """A fleshy skirt (a mantle, a fin fold) of `outline` from `heights[0]` to `heights[1]`, its
    rim lined by a vein, tinted `color`."""
    y0 = heights[0]
    y1 = heights[1]
    p.flesh.bevel_slab(outline, [y0, (y0 + y1) / 2, y1], [1.5, 2.5], color)
    if rim == None:  # noqa: E711
        return
    ring: list[Any] = []
    ring.extend(outline)
    ring.append(outline[0])
    y = (y0 + y1) / 2 + 0.2
    lifted: list[Vec3] = []
    for q in ring:
        lifted.append([q[0] * 1.005, y, q[1] * 1.005])
    vein(p.vein, lifted, 0.9, rim)


def scale_outline(outline: list[Any], k: float, dx: float = 0, dz: float = 0) -> list[Any]:
    """The outline `outline` scaled by `k` around the origin, then moved by `[dx, dz]`."""
    result: list[Any] = []
    for q in outline:
        result.append([q[0] * k + dx, q[1] * k + dz])
    return result


def barbs(parts: Any, at: Vec3, options: Any, color: Any = None) -> None:
    """A row of `count` teeth or barbs of bone along X at `at`, `size` long, along `dir`."""
    the_color = F.bone if color == None else color  # noqa: E711
    count = options["count"]
    spacing = options["spacing"]
    size = options["size"]
    direction = options["dir"]
    for i in range(count):
        x = at[0] + (i - (count - 1) / 2) * spacing
        root = [x, at[1], at[2]]
        tip = [
            x + direction[0] * size,
            at[1] + direction[1] * size,
            at[2] + direction[2] * size,
        ]
        tendril(parts.flesh, [root, tip], [size * 0.25, 0], 3, the_color)
