# Copyright (c) 2026 Renaud Guillon
"""MB-STONE-IDOL-01 to MB-STONE-IDOL-05, 3-3: the Stone Idol.

Logical pixels, nose +Z (the chin, down the screen), Y up (towards the camera): a carved head flying
face up, so the camera sees its face. The back of its head over the skull cut is the lid of its
crown, the moving piece of its armour (MB-STONE-IDOL-11, D-254): `stone_idol_lid.draw_lid`.
"""

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
from game.view.bosses.world_3.jungle_flesh import JUNGLE_FLESH, F, sinew, table, vein_to
from game.view.bosses.world_3.stone_idol_lid import (
    CUT_Z,
    HINGE_WIDTH,
    HINGE_Z,
    SIDE_VINE_CUT,
    SKULL,
    draw_lid,
)
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

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

from game.view.enemies.enemy_mesh import EnemyParts

type Vec3 = list[float]
# __pragma__ ("noskip")


# The head seen from above (its right half, +X): a broad face, a flat crown, a heavy chin.
HEAD_RIGHT = table([
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
])
# The whole head: the right half, then its mirror image without the two ends on the centre line.
HEAD = []
HEAD.extend(HEAD_RIGHT)
HEAD.extend(reversed_copy(flip_x(HEAD_RIGHT))[1:-1])
# The face: the head's section at the skull cut (its outline inset 2.5 px, as its bevel runs),
# ahead of the cut; the lid (`stone_idol_lid.LID`) is the rest.
FACE_BLOCK = table([
    [44.5, CUT_Z],
    [44.5, 5.8],
    [41.6, 21.1],
    [34.1, 34.4],
    [22.9, 43.7],
    [0, 47.5],
    [-22.9, 43.7],
    [-34.1, 34.4],
    [-41.6, 21.1],
    [-44.5, 5.8],
    [-44.5, CUT_Z],
])
# The nose: a rounded ridge (loft section) from between the brows to its tip over the mouth.
NOSE_SECTION = table([[1, 0], [0.65, 0.75], [0, 1], [-0.65, 0.75], [-1, 0]])
NOSE = table([
    [-8, 4, FACE - 1, 14],
    [6, 6, FACE - 1, 18],
    [16, 8, FACE - 1, 18.5],
    [20.5, 8, FACE - 1, 17],
])
# The neon cracks across the face (paths seen from above), lit from inside the stone.
CRACKS = table([
    [[30, 16], [24, 22], [26, 30], [19, 38], [21, 45]],
    [[-28, 14], [-36, 20], [-34, 30]],
])


def nose_paint(side: int, _band: int) -> Any:
    """Return the nose's paint: its +X side lit (the stone's light), the rest as its base."""
    if side == 1:
        return STONE.light
    return None


def draw_head(p: EnemyParts) -> None:
    """Draw the carved head without its lid: its block, the neon under its rim, the nose, the ears.

    The block is flattened to the skull cut behind `CUT_Z` (the lid lies there), the face rising to
    `FACE` ahead of it; the hinge's pin runs across the back of the crown.
    """
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    # MB-STONE-IDOL-02: a living head of grey-green flesh, the carved stone grown over it as armour
    # (its helmet, brows, nose and ear spools), roots of sinew trailing from its chin.
    flesh.bevel_slab(HEAD, [-10, 2, SKULL], [6, 2.5], F.sinew, None, JUNGLE_FLESH)
    flesh.bevel_slab(FACE_BLOCK, [SKULL, SKULL, FACE], [0, 2.5], F.sinew, None, JUNGLE_FLESH)
    neon_band(neon, HEAD, [-4.5, -1.5], [0.92, 0.975], IDOL_NEON)
    pin = Placement([-HINGE_WIDTH / 2, SKULL, HINGE_Z], 0, 0, -QUARTER)
    hull.cylinder(1.6, HINGE_WIDTH, 8, STONE.dark, pin)
    hull.loft(NOSE_SECTION, NOSE, STONE.base, None, LoftOptions(False, nose_paint))
    # The ear spools on the sides, lit in their bores.
    for s in SIDES:
        spool = Placement([s * 45, 1, 2], 0, 0, -s * QUARTER)
        hull.cylinder(7, 5, 8, STONE.dark, spool, 6)
        neon.ring(3, 0.8, 8, IDOL_NEON, Placement([s * 49.6, 1, 2], 0, 0, -s * QUARTER))


