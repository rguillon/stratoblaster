"""P10-R11, 4-5: the Ember Herald's colours, its ember lances (the parts on its turning ring), the
spikes on its hull and the embers drifting round it. Ported from
`bosses/world-4/ember-herald-parts.ts`. Logical pixels, nose +Z, Y up.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.math.rng import create_rng  # noqa: E402
from game.config.boss_look import BOSS_LOOK  # noqa: E402
from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.bosses.mini_boss_shapes import QUARTER, SHADE, WHITE, H  # noqa: E402
from game.view.bosses.world_4.living_forge import SKIN  # noqa: E402
from render.geometry.outline import hypot2  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
__pragma__("noskip")


def _neon_or(kind: str, fallback: Rgb) -> Rgb:
    """`BOSS_LOOK.neon[kind] ?? fallback`."""
    colour: Rgb = BOSS_LOOK.neon[kind]
    if colour == None:  # noqa: E711
        return fallback
    return colour


# Gold: the Ember Herald's registered neon (GD-61).
GOLD = _neon_or("ember-herald", [1, 1, 1])
# World 4 heat (P10-R11): molten seams, glowing embers, soot-black and heat-blued metal.
HEAT = {
    "molten": [1, 0.38, 0.05],
    "ember": [1, 0.6, 0.14],
    "soot": SHADE["soot"],
    "blued": [0.1, 0.09, 0.13],
}

# A lance's shaft along its axis (lathe profile: radius, distance from its inner end).
SHAFT = [
    [3.0, 0.0],
    [4.4, 2.0],
    [4.4, 6.0],
    [2.8, 8.0],
    [2.6, 21.0],
    [3.6, 23.0],
]
# Its glowing blade, from the end of the shaft out to the charge light at its tip.
BLADE = [
    [3.6, 23.0],
    [5.0, 26.5],
    [0.0, 35.0],
]
LANCE_LENGTH = BLADE[len(BLADE) - 1][1]
# The lance's charge light at its tip (lathe profile), where its spiral leaves from.
LANCE_TIP = [
    [1.4, 0.0],
    [0.0, 2.0],
]
# How far the lance's barbs stand along it, and their length.
BARBS = [
    [25.0, 7.0],
    [13.0, 5.0],
]
# A spike (lathe profile, in units of its radius and length).
SPIKE = [
    [1.0, 0.0],
    [0.45, 0.55],
    [0.0, 1.0],
]


def spike(parts: Any, at: Vec3, angles: list[float], dims: list[float]) -> None:
    """A spike of `[radius, length]` growing from `at`, tilted by `[pitch, roll, yaw]` from straight
    up: bone, a molten glow at its root."""
    place = Placement(at, angles[2], angles[0], angles[1])
    radius = dims[0]
    length = dims[1]
    # P16-R05: a bone spike, a molten glow at its root.
    parts.flesh.lathe(
        [[r[0] * radius, r[1] * length] for r in SPIKE],
        4,
        SKIN.bone,
        place,
    )
    parts.neon.ring(radius * 1.05, length * 0.1, 4, HEAT["molten"], place)


def ember_lance(p: Any, muzzles: list[Any], at: Vec3) -> None:
    """An ember lance on the turning ring, pointing out of it to its `muzzles`' tip (from the
    design): a soot-black shaft with molten bands and a gold collar, a glowing gold blade, two pairs
    of barbs, a clamp holding it to the ring, and a charge light at its tip where its spirals
    leave."""
    if len(muzzles) == 0:
        return
    m = muzzles[0]
    tip = boss_point(m[0], m[1], m[2])
    reach = hypot2(tip[0], tip[2])
    yaw = math.atan2(tip[0], tip[2])

    def out(r: float, up: float = 0) -> Vec3:
        """A point `r` px in from the tip along the lance, `up` above its axis."""
        return [math.sin(yaw) * (reach - r), tip[1] + up, math.cos(yaw) * (reach - r)]

    def axis(r: float) -> Any:
        return Placement(out(r), yaw, QUARTER)

    inner = LANCE_LENGTH + LANCE_TIP[1][1]
    p.flesh.lathe(SHAFT, 6, SKIN.panel, axis(inner))
    p.neon.lathe(BLADE, 6, GOLD, axis(inner), False)
    p.charge.lathe(LANCE_TIP, 6, WHITE, axis(LANCE_TIP[1][1]))
    p.muzzle(tip)
    p.neon.ring(4.5, 1.8, 6, GOLD, axis(inner - 3))
    for r in [inner - 10, inner - 16]:
        p.neon.ring(2.75, 1.2, 6, HEAT["molten"], axis(r))
    for barb in BARBS:
        along = barb[0]
        size = barb[1]
        for s in [-1, 1]:
            root = out(inner - along)
            spike(p, root, [QUARTER - 0.3, 0, yaw + math.pi + s * 0.7], [1.5, size])
    clamp = out(reach - hypot2(at[0], at[2]), -4.5)
    p.hull.box([6, 3, 5], SHADE["edge"], Placement(clamp, yaw), H.panel)


# The embers wreathing it: how many, how far out, and how high they drift.
EMBERS_COUNT = 26
EMBERS_INNER = 18
EMBERS_OUTER = 62
EMBERS_LOW = 4
EMBERS_HIGH = 26
EMBERS_SIZE = [0.7, 1.5]

# The embers' colours, in turn.
EMBER_COLOURS = [GOLD, HEAT["ember"], HEAT["molten"]]


def embers(neon: Any) -> None:
    """The embers wreathing the Ember Herald (P10-R11): small glowing motes scattered round the hull
    and up past its ring, some molten orange, some bright gold, the same every time."""
    random = create_rng(4505)
    for i in range(EMBERS_COUNT):
        a = random() * math.pi * 2
        r = EMBERS_INNER + (EMBERS_OUTER - EMBERS_INNER) * math.sqrt(random())
        s = EMBERS_SIZE[0] + (EMBERS_SIZE[1] - EMBERS_SIZE[0]) * random()
        y = EMBERS_LOW + (EMBERS_HIGH - EMBERS_LOW) * random()
        at = [math.sin(a) * r, y, math.cos(a) * r]
        neon.box([s, s, s], EMBER_COLOURS[i % len(EMBER_COLOURS)], Placement(at, a, 0.6))
