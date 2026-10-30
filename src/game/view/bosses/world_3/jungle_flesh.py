"""P16-R05, P16-R06: the Cyber-Organic pieces of the World 3 bosses (the jungle and its river):
living bodies grown over by the jungle, metal grafted on. Ported from
`view/bosses/world-3/jungle-flesh.ts`. Logical pixels, nose +Z, Y up."""

from org.transcrypt.stubs.browser import __pragma__

from game.config.enemy_look import ENEMY_LOOK
from render.geometry.organic import RibSpec, carapace, curve, organ, ribs, tendril, vein
from render.geometry.solids import Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
__pragma__("noskip")

# The flesh shades (P16-R01).
F = ENEMY_LOOK.flesh

# A jungle-green flesh, dark enough for the ground (P14-R04): moss-skinned bodies.
JUNGLE_FLESH = [0.05, 0.1, 0.045]


def table(rows: Any) -> Any:
    """A constant table of numbers, or a list handed to a ported enemy helper. Identity at run
    time: mypy would join its int and float rows to `list[object]`, and the enemy helpers type
    their points as tuples where the render helpers use lists (both are JavaScript arrays)."""
    return rows


def sign_of(x: float) -> int:
    """`Math.sign(x)`: -1, 0 or 1."""
    if x > 0:
        return 1
    if x < 0:
        return -1
    return 0


def spine(p: EnemyParts, path: list[Vec3], arches: Any, glow: Rgb) -> None:
    """A spine down a back (P16-R05): a pulsing vein along `path` and, at each of `arches.at`
    (z), a rib arch `arches.halfWidth` out over it from `arches.y`, in bone."""
    vein(p.vein, path, 1.2, glow)
    ribs(
        p.flesh,
        arches.at,
        RibSpec(arches.halfWidth, arches.y, arches.height, 0.7),
        F.bone,
    )


def shell(p: EnemyParts, body: Any, color: Rgb = F.teal, place: Placement | None = None) -> None:
    """A ridged shell (P16-R01) over a back: plates of `color`, darker seams between them."""
    seam = [color[0] * 0.45, color[1] * 0.45, color[2] * 0.45]
    carapace(p.flesh, body, [color, seam], place)


def gland(p: EnemyParts, at: Vec3, radius: float, glow: Rgb) -> None:
    """A glowing gland (P16-R01) of `radius` sitting at `at`, pulsing with the veins."""
    organ(p.vein, radius, 5, glow, Placement(at), 0.6)


def sac(p: EnemyParts, at: Vec3, radius: float, color: Rgb, stretch: float = 0.7) -> None:
    """A swollen flesh sac (P16-R01) of `radius` at `at`, `stretch` times as tall."""
    organ(
        p.flesh,
        radius,
        6,
        color,
        Placement([at[0], at[1] - radius * stretch, at[2]]),
        stretch,
    )


def sinew(
    p: EnemyParts,
    ends: list[Vec3],
    bow: Vec3,
    radius: float,
    color: Rgb = F.sinew,
) -> None:
    """A sinew from `ends[0]` to `ends[1]` bowed by `bow`: a tapering flesh tendril, `radius`
    thick."""
    tendril(p.flesh, curve(ends[0], ends[1], bow, 3), [radius, radius * 0.4], 4, color)


def vein_to(
    p: EnemyParts,
    ends: list[Vec3],
    bow: Vec3,
    glow: Rgb,
    width: float = 0.9,
) -> None:
    """A vein from `ends[0]` to `ends[1]` bowed by `bow`, `width` across, pulsing (P16-R07)."""
    vein(p.vein, curve(ends[0], ends[1], bow, 3), width, glow)