def draw_guns(p: EnemyParts) -> None:
    """Mark the forehead jewel's muzzle (its last-stage spiral) and draw the nostrils (its fans).

    The jewel itself is set in the lid (`stone_idol_lid.draw_jewel`).
    """
    hull = p.hull
    charge = p.charge
    muzzle = p.muzzle
    for m in IDOL_JEWEL:
        muzzle(boss_point(m[0], m[1], m[2]), "ring")
    for m in IDOL_NOSTRILS:
        nostril = boss_point(m[0], m[1], m[2])
        x = nostril[0]
        y = nostril[1]
        z = nostril[2]
        hull.cylinder(2.2, 0.8, 6, STONE.deep, Placement([x, y, z - 1.4], 0, QUARTER))
        charge.cylinder(1.6, 0.6, 6, WHITE, Placement([x, y, z - 0.6], 0, QUARTER), 1.2)
        muzzle(nostril, "gun")


def draw_roots(p: EnemyParts) -> None:
    """MB-STONE-IDOL-02: the sinew roots trailing from its chin, and the veins on its cheeks."""
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


def draw_jungle(p: EnemyParts) -> None:
    """Draw the face's cracks, moss and vine (MB-STONE-IDOL-04), its roots and its thrusters.

    The crown's growth is on the lid (`stone_idol_lid.draw_crown_growth`).
    """
    hull = p.hull
    for path in CRACKS:
        crack(p.neon, path, FACE + 0.15, IDOL_NEON)
    for patch in table([[-22, 20, 4.5], [30, 30, 3.5], [12, 42, 3]]):
        x = patch[0]
        z = patch[1]
        size = patch[2]
        moss(hull, [x, FACE, z], size, x)
    vine(hull, [[-30, FACE, 32], [-36, FACE - 2, 36], [-38, -2, 39]])
    # The side vine from the crown's lid, hanging on down the head's right side.
    vine(hull, [SIDE_VINE_CUT, [46.5, 4, -22], [48, -6, -20]])
    leaf(hull, [-40, FACE - 4, 25], 4, 3)
    draw_roots(p)
    for s in SIDES:
        reactor_sac(p, table([s * 16, -3, -48.5]), 4.5, IDOL_NEON, F.graphite, None)
        hull.cylinder(5.4, 3, 8, H.dark, Placement([s * 16, -3, -50], 0, -QUARTER))


EYE_AT = IDOL_PARTS.eye
MOUTH_AT = IDOL_PARTS.mouth


def stone_idol_core(p: EnemyParts) -> None:
    """Add the core of the Stone Idol: its head, guns (MB-STONE-IDOL-03) and carved jungle."""
    draw_head(p)
    draw_guns(p)
    draw_jungle(p)
    for s in SIDES:
        socket(p.hull, boss_point(s * EYE_AT[0], EYE_AT[1], FACE - 1), 9, 1.2)
    socket(p.hull, boss_point(MOUTH_AT[0], MOUTH_AT[1], FACE - 0.6), 8, 0.6)


def build_stone_idol(scene: Any) -> Any:
    """MB-STONE-IDOL-01, MB-STONE-IDOL-05: the Stone Idol, a flying stone head.

    With neon cracks, glowing eyes and mouth; moss and vines over its crown, an Olmec helmet, a
    jewel on its forehead. The lid of its crown flips up as it transforms (MB-STONE-IDOL-11).
    """
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
        {
            "core": stone_idol_core,
            "parts": parts,
            "turrets": turrets,
            "armour": {"crown": {"whole": draw_lid}},
        },
    )
