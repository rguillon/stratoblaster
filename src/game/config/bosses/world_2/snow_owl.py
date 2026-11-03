# Copyright (c) 2026 Renaud Guillon
"""The Snow Owl (2-3's mini boss, specs/bosses/mini/2-3-snow-owl.md).

The mini boss of the Tundra level. Offsets in px from the boss's centre, X right and Y up (its nose
points down, at -Y). The stage patterns are the agent's design (MB-SNOW-OWL-11): the parts fire the
same while they stand, the core fires something new at every stage, and its last stage (only the
core left) a ring used by no earlier stage. Health values (MB-SNOW-OWL-14) are placeholders for the
World 2 tuning (WLD-2-25, WLD-2-27).
"""

from game.config.bosses.boss_kit import bullet, mirror, part, stages, stats, twin, volley
from game.config.bosses.hidden_weapons import armour_region, hidden_weapon, with_weapons
from game.config.bosses.moving_regions import moving_region, slide
from game.config.record import concat, merge, record

MAGENTA = bullet("magenta", 180)
RED = bullet("red", 190)
BLUE = bullet("blue", 185)
PURPLE = bullet("purple", 195)

# The guns' muzzles (phase 7 review, MB-SNOW-OWL-03): the tips of the barrels its model draws, from
# the boss's centre, X right, Y up, and height above the playfield (see `BossDesign.guns`).

# The right wing radar pod's two fan barrels, under the pod's front.
OWL_POD_GUNS = twin(38, -17, 1.5, 2.5)
# The sensor eye's lens: its laser leaves from the lens's centre.
OWL_EYE_LENS = [[0, -38.5, 6]]
# The two chin guns either side of the eye (the core's aimed shots and bursts).
OWL_CHIN_GUNS = twin(13, -27, 1.5)
# The crown emitter on its back, between the ear tufts (the core's last-stage rings).
OWL_CROWN = [[0, 10, 12.5]]

# 2-3: a wide-winged recon drone with white neon and a big round sensor eye at its front; two wing
# radar pods fire fans and shield the core (MB-SNOW-OWL-09), the eye fires a laser after its
# warning line (MB-SNOW-OWL-10). The eye sits in front of the core, so it can always be shot.
_SNOW_OWL = record({
    "id": "snow-owl",
    # Its core, wing pods, eye and points (MB-SNOW-OWL-14).
    "stats": stats({
        "id": "snow-owl",
        "name": "Snow Owl",
        "size": 3,
        "coreRadius": 18,
        "coreHealth": 1250,
        "points": 5500,
        "groundSpeed": 0.5,
        "parts": [
            part("pod-left", [-38, -2], 13, 850),
            part("pod-right", [38, -2], 13, 850),
            part("eye", [0, -30], 11, 600, {"shields": False}),
        ],
    }),
    # Where it stops and how it moves in place (MB-SNOW-OWL-08).
    "stopFraction": 0.73,
    "sway": {"amplitude": 65, "period": 7.5},
    "bob": {"amplitude": 9, "period": 3.4},
    "guns": {
        "core": {"gun": OWL_CHIN_GUNS, "ring": OWL_CROWN},
        "pod-left": {"gun": mirror(OWL_POD_GUNS)},
        "pod-right": {"gun": OWL_POD_GUNS},
        "eye": {"laser": OWL_EYE_LENS},
    },
    # The pods' fans and the eye's laser, then the core's pattern per stage (MB-SNOW-OWL-11).
    "stages": stages(
        [
            # The pods' fans cross under the drone, each leaning towards the other side.
            volley.fan("pod-left", 2.3, 3, 14, MAGENTA, 0.9, 10),
            volley.fan("pod-right", 2.3, 3, 14, MAGENTA, 2, -10),
            volley.laser("eye", 5.5, 1.4, 3),
        ],
        [
            [volley.aimed("core", 3, 1, 0, RED, 1.5)],
            [volley.aimed("core", 2.4, 3, 12, RED, 0.8)],
            [volley.burst("core", 2.2, 4, 0.14, RED, 0.6)],
            [
                volley.ring("core", 1.4, 12, 8, BLUE, 0.4),
                volley.aimed("core", 2.4, 1, 0, PURPLE, 1),
            ],
        ],
    ),
})

# Its transformation (D-230, MB-SNOW-OWL-13): once both wing pods are gone its outer wing panels
# slide out, their dark metal spars showing, a sweeper riding each new tip; its back plating bursts
# off for a mortar (its change of shape, MB-SNOW-OWL-07).
SNOW_OWL = with_weapons(
    merge(_SNOW_OWL, {"transformParts": [["pod-left", "pod-right"]]}),
    [
        hidden_weapon("sweeper-left", "sweeper", [-61, -1], 6, 680, 1, "magenta", 1.2, 7),
        hidden_weapon("sweeper-right", "sweeper", [61, -1], 6, 680, 1, "magenta", 3.8, 7),
        hidden_weapon("mortar", "mortar", [0, 8], 9, 680, 1, "purple", 2.0, 14),
    ],
    concat(
        # MB-SNOW-OWL-07: the outer panel of each wing from 30 px out (its leading edge at -Y),
        # and the deck it slides along out to 56 px; a sweeper rides it.
        moving_region(
            "wingtips",
            1,
            [[30, -9.2], [48, -5], [56, -5], [56, 12], [30, 12]],
            slide([[0, 0, 0], [16, 0, 0]]),
            "wing",
            [-3, 1000],
        ),
        [
            # MB-SNOW-OWL-07: the plating of its back, over the flat deck of the back from the
            # tail (22 px behind) to the head's root (6 px ahead); the mortar lies under it.
            armour_region(
                "back",
                1,
                [
                    [-4.5, 22],
                    [4.5, 22],
                    [6, 18],
                    [7.5, 4],
                    [7.3, -6],
                    [-7.3, -6],
                    [-7.5, 4],
                    [-6, 18],
                ],
                "shell",
                None,
                False,
            ),
        ],
    ),
)
