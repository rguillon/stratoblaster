"""P10-R11, 4-4: the Furnace Drake's parts (its beating wings and its jaw) and its forge colours.
Ported from `bosses/world-4/furnace-drake-parts.ts`. Logical pixels, nose +Z, Y up (towards the
camera).
"""

from org.transcrypt.stubs.browser import __pragma__

from game.config.boss_look import BOSS_LOOK  # noqa: E402
from game.config.bosses.boss_kit import mirror  # noqa: E402
from game.config.bosses.world_4.furnace_drake import DRAKE_MAW, DRAKE_WING_GUNS  # noqa: E402
from game.view.bosses.boss_limbs import boss_point  # noqa: E402
from game.view.bosses.final_boss_greebles import rod  # noqa: E402
from game.view.bosses.final_boss_shapes import sided  # noqa: E402
from game.view.bosses.mini_boss_greebles import lamps, seam  # noqa: E402
from game.view.bosses.mini_boss_shapes import QUARTER, SHADE, WHITE, H, offset  # noqa: E402
from game.view.bosses.world_4.living_forge import FL, SKIN, glands  # noqa: E402
from game.view.enemies.enemy_shapes import FIGHTER_SECTION, POD_SECTION, SIDES  # noqa: E402
from render.geometry.solids import Placement  # noqa: E402

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
type OutlinePoint = list[float]
__pragma__("noskip")


def _neon_or(kind: str, fallback: Rgb) -> Rgb:
    """`BOSS_LOOK.neon[kind] ?? fallback`."""
    colour: Rgb = BOSS_LOOK.neon[kind]
    if colour == None:  # noqa: E711
        return fallback
    return colour


def _sign(v: float) -> float:
    """`Math.sign`."""
    if v > 0:
        return 1
    if v < 0:
        return -1
    return 0


# The Drake's red neon, and the orange of its molten seams and flame (World 4: heat glow).
DRAKE_RED = _neon_or("furnace-drake", [1, 0.22, 0.05])
DRAKE_ORANGE = [1.0, 0.55, 0.08]
# Soot-blackened plates, and the dark, heat-stained hide of its wing membranes.
SOOT = SHADE["soot"]
HIDE = [0.08, 0.035, 0.03]


def spike(builder: Any, at: Vec3, dims: list[float], color: Rgb = H.dark, lean: float = 0) -> None:
    """A fin or spike standing on `at`: a three-sided cone `height` tall, leaning back by `lean`."""
    radius = dims[0]
    height = dims[1]
    profile = [
        [radius, 0],
        [0, height],
    ]
    builder.lathe(profile, 3, color, Placement(at, 0, -lean))


# The left wing seen from above (model +X), from its root's leading edge out and back.
WING = [
    [12.0, 8.0],
    [30.0, 15.0],
    [48.0, 12.0],
    [59.0, 2.0],
    [52.0, -7.0],
    [45.0, -3.0],
    [39.0, -15.0],
    [31.0, -9.0],
    [23.0, -19.0],
    [15.0, -11.0],
    [12.0, -6.0],
]
# The wing's bones: from the shoulder out along the leading edge, and the fingers to each scallop.
BONES = [
    [[12.0, 5.0, 6.0], [30.0, 5.6, 14.0]],
    [[30.0, 5.6, 14.0], [48.0, 5.0, 11.0]],
    [[48.0, 5.0, 11.0], [59.0, 4.6, 2.0]],
    [[30.0, 5.6, 14.0], [52.0, 4.6, -7.0]],
    [[30.0, 5.6, 14.0], [39.0, 4.6, -15.0]],
    [[24.0, 5.4, 11.0], [23.0, 4.6, -19.0]],
]
# The first bones (from the shoulder) are the thick ones.
THICK_BONES = 3
# Height of the membrane, stretched between the bones.
WING_Y = 4
# A wing's gun pod under the membrane (loft stations around the pod's centre).
NACELLE = [
    [-9.0, 2.4, -2.0, 2.0],
    [-3.0, 4.0, -2.5, 3.2],
    [5.0, 3.8, -2.0, 3.0],
    [8.0, 2.8, -1.0, 2.4],
]


def _membrane(p: Any, s: float) -> None:
    """The membrane and its bones, lit along their length by molten seams."""
    hull = p.flesh
    neon = p.neon
    # P16-R05: a membrane stretched on bone, veined molten.
    hull.bevel_slab(sided(WING, s), [WING_Y - 0.4, WING_Y, WING_Y + 0.5], [0.3, 0.3], FL.membrane)
    for i in range(len(BONES)):
        a = BONES[i][0]
        b = BONES[i][1]
        rod(
            hull,
            [s * a[0], a[1], a[2]],
            [s * b[0], b[1], b[2]],
            1.1 if i < THICK_BONES else 0.7,
            SKIN.bone,
        )
        seam(
            neon,
            [s * a[0], a[2]],
            [s * b[0], b[2]],
            [a[1] + 0.6, 0.45, 0.25],
            DRAKE_ORANGE,
        )
    # A claw at the wing's thumb, and soot along its trailing edge.
    spike(hull, [s * 30, 5.6, 14], [1.4, 5], SKIN.bone, -0.9)
    seam(hull, [s * 15, -10], [s * 38, -14], [WING_Y + 0.5, 1.6, 0.3], HIDE)


