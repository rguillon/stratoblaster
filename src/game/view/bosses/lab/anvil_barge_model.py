# Copyright (c) 2026 Renaud Guillon
"""MB-ANVIL-BARGE-01, MB-ANVIL-BARGE-02: the Anvil Barge, the Lab's L-21 mini boss.

Logical pixels, nose +Z, Y up (towards the camera). A flying iron bunker shaped like an anvil, seen
from above: the flat working face of hardened steel plates with glowing seams between them, the
step in front of it, the horn (two halves, `anvil_barge_parts`), the heel overhanging its back, the
heavy waisted base under them and its flared feet. Under the horn a forge throat glows, shown once
the horn splits; rams push the halves apart (`anvil_barge_rig`). A machine, not a creature (the
Lab's fifth round, user request 2026-11-06).
"""

from game.config.bosses.lab.anvil_barge import (
    ANVIL_BARGE,
    CANNON_AT,
    CASEMATE_AT,
    FACE_BACK,
    FACE_FRONT,
    FACE_HALF,
    FACE_TOP,
    FACE_UNDER,
    FEET,
    FORGE_AT,
    HEEL_BACK,
    HEEL_HALF,
    HORN_ROOT_HALF,
    HORN_TIP,
    STEP_FRONT,
    STEP_HALF,
    STEP_TOP,
    WAIST,
)
from game.view.bosses.boss_limbs import boss_point
from game.view.bosses.boss_model import build_boss_model
from game.view.bosses.lab.anvil_barge_parts import (
    BAND,
    IRON,
    STEEL,
    N,
    barge_armour,
    forge,
    jets,
    outline_of,
    rivets,
    seam,
)
from game.view.bosses.lab.anvil_barge_rig import build_barge_rig, rig_triangles
from game.view.bosses.world_1_organic_kit import M
from render.geometry.solids import Placement

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# The face's hardened plates: the Y where each ends, from front to back (seams between them).
PLATE_YS = [FACE_FRONT, -14, 3, FACE_BACK]
# The throat under the horn: its outline (config), its floor and its lit channel's top.
THROAT = [  # type: list[list[float]]
    [-10, STEP_FRONT + 1],
    [10, STEP_FRONT + 1],
    [8, -56],
    [0, HORN_TIP + 3],
    [-8, -56],
]
THROAT_FLOOR = [1, 5]


def _chamfered(half: float, front: float, back: float, cut: float) -> list[list[float]]:
    """Return a rectangle's outline (config) `half` either side, `front` to `back`, corners cut."""
    return [
        [-half + cut, front],
        [half - cut, front],
        [half, front + cut],
        [half, back - cut],
        [half - cut, back],
        [-half + cut, back],
        [-half, back - cut],
        [-half, front + cut],
    ]


def _draw_base(p: Any) -> None:
    """Draw the heavy base (MB-ANVIL-BARGE-02): flared feet, a waist, riveted bands, lit seams."""
    feet = _chamfered(FEET[0], FEET[1], FEET[2], 7)
    p.hull.bevel_slab(outline_of(feet), [FEET[3], FEET[4] - 3, FEET[4]], [3.5, 1], IRON, None, BAND)
    waist = _chamfered(WAIST[0], WAIST[1], WAIST[2], 4)
    p.hull.bevel_slab(outline_of(waist), [WAIST[3], WAIST[3] + 2, WAIST[4]], [-4, 0], IRON)
    # Riveted rims round the feet's top, a lit seam on their slope.
    h = FEET[4]
    rivets(p, [-FEET[0] + 8, FEET[1] + 1.5], [FEET[0] - 8, FEET[1] + 1.5], 8, h)
    rivets(p, [-FEET[0] + 8, FEET[2] - 1.5], [FEET[0] - 8, FEET[2] - 1.5], 8, h)
    for s in [-1, 1]:
        seam(p, [s * (FEET[0] - 0.4), FEET[1] + 9], [s * (FEET[0] - 0.4), FEET[2] - 9], h - 1.6)
        seam(p, [s * 13, FEET[1] + 0.3], [s * 22, FEET[1] + 0.3], h - 1.4)
        # Mooring bollards on the feet's back corners.
        q = boss_point(s * 22, FEET[2] - 4, h)
        p.hull.cylinder(1.6, 2.6, 6, M.panel, Placement(q), 1.2)
        p.neon.box([0.8, 0.8, 0.8], N, Placement([q[0], h + 2.6, q[2]]))


