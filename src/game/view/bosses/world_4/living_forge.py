"""P16-R05, P16-R06: the Cyber-Organic pieces of the World 4 bosses (the volcanic, ash and foundry
world): scorched flesh swollen around metal grafts, molten veins and glands glowing ember. Logical
pixels, nose +Z, Y up.
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.enemy_look import ENEMY_LOOK  # noqa: E402
from game.config.record import record  # noqa: E402
from game.view.bosses.world_4.black_sands_kit import FORGE  # noqa: E402
from game.view.enemies.organic_parts import reactor_sac  # noqa: E402
from render.geometry.organic import curve, organ, ribs, tendril, vein  # noqa: E402
from render.geometry.solids import LoftOptions, Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
__pragma__("noskip")

# The flesh shades (P16-R01).
FL = ENEMY_LOOK.flesh
# Scorched flesh: the World 4 bodies, by role (base body, sinews and muscles, folds).
SKIN = record({"base": FL.crimson, "panel": FL.sinew, "dark": FL.membrane, "bone": FL.bone})
# The molten glow of their veins and glands.
MAGMA = FORGE.molten


def sinew(
    b: Any, ends: list[Vec3], radii: list[float], color: Rgb = SKIN.panel, bow: float = 1.5
) -> None:
    """A muscle or sinew from `a` to `b`, bowed up by `bow`, `r` thick at `a` thinning to `rb`."""
    a = ends[0]
    c = ends[1]
    tendril(b, curve(a, c, [0, bow, 0], 3), [radii[0], radii[1]], 5, color)


def back_ribs(p: Any, zs: list[float], arch: Any, color: Rgb = SKIN.bone) -> None:
    """Ribs arching over a back at each z of `zs`, bone pale. `arch` is a `RibSpec`."""
    ribs(p.flesh, zs, arch, color)


def glands(p: Any, at: list[Vec3], radius: float, glow: Rgb) -> None:
    """Glowing glands (pulsing, P16-R07) of `radius` at each point."""
    for g in at:
        organ(p.vein, radius, 5, glow, Placement(g), 0.6)


def lumps(
    p: Any, at: list[Vec3], radius: float, color: Rgb = SKIN.base, stretch: float = 0.7
) -> None:
    """Fleshy lumps (swollen growths) of `radius` at each point."""
    for g in at:
        organ(p.flesh, radius, 6, color, Placement(g), stretch)


def magma_vein(p: Any, points: list[Vec3], width: float, glow: Rgb = MAGMA) -> None:
    """A molten vein (pulsing) through `points`, `width` across."""
    for i in range(1, len(points)):
        a = points[i - 1]
        b = points[i]
        vein(p.vein, curve(a, b, [0, width * 0.6, 0], 2), width, glow)


def reactor_sacs(p: Any, at: list[Any], radius: float, glow: Any) -> None:
    """Reactors at the back, each set in a glowing flesh sac with a vein forward."""
    for r in at:
        reactor_sac(p, r, radius, glow, SKIN.base)


def _band_paint(seam: Rgb) -> Any:
    """Paints every other band of a loft `seam` (the bands alternate colours)."""

    def paint(_side: int, band: int) -> Any:
        if band % 2 == 1:
            return seam
        return None

    return paint


def flesh_shell(
    b: Any, section: list[Any], stations: list[Any], colors: list[Rgb] | None = None
) -> None:
    """A fleshy shell lofted through `stations` on `section`, its bands alternately `color`,
    `seam`."""
    if colors is None:
        colors = [SKIN.base, SKIN.dark]
    b.loft(section, stations, colors[0], None, LoftOptions(False, _band_paint(colors[1])))