def wing(p: Any, at: Vec3) -> None:
    """A wing around its pod's centre `at` (P10-R11), drawn on its beating joint: a scalloped hide
    membrane on heavy bones, molten seams along them, and under it the gun pod with its two fan
    barrels."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    s = _sign(at[0])
    _membrane(p, s)
    hull.loft(POD_SECTION, NACELLE, H.base, Placement([at[0], -1, at[2]]))
    neon.box([0.5, 0.6, 9], DRAKE_RED, Placement([at[0] + s * 3.9, 0.6, at[2]]))
    # The left wing (screen left) is on the model's +X side.
    guns = DRAKE_WING_GUNS if s > 0 else mirror(DRAKE_WING_GUNS)
    for m in guns:
        tip = boss_point(m[0], m[1], m[2])
        x = tip[0]
        y = tip[1]
        z = tip[2]
        hull.cylinder(1, 6.4, 6, H.dark, Placement([x, y, z - 7], 0, QUARTER))
        charge.cylinder(1.05, 0.6, 6, WHITE, Placement([x, y, z - 0.6], 0, QUARTER))
        muzzle(tip)


# The neck, shoulders to skull (loft stations, model space).
NECK = [
    [15.0, 6.5, -1.0, 7.5],
    [22.0, 5.0, -0.5, 6.8],
    [29.0, 5.2, 0.0, 7.0],
]
# The skull and its upper jaw, ending in a blunt snout over the maw.
SKULL = [
    [27.0, 7.0, 1.0, 8.5],
    [35.0, 8.0, 2.0, 9.0],
    [43.0, 6.5, 4.6, 8.0],
    [50.0, 4.2, 4.6, 6.8],
    [55.0, 2.6, 4.6, 5.8],
]
# The left half of the lower jaw (model +X), hinged under the skull, open outwards.
LOWER_JAW = [
    [1.0, 34.0],
    [7.0, 34.0],
    [6.5, 46.0],
    [4.5, 55.0],
    [2.5, 55.0],
    [1.0, 44.0],
]


def _skull(p: Any) -> None:
    """The skull: horns swept back, red eyes, the open lower jaw with its teeth."""
    flesh = p.flesh
    neon = p.neon
    flesh.loft(FIGHTER_SECTION, SKULL, SKIN.base)
    for s in SIDES:
        rod(flesh, [s * 4.5, 8.4, 33], [s * 7, 12.5, 27], 1.2, SKIN.bone)
        rod(flesh, [s * 7, 12.5, 27], [s * 8, 13.4, 23.5], 0.6, SKIN.bone)
        lamps(neon, [[s * 4.6, 8.4, 41]], 1.6, DRAKE_RED)
        glands(p, [[s * 4.6, 8.6, 38]], 1, DRAKE_ORANGE)
        p.hull.bevel_slab(sided(LOWER_JAW, s), [0.4, 1.4, 2.8], [0.3, 0.3], H.panel)
        for z in [42, 47, 52]:
            spike(flesh, [s * 4.5, 2.8, z], [0.6, 1.8], SKIN.bone)
    seam(neon, [0, 30], [0, 48], [8.9, 0.5, 0.3], DRAKE_ORANGE)


def jaw(p: Any, at: Vec3) -> None:
    """The drake's jaw around the head's centre `at` (P10-R11), on its swaying neck: the neck and
    skull, the open maw glowing as the flame charges, and the flame nozzle in its throat."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    p.flesh.loft(POD_SECTION, NECK, SKIN.panel)
    for s in SIDES:
        seam(neon, [s * 5.2, 17], [s * 5, 28], [3.4, 0.4, 0.4], DRAKE_ORANGE)
    for z in [18, 24]:
        spike(p.flesh, [0, 7, z], [1.2, 3.4], SKIN.bone, 0.6)
    _skull(p)
    if len(DRAKE_MAW) == 0:
        return
    m = DRAKE_MAW[0]
    tip = boss_point(m[0], m[1], m[2])
    x = tip[0]
    y = tip[1]
    z = tip[2]
    charge.box([5, 1.2, 12], WHITE, Placement(offset(at, 0, 1.6, 8)))
    hull.cylinder(1.3, 9, 6, H.dark, Placement([x, y, z - 9.6], 0, QUARTER), 1.1)
    charge.cylinder(1.15, 0.6, 6, WHITE, Placement([x, y, z - 0.6], 0, QUARTER))
    muzzle(tip)