def _draw_body(p: Any) -> None:
    """Draw the anvil's body (MB-ANVIL-BARGE-02): the face, the step, the heel, their plating.

    The working face is hardened steel in three plates, glowing seams between them and along its
    edges, rivets on their rims; seats for the fixed cannons in its front; the forge turret's
    pedestal on the heel.
    """
    face = _chamfered(FACE_HALF, FACE_FRONT, FACE_BACK, 2)
    p.hull.bevel_slab(outline_of(face), [FACE_UNDER, FACE_TOP - 2.5, FACE_TOP], [-1.5, 1.4], IRON)
    heel = _chamfered(HEEL_HALF, FACE_BACK - 2, HEEL_BACK, 3)
    p.hull.bevel_slab(outline_of(heel), [FACE_UNDER + 3, FACE_TOP - 2, FACE_TOP], [1.5, 1.2], IRON)
    step = _chamfered(STEP_HALF, STEP_FRONT, FACE_FRONT + 1, 1.5)
    p.hull.bevel_slab(outline_of(step), [FACE_UNDER - 4, STEP_TOP - 1.5, STEP_TOP], [0, 1], IRON)
    # The hardened plates on the face, a glowing seam between each two.
    for k in range(len(PLATE_YS) - 1):
        y0 = PLATE_YS[k] + 1.6
        y1 = PLATE_YS[k + 1] - 1.6
        plate = [[-FACE_HALF + 1.6, y0], [FACE_HALF - 1.6, y0], [FACE_HALF - 1.6, y1]]
        plate.append([-FACE_HALF + 1.6, y1])
        p.hull.slab(outline_of(plate), [FACE_TOP - 0.2, FACE_TOP + 0.6], STEEL)
        rivets(p, [-FACE_HALF + 2.6, y0 + 1], [FACE_HALF - 2.6, y0 + 1], 8, FACE_TOP + 0.6)
        if k > 0:
            seam(
                p, [-FACE_HALF + 1, PLATE_YS[k]], [FACE_HALF - 1, PLATE_YS[k]], FACE_TOP + 0.1, 0.9
            )
    for s in [-1, 1]:
        seam(p, [s * (FACE_HALF + 0.1), FACE_FRONT + 3], [s * (FACE_HALF + 0.1), FACE_BACK - 3], 17)
        seam(p, [s * (HEEL_HALF + 0.1), FACE_BACK + 1], [s * (HEEL_HALF + 0.1), HEEL_BACK - 2], 18)
        # The fixed cannons' seats: an iron cradle under each (MB-ANVIL-BARGE-07).
        c = boss_point(s * CANNON_AT[0], CANNON_AT[1], FACE_TOP + 0.4)
        p.hull.box([7, 1, 6.5], BAND, Placement(c))
        p.neon.box([7.2, 0.3, 0.4], N, Placement([c[0], FACE_TOP + 1.4, c[2] - 3.1]))
        # The casemates' lips on the face's flanks.
        q = boss_point(s * (CASEMATE_AT[0] + 3.6), CASEMATE_AT[1], FACE_TOP - 4)
        p.hull.box([2, 4, 11], BAND, Placement(q))
    # The heel's back: a lit vent band; the forge turret's pedestal (it stays, under its stump).
    p.neon.box([2 * HEEL_HALF - 6, 1, 0.4], N, Placement([0, FACE_TOP - 3.5, -HEEL_BACK - 0.05]))
    f = boss_point(FORGE_AT[0], FORGE_AT[1], FACE_TOP)
    p.hull.cylinder(4.6, 4.9, 8, BAND, Placement(f))


def _draw_throat(p: Any) -> None:
    """Draw the forge throat under the horn (MB-ANVIL-BARGE-05): shown once the horn splits.

    A dark channel, a lit molten groove along its middle, iron ribs across it, the rams' seats.
    """
    p.hull.slab(outline_of(THROAT), THROAT_FLOOR, BAND)
    groove = [[-1.6, STEP_FRONT], [1.6, STEP_FRONT], [1, HORN_TIP + 6], [-1, HORN_TIP + 6]]
    p.neon.slab(outline_of(groove), [THROAT_FLOOR[1], THROAT_FLOOR[1] + 0.3], N)
    for y in [-38, -45, -52]:
        q = boss_point(0, y, THROAT_FLOOR[1])
        p.bare.box([15 - (-y - 38) * 0.4, 0.8, 1], M.base, Placement(q))
    # Its sides rise to the step: a dark wall the horn's root closes on.
    wall = [[-HORN_ROOT_HALF, STEP_FRONT - 0.5], [HORN_ROOT_HALF, STEP_FRONT - 0.5]]
    wall.append([HORN_ROOT_HALF, STEP_FRONT + 1.5])
    wall.append([-HORN_ROOT_HALF, STEP_FRONT + 1.5])
    p.hull.slab(outline_of(wall), [THROAT_FLOOR[0], STEP_TOP - 1], BAND)


def build_anvil_barge(scene: Any) -> Any:
    """MB-ANVIL-BARGE-01, MB-ANVIL-BARGE-02: the Anvil Barge.

    Blackened iron and hardened steel, ember light lines (shown yellow) in its seams.
    """

    def core(p: Any) -> None:
        _draw_base(p)
        _draw_body(p)
        _draw_throat(p)

    return build_boss_model(
        ANVIL_BARGE,
        scene,
        N,
        {
            "core": core,
            "parts": {"jets-left": jets, "jets-right": jets, "forge": forge},
            "armour": barge_armour(),
            "rig": {"build": build_barge_rig, "triangles": rig_triangles},
        },
    )
