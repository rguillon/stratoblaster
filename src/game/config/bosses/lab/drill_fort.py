# Copyright (c) 2026 Renaud Guillon
"""The Drill Fort, the Lab's L-23 mini boss (specs/bosses/lab/L-23-drill-fort.md).

Lab boss: in the dev viewer only, no level brings it in. A gigantic flying mining fortress seen
from above: a huge spiralled drill head spinning at its front, a boxy armoured body on two long
track pontoons, a conveyor belt down its back from the drill to the control cab, four ore hoppers
either side of the belt, two exhaust stacks. It comes in with three guns only: a fixed twin cannon
either side of the drill and the cab's turret. Each part it loses brings out more guns: turrets
rise out of the rear hoppers' ore, a fixed spitter out of the conveyor's head, a rotor out of its
tail. Once two parts are gone the front hoppers tip over the sides, dumping their ore, and a mortar
rises out of each (a moving piece, BOSS-45, and a shed load, BOSS-42).

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y).
"""

from game.config.bosses.boss_guns import gun_mount
from game.config.bosses.boss_kit import bullet, part, stages, stats, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.bosses.moving_regions import moving_region, swing
from game.config.record import concat, merge, record

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


# MB-DRILL-FORT-01: the body, a bevelled armoured box `[half width, front, back]`, its floor, its
# walls' top and its deck.
BODY = [24, -30, 38]
BODY_LOW = 2
BODY_WALL = 11
DECK = 12
# The track pontoons along its flanks: `[inner x, outer x, front, back]` and their top.
TRACK = [25, 35, -26, 34]
TRACK_TOP = 9
# The drill head (MB-DRILL-FORT-02): its axis' height, its collar `[y0, y1, radius]` on the body's
# front, its cone from its base `[y, radius]` to its tip's Y, and its flutes.
DRILL_AXIS = 7.5
COLLAR = [-37, -29, 13]
CONE_BASE = [-37, 12]
CONE_TIP = -76
FLUTES = 3
# The hoppers (MB-DRILL-FORT-03): the right ones' outline `[x0, x1, y0, y1]` (mirrored), front pair
# (they tip, the mortars under them) and rear pair (their guns rise out of the ore); their rim's
# height and the ore's top.
HOPPER_FRONT = [5, 19, -22, -7]
HOPPER_REAR = [5, 19, 2, 17]
HOPPER_TOP = 21
ORE_TOP = 18.5
# The conveyor belt down the centre line: `[half width, front, back]`, its belt's height.
CONVEYOR = [3.6, -30, 24]
BELT_TOP = 14
# The exhaust stacks: their centre (right; mirrored), radius and top.
STACK_AT = [19, 29]
STACK_RADIUS = 3.2
STACK_TOP = 27
# The control cab at its back: `[half width, front, back]` and its roof.
CAB = [11, 25, 38]
CAB_TOP = 20

RED = bullet("red", 185)
ORANGE = bullet("orange", 175)
AMBER = bullet("orange", 160, 5)

# Its guns (BOSS-58, MB-DRILL-FORT-04): a fixed twin cannon either side of the drill (its parts),
# and the core's: the cab's twin turret (from the start), a triple turret under the grate of each
# rear hopper, a fixed triple spitter under the conveyor's head cowl and a rotor under the
# conveyor's tail cowl (its last rings).
CHEEK_AT = [19, -37]
CHEEK_GUN_AT = [19, -39]
CHEEK_GUN = {
    "size": 3.6,
    "barrels": 2,
    "gap": 2.6,
    "bore": 1.0,
    "length": 8,
    "turret": False,
    "restDeg": 0,
}
CAB_GUN_AT = [0, 31.5]
CAB_GUN = {"size": 4.4, "barrels": 2, "gap": 1.2, "bore": 1.0, "length": 7}
HOPPER_GUN_AT = [12, 9.5]
HOPPER_GUN_H = ORE_TOP
HOPPER_GUN = {"size": 4.2, "barrels": 3, "gap": 1.0, "bore": 0.85, "length": 6.5}
SPITTER_AT = [0, -28]
# On top of the conveyor's head, raised over the drill's collar.
SPITTER_H = 21
SPITTER = {
    "size": 3.4,
    "barrels": 3,
    "gap": 1.0,
    "bore": 0.8,
    "length": 6,
    "turret": False,
    "restDeg": 0,
}
ROTOR_AT = [0, 19]
ROTOR_H = BELT_TOP + 0.5
ROTOR = {"size": 4.0, "barrels": 10, "layout": "ring", "bore": 0.75, "length": 3.0}


