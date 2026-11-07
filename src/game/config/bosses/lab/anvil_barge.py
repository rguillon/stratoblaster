# Copyright (c) 2026 Renaud Guillon
"""The Anvil Barge, the Lab's L-21 mini boss (specs/bosses/lab/L-21-anvil-barge.md).

Lab boss: in the dev viewer only, no level brings it in. A gigantic flying iron bunker shaped like
an anvil, seen from above: a horn at its front, a step, a flat working face, a heel overhanging its
back, all on a heavy waisted base whose feet flare out under it, held up by a bank of downward lift
jets along each foot. Riveted plate, glowing seams. It comes in with three guns: two fixed cannons
in the face's front firing straight down the screen and the forge's turret on its heel. Each lost
part brings a new gun up out of a hatch in the face. Once both jet banks are gone its horn splits
lengthwise, its halves swinging apart like jaws (it changes shape, BOSS-45), a gatling riding each.

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

import math

from game.config.bosses.boss_guns import gun_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.bosses.moving_regions import move_point, moving_region, swing
from game.config.record import concat, merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# MB-ANVIL-BARGE-01: the face (the anvil's flat top): its half width, its front and back and its
# top; the step in front of it (lower) and the heel behind it; the waisted base under them and the
# flared feet at its bottom `[half width, front, back, bottom, top]`.
FACE_HALF = 20
FACE_FRONT = -24
FACE_BACK = 26
FACE_TOP = 22
FACE_UNDER = 13
STEP_HALF = 14
STEP_FRONT = -32
STEP_TOP = 18
HEEL_HALF = 14
HEEL_BACK = 40
WAIST = [12, -18, 22, 1, FACE_UNDER]
FEET = [30, -30, 36, -9, 1]
# The horn (MB-ANVIL-BARGE-05): from its root on the step's front to its tip, its half width at its
# root, its underside and its flat top. It is drawn as two halves split along the centre line, each
# swinging out about the vertical through its root's outer corner (`HORN_SWING` degrees at the
# end; the left half is the mirror image).
HORN_TIP = -64
HORN_ROOT_HALF = 13
HORN_UNDER = 6
HORN_TOP = 17
HORN_SWING = 40
# The right half's outline as drawn (closed), from the centre line out and forward.
HORN = [  # type: list[list[float]]
    [0, STEP_FRONT],
    [HORN_ROOT_HALF, STEP_FRONT],
    [11.5, -44],
    [7.5, -55],
    [0, HORN_TIP],
]
# The lift jet banks (MB-ANVIL-BARGE-03): a long nacelle along each foot's flank, its centre, half
# width, half length, bottom and top.
JETS_AT = [34, 3]
JETS = [5.5, 19, -6, 7]
# The forge on the heel (MB-ANVIL-BARGE-03): its centre, half size and top; its turret on top.
FORGE_AT = [0, 33]
FORGE = [9, 6, 27]

# The guns (BOSS-58). Two fixed cannons in the face's front, pointing straight down the screen
# (MB-ANVIL-BARGE-07); the forge's twin turret; under hatches in the face: the turret by its front,
# the fixed casemates on its flanks pointing out and down, the rotor in its hardy hole.
CANNON_AT = [14, -20]
FACE_CANNON = {
    "size": 4.4,
    "barrels": 2,
    "gap": 3.4,
    "bore": 1.3,
    "length": 10,
    "turret": False,
}
FORGE_GUN = {"size": 4.6, "barrels": 2, "gap": 1.4, "bore": 1.1, "length": 7}
TURRET_AT = [0, -8]
FACE_TURRET = {"size": 4.6, "barrels": 3, "gap": 1.1, "bore": 1.0, "length": 7}
CASEMATE_AT = [17, 6]
CASEMATE_DEG = 40
CASEMATE = {
    "size": 3.6,
    "barrels": 2,
    "gap": 2.8,
    "bore": 1.0,
    "length": 6,
    "turret": False,
}
ROTOR_AT = [0, 15]
ROTOR = {"size": 4.4, "barrels": 12, "layout": "ring", "bore": 0.8, "length": 3.2}
# The hatches over the late guns: the round plate over the turret, the square hardy plate over the
# rotor, the flank plates over the casemates (their half sizes).
TURRET_HATCH = 6.5
ROTOR_HATCH = 6
CASEMATE_HATCH = [4.5, 5]

# Its bullets: the cannons' heavy slugs, the forge's sparks, the face's red and orange ones.
SLUG = bullet("orange", 165, 6)
SPARK = bullet("red", 185)
RED = bullet("red", 175)
MAGENTA = bullet("magenta", 175)
SPIRAL = bullet("orange", 160)


def _core(shot: Any, mount_id: str) -> Any:
    """Return `shot`, a core volley, fired from the core's mount `mount_id` (BOSS-58)."""
    return merge(shot, {"mount": mount_id})


