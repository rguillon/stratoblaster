"""P09-R09, 3-2: the Toucan. Ported from `view/bosses/world-3/toucan-model.ts`. Logical pixels,
nose +Z, Y up (towards the camera). A stubby gunship: a round black body, short wings carrying the
fan pods, a fanned tail, and the huge bright beak (its cannon, a part) in front of its head."""

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.world_3.toucan import TOUCAN, TOUCAN_CHEEK_GUNS, TOUCAN_CREST
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.final_boss_shapes import (
    mirrored,
    strip,
)
from game.view.bosses.mini_boss_greebles import seam, vent
from game.view.bosses.mini_boss_shapes import (
    QUARTER,
    SHADE,
    WHITE,
    H,
    offset,
    socket,
)
from game.view.bosses.world_3.jungle_flesh import F, sinew, spine, table
from game.view.bosses.world_3.toucan_jungle import moss, sagging, vine
from game.view.bosses.world_3.toucan_parts import (
    TOUCAN_ORANGE,
    TOUCAN_YELLOW,
    beak,
    wing_pod,
)
from game.view.enemies.enemy_shapes import SIDES
from game.view.enemies.organic_parts import reactor_sac
from render.geometry.organic import ROUND_SECTION
from render.geometry.solids import LoftOptions, Placement

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

from game.view.enemies.enemy_mesh import EnemyParts  # noqa: E402

type Rgb = list[float]
type Vec3 = list[float]
__pragma__("noskip")

# The body along the centre line, tail to head (loft stations: z, half width, bottom, top).
BODY = table(
    [
        [-36, 5, 0, 5],
        [-26, 11, -2, 9.5],
        [-10, 16, -4, 13],
        [6, 17, -4, 15],
        [15, 14.5, -3, 14.2],
        [21, 10.6, -1.5, 12.6],
    ]
)
# The cream bib under its head (the lower sides of the body's last bands).
BIB = [0.7, 0.64, 0.42]
BIB_SIDES = [0, 1, 7, 8]
# The wings seen from above (right half, front to back), the pods at their ends.
WINGS = mirrored(
    [
        [0, 13],
        [14, 12],
        [26, 9],
        [30, 4],
        [30, -9],
        [24, -15],
        [12, -17],
        [0, -17],
    ]
)
# The tail's fan of feathers seen from above (right half, from the body back).
TAIL = mirrored([[0, -30], [8, -32], [11, -45], [5, -48], [0, -44]])


def body_paint(side: int, band: int) -> Any:
    """The body's paint: the bib on the lower sides of its last band."""
    if band == 4 and side in BIB_SIDES:  # noqa: PLR2004 (the last band of BODY)
        return BIB
    return None


