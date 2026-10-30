"""P09-R09, 3-3: the Stone Idol. Logical
pixels, nose +Z (the chin, down the screen), Y up (towards the camera): a carved head flying face
up, so the camera sees its face."""

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.world_3.stone_idol import (
    IDOL_JEWEL,
    IDOL_NOSTRILS,
    IDOL_PARTS,
    STONE_IDOL,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.mini_boss_shapes import (
    QUARTER,
    WHITE,
    H,
    neon_band,
    socket,
)
from game.view.bosses.world_3.jungle_flesh import JUNGLE_FLESH, F, gland, sinew, table, vein_to
from game.view.bosses.world_3.stone_idol_parts import (
    FACE,
    IDOL_NEON,
    eye_socket,
    eyeball,
    mouth,
)
from game.view.bosses.world_3.stone_idol_stone import STONE, crack, leaf, moss, vine
from game.view.enemies.enemy_shapes import SIDES, flip_x
from game.view.enemies.organic_parts import reactor_sac
from render.geometry.outline import reversed_copy
from render.geometry.solids import LoftOptions, Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402

type Vec3 = list[float]
__pragma__("noskip")

# The head seen from above (its right half, +X): a broad face, a flat crown, a heavy chin.
HEAD_RIGHT = table(
    [
        [0, 50],
        [24, 46],
        [36, 36],
        [44, 22],
        [47, 6],
        [47, -12],
        [44, -30],
        [36, -42],
        [22, -48],
        [0, -50],
    ]
)
# The whole head: the right half, then its mirror image without the two ends on the centre line.
HEAD = []
HEAD.extend(HEAD_RIGHT)
HEAD.extend(reversed_copy(flip_x(HEAD_RIGHT))[1:-1])
# The helmet over the forehead (an Olmec headdress), outline seen from above.
HELMET = table(
    [
        [0, -47],
        [23, -45],
        [35, -38],
        [42, -26],
        [41, -18],
        [0, -21],
        [-41, -18],
        [-42, -26],
        [-35, -38],
        [-23, -45],
    ]
)
# The nose: a rounded ridge (loft section) from between the brows to its tip over the mouth.
NOSE_SECTION = table([[1, 0], [0.65, 0.75], [0, 1], [-0.65, 0.75], [-1, 0]])
NOSE = table(
    [
        [-8, 4, FACE - 1, 14],
        [6, 6, FACE - 1, 18],
        [16, 8, FACE - 1, 18.5],
        [20.5, 8, FACE - 1, 17],
    ]
)
# The neon cracks across the face (paths seen from above), lit from inside the stone.
CRACKS = table(
    [
        [[-14, -46], [-10, -36], [-15, -28], [-12, -20]],
        [[30, 16], [24, 22], [26, 30], [19, 38], [21, 45]],
        [[-28, 14], [-36, 20], [-34, 30]],
        [[8, -16], [14, -6]],
    ]
)


def nose_paint(side: int, band: int) -> Any:
    """The nose's paint: its +X side lit (the stone's light), the rest as its base."""
    if side == 1:
        return STONE.light
    return None


def draw_head(p: EnemyParts) -> None:
    """The carved head: its block, the neon glowing under its rim, the helmet and the brows."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    # P16-R05: a living head of grey-green flesh, the carved stone grown over it as armour (its
    # helmet, brows, nose and ear spools), roots of sinew trailing from its chin.
    flesh.bevel_slab(HEAD, [-10, 2, FACE], [6, 5], F.sinew, None, JUNGLE_FLESH)
    neon_band(neon, HEAD, [-4.5, -1.5], [0.92, 0.975], IDOL_NEON)
    hull.bevel_slab(HELMET, [FACE - 1, FACE + 2, FACE + 5], [0, 1.5], STONE.base, None, STONE.light)
    neon.box([60, 0.6, 0.6], IDOL_NEON, Placement([0, FACE + 3.2, -19.6], 0))
    # The brow ridge over the eyes, broken on the left (the model's +X).
    hull.box([30, 3.5, 6], STONE.base, Placement([-19, FACE - 0.5, -10]), STONE.light)
    hull.box([22, 3, 6], STONE.base, Placement([21, FACE - 0.5, -10], 0.08), STONE.light)
    hull.box([5, 2.4, 4], STONE.dark, Placement([36, FACE - 0.5, -12], 0.6), STONE.base)
    hull.loft(NOSE_SECTION, NOSE, STONE.base, None, LoftOptions(False, nose_paint))
    # The ear spools on the sides, lit in their bores.
    for s in SIDES:
        spool = Placement([s * 45, 1, 2], 0, 0, -s * QUARTER)
        hull.cylinder(7, 5, 8, STONE.dark, spool, 6)
        neon.ring(3, 0.8, 8, IDOL_NEON, Placement([s * 49.6, 1, 2], 0, 0, -s * QUARTER))


def draw_guns(p: EnemyParts) -> None:
    """The forehead jewel (its last-stage spiral) and the nostrils (its fans), charge-lit."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    for m in IDOL_JEWEL:
        jewel = boss_point(m[0], m[1], m[2])
        x = jewel[0]
        y = jewel[1]
        z = jewel[2]
        hull.cylinder(4.2, 1.2, 8, STONE.gilt, Placement([x, FACE + 5, z]), 3.6)
        neon.ring(4.3, 0.5, 8, IDOL_NEON, Placement([x, FACE + 5.6, z]))
        gem = [[3, FACE + 6.2], [3.4, y - 1.6], [0, y]]
        charge.lathe(gem, 6, WHITE, Placement([x, 0, z]))
        muzzle(jewel, "ring")
    for m in IDOL_NOSTRILS:
        nostril = boss_point(m[0], m[1], m[2])
        x = nostril[0]
        y = nostril[1]
        z = nostril[2]
        hull.cylinder(2.2, 0.8, 6, STONE.deep, Placement([x, y, z - 1.4], 0, QUARTER))
        charge.cylinder(1.6, 0.6, 6, WHITE, Placement([x, y, z - 0.6], 0, QUARTER), 1.2)
        muzzle(nostril, "gun")


def draw_roots(p: EnemyParts) -> None:
    """P16-R05: the sinew roots trailing from its chin, its veins and glands."""
    for root in [[-16, -3], [14, 4], [28, 2]]:
        x = root[0]
        bow = root[1]
        sinew(
            p,
            [[x, 2, 44], [x + bow, -4, 53]],
            [bow, -2, 0],
            2,
            F.sinew,
        )
    for s in SIDES:
        vein_to(
            p,
            [[s * 8, FACE + 0.3, 26], [s * 34, FACE + 0.3, 30]],
            [0, 0, 6],
            IDOL_NEON,
            1.2,
        )
        gland(p, [s * 38, FACE - 0.5, -32], 3, IDOL_NEON)


def draw_jungle(p: EnemyParts) -> None:
    """Its cracks, the moss in its hollows, the vines over its crown, and the thrusters it flies
    on."""
    hull = p.hull
    neon = p.neon
    for path in CRACKS:
        crack(neon, path, FACE + 0.15, IDOL_NEON)
    crack(neon, [[-24, -40], [-30, -33], [-27, -27]], FACE + 5.1, IDOL_NEON)
    for patch in table([[-22, 20, 4.5], [30, 30, 3.5], [12, 42, 3], [-38, -6, 3.5], [24, -40, 4]]):
        x = patch[0]
        z = patch[1]
        size = patch[2]
        moss(hull, [x, FACE + 5 if z < -20 else FACE, z], size, x)  # noqa: PLR2004 (the TS cut-off of -20)
    vine(
        hull,
        [
            [18, FACE + 5, -40],
            [30, FACE + 4.6, -34],
            [40, FACE, -26],
            [46.5, 4, -22],
            [48, -6, -20],
        ],
    )
    vine(
        hull,
        [[-10, FACE + 5, -44], [-14, FACE + 2, -49], [-15, -2, -51], [-13, -8, -50]],
    )
    vine(hull, [[-30, FACE, 32], [-36, FACE - 2, 36], [-38, -2, 39]])
    leaf(hull, [-40, FACE - 4, 25], 4, 3)
    draw_roots(p)
    for s in SIDES:
        reactor_sac(p, table([s * 16, -3, -48.5]), 4.5, IDOL_NEON, F.purple, None)
        hull.cylinder(5.4, 3, 8, H.dark, Placement([s * 16, -3, -50], 0, -QUARTER))


EYE_AT = IDOL_PARTS.eye
MOUTH_AT = IDOL_PARTS.mouth


def stone_idol_core(p: EnemyParts) -> None:
    """The core of the Stone Idol: its head, guns and carved jungle."""
    draw_head(p)
    draw_guns(p)
    draw_jungle(p)
    for s in SIDES:
        socket(p.hull, boss_point(s * EYE_AT[0], EYE_AT[1], FACE - 1), 9, 1.2)
    socket(p.hull, boss_point(MOUTH_AT[0], MOUTH_AT[1], FACE - 0.6), 8, 0.6)


def build_stone_idol(scene: Any) -> Any:
    """P09-R09: the Stone Idol, a flying stone head with neon cracks, glowing eyes and mouth; moss
    and vines over its crown, an Olmec helmet, a jewel on its forehead."""
    parts: dict[str, Any] = {
        "eye-left": eye_socket,
        "eye-right": eye_socket,
        "mouth": mouth,
    }
    turrets: dict[str, Any] = {"eye-left": eyeball, "eye-right": eyeball}
    return build_boss_model(
        STONE_IDOL,
        scene,
        IDOL_NEON,
        {"core": stone_idol_core, "parts": parts, "turrets": turrets},
    )