def _cannons() -> list[Any]:
    """Return the face cannons' volleys: two slugs side by side from each, one after the other."""
    return [
        _core(volley.fan("core", 1.6, 2, 0, SLUG, 0.6), "face-cannon-left"),
        _core(volley.fan("core", 1.6, 2, 0, SLUG, 1.4), "face-cannon-right"),
    ]


def _casemates() -> list[Any]:
    """Return the flank casemates' volleys: a pair along their barrels, out and down."""
    return [
        _core(volley.fan("core", 2.2, 2, 0, RED, 0.5), "casemate-left"),
        _core(volley.fan("core", 2.2, 2, 0, RED, 1.6), "casemate-right"),
    ]


_ANVIL_BARGE = record({
    "id": "anvil-barge",
    # Its points and its parts' drops (MB-ANVIL-BARGE-11).
    "stats": stats({
        "id": "anvil-barge",
        "name": "Anvil Barge",
        "size": 3.6,
        "coreRadius": 16,
        "coreHealth": 1000,
        "points": 3600,
        "groundSpeed": 0.5,
        "parts": [
            part("jets-left", [-JETS_AT[0], JETS_AT[1]], 11, 560),
            part("jets-right", JETS_AT, 11, 560),
            part("forge", FORGE_AT, 10, 720),
        ],
    }),
    # Where it stops and how it moves in place (MB-ANVIL-BARGE-06): a heavy, slow drift.
    "stopFraction": 0.72,
    "sway": {"amplitude": 45, "period": 9.5},
    "bob": {"amplitude": 3, "period": 3.6},
    "guns": {},
    # Its gun mounts (BOSS-58, MB-ANVIL-BARGE-07).
    "mounts": [
        gun_mount(
            "face-cannon-left",
            "core",
            [-CANNON_AT[0], CANNON_AT[1]],
            FACE_TOP,
            FACE_CANNON,
        ),
        gun_mount("face-cannon-right", "core", CANNON_AT, FACE_TOP, FACE_CANNON),
        gun_mount("forge", "forge", FORGE_AT, FORGE[2], FORGE_GUN),
        gun_mount("face-turret", "core", TURRET_AT, FACE_TOP, FACE_TURRET),
        gun_mount(
            "casemate-left",
            "core",
            [-CASEMATE_AT[0], CASEMATE_AT[1]],
            FACE_TOP,
            merge(CASEMATE, {"restDeg": CASEMATE_DEG}),
        ),
        gun_mount(
            "casemate-right",
            "core",
            CASEMATE_AT,
            FACE_TOP,
            merge(CASEMATE, {"restDeg": -CASEMATE_DEG}),
        ),
        gun_mount("rotor", "core", ROTOR_AT, FACE_TOP, ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (MB-ANVIL-BARGE-08): the forge's turret
    # sweeps aimed pairs; the face cannons fire pairs of slugs straight down at every stage; each
    # stage brings a new gun out of the face: its turret (aimed spreads, then bursts), its flank
    # casemates, then its rotor's spiral of 12.
    "stages": stages(
        [volley.aimed("forge", 2.4, 2, 7, SPARK, 1.2)],
        [
            _cannons(),
            concat(
                _cannons(), [_core(volley.aimed("core", 2.4, 3, 10, MAGENTA, 0.8), "face-turret")]
            ),
            concat(
                _cannons(),
                concat(
                    [_core(volley.burst("core", 2.6, 3, 0.14, MAGENTA, 0.9), "face-turret")],
                    _casemates(),
                ),
            ),
            concat(
                _cannons(),
                concat(
                    [_core(volley.ring("core", 1.5, 12, 15, SPIRAL, 0.4), "rotor")],
                    _casemates(),
                ),
            ),
        ],
    ),
})

# MB-ANVIL-BARGE-05: the right horn half's swing about the vertical through its root's outer corner,
# out to the right (counter-clockwise seen from above); the left one is its mirror image.
HORN_PIVOT = [  # type: list[float]
    HORN_ROOT_HALF,
    STEP_FRONT,
    HORN_TOP,
]
HORN_MOTION = swing(HORN_PIVOT, "up", [0, HORN_SWING])
HORN_HEIGHTS = [HORN_UNDER, HORN_TOP]
# Where each gatling stands on its horn half, as drawn (closed), and its pod's base and top
# (MB-ANVIL-BARGE-10): it rides the half to where the half ends up.
GATLING_ON = [5.2, -44]
GATLING_POD = [HORN_TOP, HORN_TOP + 3]


def gatling_at() -> list[float]:
    """Return where the right gatling ends up: its spot on the right half, swung out."""
    end = move_point(HORN_MOTION, HORN_SWING, [GATLING_ON[0], GATLING_ON[1], HORN_TOP])
    return [round(end[0] * 100) / 100, round(end[1] * 100) / 100]


def _circle(at: list[Any], radius: float, count: int) -> list[list[float]]:
    """Return a hatch's outline: `count` corners round `at`, `radius` out."""
    return [
        [
            at[0] + radius * math.cos(k * 2 * math.pi / count + math.pi / count),
            at[1] + radius * math.sin(k * 2 * math.pi / count + math.pi / count),
        ]
        for k in range(count)
    ]


def _box(at: list[Any], half: list[Any]) -> list[list[float]]:
    """Return a hatch's outline: a rectangle `half` big either way round `at`."""
    return [
        [at[0] - half[0], at[1] - half[1]],
        [at[0] + half[0], at[1] - half[1]],
        [at[0] + half[0], at[1] + half[1]],
        [at[0] - half[0], at[1] + half[1]],
    ]


def _hatch(region_id: str, outline: list[Any], mount_id: str) -> Any:
    """Return the hatch over the core's mount `mount_id`: it bursts as that gun comes out."""
    return armour_region(region_id, None, outline, "ring", None, False, mount_id)


_GATLING_AT = gatling_at()

# Its transformation (BOSS-45, MB-ANVIL-BARGE-10): once both lift jet banks are gone its horn
# splits lengthwise, the halves swinging apart like jaws, a gatling riding each. The face's late
# guns come out of hatches as their stages first use them (BOSS-58).
ANVIL_BARGE = with_weapons(
    merge(_ANVIL_BARGE, {"transformParts": [["jets-left", "jets-right"]]}),
    [
        hidden_weapon(
            "gatling-left",
            "gatling",
            [-_GATLING_AT[0], _GATLING_AT[1]],
            5.5,
            580,
            1,
            "red",
            1.2,
            GATLING_POD,
        ),
        hidden_weapon(
            "gatling-right", "gatling", _GATLING_AT, 5.5, 580, 1, "red", 2.0, GATLING_POD
        ),
    ],
    concat(
        moving_region("horn", 1, HORN, HORN_MOTION, None, HORN_HEIGHTS),
        [
            _hatch("turret-hatch", _circle(TURRET_AT, TURRET_HATCH, 8), "face-turret"),
            _hatch("rotor-hatch", _box(ROTOR_AT, [ROTOR_HATCH, ROTOR_HATCH]), "rotor"),
            _hatch(
                "casemate-hatch-left",
                _box([-CASEMATE_AT[0], CASEMATE_AT[1]], CASEMATE_HATCH),
                "casemate-left",
            ),
            _hatch("casemate-hatch-right", _box(CASEMATE_AT, CASEMATE_HATCH), "casemate-right"),
        ],
    ),
)