def draw_body(p: EnemyParts) -> None:
    """The body: black plates, a cream bib, orange neon along its flanks, moss on its back."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    # P16-R05: a round, living bird's body of dark purple flesh, a bone ribcage over its back.
    flesh.loft(
        ROUND_SECTION,
        BODY,
        F.purple,
        None,
        LoftOptions(False, body_paint),
    )
    path: list[Vec3] = []
    for st in BODY[1:]:
        path.append([0, st[3] + 0.3, st[0]])
    spine(
        p,
        path,
        {"at": [-20, -12, -4], "halfWidth": 13, "y": 2, "height": 11.8},
        TOUCAN_ORANGE,
    )
    for s in SIDES:
        strip(neon, [s * 15.6, 4], [s * 12, -20], 0.8, [3.6, 4.4], TOUCAN_ORANGE)
        seam(hull, [s * 6, 10], [s * 7, -22], [12.4, 0.8, 0.5], H.dark)
        vent(hull, [s * 9, 11.4, -14], [3.2, 6], 3, s * 0.12)
    moss(hull, [5, 14.2, -4], 4.2, 0.7)
    moss(hull, [-7, 12.2, -19], 3.4, 2.1)


def draw_wings_and_tail(p: EnemyParts) -> None:
    """The wings and the tail: dark, bevelled, neon on their edges, vines hanging from them."""
    hull = p.hull
    flesh = p.flesh
    neon = p.neon
    # P16-R05: short, heavy membrane wings (still, P16-R01) on bone struts, a fan of bone quills.
    flesh.bevel_slab(WINGS, [-1.5, 0, 2], [0.8, 1], F.membrane, None, F.purple)
    flesh.bevel_slab(TAIL, [0.5, 1.5, 3], [0.4, 0.8], F.membrane, None, F.crimson)
    for s in SIDES:
        for strut_end in [[30, 4], [30, -9], [24, -15]]:
            sinew(
                p,
                [[s * 4, 2.4, 0], [s * strut_end[0], 2.2, strut_end[1]]],
                [0, 0.6, 0],
                1,
                F.bone,
            )
        sinew(
            p,
            [[s * 2, 3.2, -30], [s * 10, 3.2, -45]],
            [0, 0.3, 0],
            0.7,
            F.bone,
        )
    for s in SIDES:
        strip(neon, [s * 14, 12.2], [s * 25.5, 9.4], 0.8, [1.9, 2.3], TOUCAN_YELLOW)
        strip(neon, [s * 8.5, -33], [s * 10.6, -44.5], 0.7, [2.9, 3.3], TOUCAN_ORANGE)
        seam(hull, [s * 18, 8], [s * 22, -14], [2, 0.6, 0.4], H.dark)
        vine(hull, sagging([s * 12, -0.5, -16.5], [s * 26, -0.5, -14.5], 5, 3.5))
        moss(hull, [s * 20, 2, -4], 3, s)
        reactor_sac(p, table([s * 4.5, 3, -36.2]), 2.8, table(TOUCAN_ORANGE), None, None)


def draw_head(p: EnemyParts) -> None:
    """The head: its round neon eyes either side, the cheek guns under them, the crest emitter."""
    hull = p.hull
    neon = p.neon
    charge = p.charge
    muzzle = p.muzzle
    for s in SIDES:
        eye: Vec3 = [s * 12.4, 8.6, 15]
        hull.cylinder(3.2, 0.8, 8, H.dark, Placement(eye, 0, 0, -s * QUARTER))
        neon.ring(
            3.3,
            0.9,
            8,
            TOUCAN_YELLOW,
            Placement(offset(eye, s * 0.4, 0, 0), 0, 0, -s * QUARTER),
        )
        charge.cylinder(
            1.5,
            0.5,
            8,
            WHITE,
            Placement(offset(eye, s * 0.6, 0, 0), 0, 0, -s * QUARTER),
        )
    for m in TOUCAN_CHEEK_GUNS:
        tip = boss_point(m[0], m[1], m[2])
        x = tip[0]
        y = tip[1]
        z = tip[2]
        hull.box([4.4, 4, 7], H.panel, Placement([x, y - 2.4, z - 10]), H.base)
        hull.cylinder(1.2, 6.4, 6, H.dark, Placement([x, y, z - 7], 0, QUARTER))
        charge.cylinder(1.25, 0.6, 6, WHITE, Placement([x, y, z - 0.6], 0, QUARTER))
        muzzle(tip)
    if len(TOUCAN_CREST) == 0:
        return
    crest = boss_point(TOUCAN_CREST[0][0], TOUCAN_CREST[0][1], TOUCAN_CREST[0][2])
    socket(hull, offset(crest, 0, -3.4, 0), 3.4, 1.6)
    neon.ring(3.5, 0.5, 8, TOUCAN_ORANGE, Placement(offset(crest, 0, -2.2, 0)))
    hull.cylinder(2.2, 1.2, 8, H.panel, Placement(offset(crest, 0, -1.8, 0)), 1.8)
    charge.cylinder(1.6, 0.6, 8, WHITE, Placement(offset(crest, 0, -0.6, 0)))
    muzzle(crest, "ring")
    hull.box(
        [2.6, 2.4, 7],
        SHADE["edge"],
        Placement(offset(crest, 0, -2.6, -7), 0, -0.25),
    )


def toucan_core(p: EnemyParts) -> None:
    """The core of the Toucan: its body, wings, tail and head."""
    draw_body(p)
    draw_wings_and_tail(p)
    draw_head(p)


def build_toucan(scene: Any) -> Any:
    """P09-R09: the Toucan, a stubby gunship with a huge bright beak, yellow and orange neon, moss
    on its back and vines hanging from its wings."""
    parts: dict[str, Any] = {
        "pod-left": wing_pod,
        "pod-right": wing_pod,
        "beak": beak,
    }
    return build_boss_model(
        TOUCAN,
        scene,
        TOUCAN_YELLOW,
        {"core": toucan_core, "parts": parts},
    )