def _named(shot: Any, mount_id: str) -> Any:
    """`shot` fired from the core's mount `mount_id` (BOSS-58)."""
    return merge(shot, {"mount": mount_id})


# The core's guns per stage: each new stage brings out new ones (the round's gun progression); the
# older ones keep firing.
CAB_AIMED = _named(volley.aimed("core", 2.6, 1, 0, ORANGE, 1.4), "cab-gun")
CAB_SPREAD = _named(volley.aimed("core", 2.8, 3, 8, ORANGE, 1.2), "cab-gun")
HOPPER_BURSTS = [
    _named(volley.burst("core", 2.8, 3, 0.13, RED, 0.8), "hopper-gun-left"),
    _named(volley.burst("core", 2.8, 3, 0.13, RED, 2.2), "hopper-gun-right"),
]
SPITTER_FAN = _named(volley.fan("core", 2.2, 3, 0, AMBER, 0.6), "spitter")
ROTOR_RING = _named(volley.ring("core", 1.6, 10, 9, ORANGE, 0.4), "rotor")

_DRILL_FORT = record({
    "id": "drill-fort",
    # Its points and its parts' drops (MB-DRILL-FORT-11).
    "stats": stats({
        "id": "drill-fort",
        "name": "Drill Fort",
        "size": 3.4,
        "coreRadius": 16,
        "coreHealth": 1100,
        "points": 4400,
        "groundSpeed": 0.6,
        "parts": [
            part("gun-left", [-CHEEK_AT[0], CHEEK_AT[1]], 8, 700),
            part("gun-right", CHEEK_AT, 8, 700),
            # The drill head carries no gun: its loss brings out new ones all the same.
            part("drill", [0, -55], 13, 850),
        ],
    }),
    # Where it stops and how it moves in place (MB-DRILL-FORT-06): a heavy, slow grind.
    "stopFraction": 0.74,
    "sway": {"amplitude": 45, "period": 8},
    "bob": {"amplitude": 3, "period": 3.4},
    "guns": {},
    # Its gun mounts (BOSS-58, MB-DRILL-FORT-04).
    "mounts": [
        gun_mount("gun-left", "gun-left", [-CHEEK_GUN_AT[0], CHEEK_GUN_AT[1]], DECK, CHEEK_GUN),
        gun_mount("gun-right", "gun-right", CHEEK_GUN_AT, DECK, CHEEK_GUN),
        gun_mount("cab-gun", "core", CAB_GUN_AT, CAB_TOP, CAB_GUN),
        gun_mount(
            "hopper-gun-left",
            "core",
            [-HOPPER_GUN_AT[0], HOPPER_GUN_AT[1]],
            HOPPER_GUN_H,
            HOPPER_GUN,
        ),
        gun_mount("hopper-gun-right", "core", HOPPER_GUN_AT, HOPPER_GUN_H, HOPPER_GUN),
        gun_mount("spitter", "core", SPITTER_AT, SPITTER_H, SPITTER),
        gun_mount("rotor", "core", ROTOR_AT, ROTOR_H, ROTOR),
    ],
    # Its parts' volleys, then the core's pattern per stage (MB-DRILL-FORT-08): the cheek cannons'
    # parallel pairs straight down; the cab's aimed shots, then the hopper turrets' bursts, the
    # spitter's parallel triples, and last the rotor's rings of 10.
    "stages": stages(
        [
            volley.fan("gun-left", 2.4, 2, 0, RED, 1.0),
            volley.fan("gun-right", 2.4, 2, 0, RED, 2.2),
        ],
        [
            [CAB_AIMED],
            concat([CAB_SPREAD], HOPPER_BURSTS),
            concat([CAB_AIMED, SPITTER_FAN], HOPPER_BURSTS),
            concat([ROTOR_RING, SPITTER_FAN, CAB_SPREAD], HOPPER_BURSTS),
        ],
    ),
})

# Its transformation (MB-DRILL-FORT-10): the front hoppers, as drawn, and their tip about their
# outer bottom edge, out over the tracks; the ore load in them (shed, it bursts into lumps); the
# mortars under it, on the deck.
HOPPER_TIP = swing(
    [HOPPER_FRONT[1], (HOPPER_FRONT[2] + HOPPER_FRONT[3]) / 2, DECK], "along", [0, 118]
)
ORE = [
    [HOPPER_FRONT[0] + 1.5, HOPPER_FRONT[2] + 1.5],
    [HOPPER_FRONT[1] - 1.5, HOPPER_FRONT[2] + 1.5],
    [HOPPER_FRONT[1] - 1.5, HOPPER_FRONT[3] - 1.5],
    [HOPPER_FRONT[0] + 1.5, HOPPER_FRONT[3] - 1.5],
]
MORTAR_AT = [12, -14.5]
MORTAR_POD = [DECK, DECK + 2.5]


def _box(b: list[Any]) -> list[list[Any]]:
    """Return the outline of the box `[x0, x1, y0, y1]`."""
    return [[b[0], b[2]], [b[1], b[2]], [b[1], b[3]], [b[0], b[3]]]


def _hatch(region_id: str, at: list[Any], half: list[Any], mount_id: str) -> Any:
    """Return the hatch over the core's mount `mount_id` (BOSS-58): a box `half` round `at`."""
    outline = [
        [at[0] - half[0], at[1] - half[1]],
        [at[0] + half[0], at[1] - half[1]],
        [at[0] + half[0], at[1] + half[1]],
        [at[0] - half[0], at[1] + half[1]],
    ]
    return armour_region(region_id, None, outline, "shell", None, False, mount_id)


# The hatches: the grates over the rear hoppers (their turrets), the conveyor's head and tail cowls
# (the spitter, the rotor).
GRATE_HALF = [6, 6.5]
COWL_HALF = [5, 4]
ROTOR_COWL = [5.5, 5.5]

DRILL_FORT = with_weapons(
    _DRILL_FORT,
    [
        hidden_weapon(
            "mortar-left",
            "mortar",
            [-MORTAR_AT[0], MORTAR_AT[1]],
            7,
            680,
            1,
            "orange",
            1.2,
            MORTAR_POD,
        ),
        hidden_weapon("mortar-right", "mortar", MORTAR_AT, 7, 680, 1, "orange", 2.0, MORTAR_POD),
    ],
    concat(
        moving_region("hopper", 1, _box(HOPPER_FRONT), HOPPER_TIP, None, [DECK, HOPPER_TOP]),
        [
            armour_region("ore", 1, ORE, "shell", [DECK + 0.5, ORE_TOP]),
            _hatch(
                "grate-left", [-HOPPER_GUN_AT[0], HOPPER_GUN_AT[1]], GRATE_HALF, "hopper-gun-left"
            ),
            _hatch("grate-right", HOPPER_GUN_AT, GRATE_HALF, "hopper-gun-right"),
            _hatch("head-cowl", SPITTER_AT, COWL_HALF, "spitter"),
            _hatch("tail-cowl", ROTOR_AT, ROTOR_COWL, "rotor"),
        ],
    ),
)
