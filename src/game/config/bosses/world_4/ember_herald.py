"""P10-R11, 4-5's mini boss: the Ember Herald ().

Offsets in px from the boss's centre, X right and Y up (its nose points down, at -Y). Stage
patterns as for the earlier mini bosses (P07-R04, D-055): its three ember lances fire spirals from
their tips while they stand, the core fires aimed bursts that change at every stage, and twin
spirals of its own, used by no earlier stage, once it stands alone.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.bosses.boss_kit import bullet, part, stages, stats, twin, volley
from game.config.bosses.boss_rage import rage
from game.config.record import concat, record

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

MAGENTA = bullet("magenta", 215)
PURPLE = bullet("purple", 190)
BLUE = bullet("blue", 205)

# The turning ring's ember lances (P10-R11): each points out of the ring, its centre `orbit` px
# from the core, its tip (where its spiral leaves from) `tip` px out, `height` above the playfield.
# The model draws them from these numbers.
EMBER_LANCE = record({"orbit": 40, "tip": 61, "height": 12})

# The lances' turns around the core at a spin of 0, from the nose (radians, clockwise on screen).
LANCE_TURNS = [0, (2 * math.pi) / 3, (4 * math.pi) / 3]


def out_along(turn: float, r: float) -> Any:
    """Where a point `r` px out along the turn `turn` is on the playfield, at a spin of 0."""
    return [r * math.sin(turn), -r * math.cos(turn)]


def lance_tip(turn: float) -> Any:
    """The tip of the lance turned by `turn`: where its bullets leave from."""
    return [concat(out_along(turn, EMBER_LANCE.tip), [EMBER_LANCE.height])]


# The twin ember cannons under the nose (aimed bursts).
EMBER_GUNS = twin(5, -57, 3)
# The core's spiral emitter: the lit crown of the spire over the ring's hub.
EMBER_CROWN = [0, 0, 24]


def lance_parts() -> Any:
    """The three lances, on the ring around the core."""
    return [
        part(
            "lance-" + str(i + 1),
            out_along(turn, EMBER_LANCE.orbit),
            14,
            1200,
            {"orbits": True},
        )
        for i, turn in enumerate(LANCE_TURNS)
    ]


# 4-5: a fast, spiky interceptor wreathed in embers, gold neon (P10-R11); three ember lances on a
# turning ring fire spirals and shield the core, which fires aimed bursts from its nose. It chases
# the ship down the volcano's slope (ground x1.4).
EMBER_HERALD = record(
    {
        "id": "ember-herald",
        # Angry after each destroyed part (phase 7 review): the hottest mini boss so far.
        "rage": rage.spirals(13.5, "magenta", "purple"),
        "stats": stats(
            record(
                {
                    "id": "ember-herald",
                    "name": "Ember Herald",
                    "size": 3.5,
                    "coreRadius": 21,
                    "coreHealth": 1950,
                    "points": 9000,
                    "groundSpeed": 1.4,
                    "parts": lance_parts(),
                }
            )
        ),
        "stopFraction": 0.74,
        "sway": {"amplitude": 60, "period": 6},
        "bob": {"amplitude": 8, "period": 2.8},
        "spinRate": 0.9,
        "guns": {
            "core": {"gun": EMBER_GUNS, "ring": [EMBER_CROWN]},
            "lance-1": {"gun": lance_tip(LANCE_TURNS[0])},
            "lance-2": {"gun": lance_tip(LANCE_TURNS[1])},
            "lance-3": {"gun": lance_tip(LANCE_TURNS[2])},
        },
        "stages": stages(
            [
                volley.ring("lance-1", 0.85, 3, 23, PURPLE, 0.4),
                volley.ring("lance-2", 0.85, 3, 23, PURPLE, 0.68),
                volley.ring("lance-3", 0.85, 3, 23, PURPLE, 0.96),
            ],
            [
                [volley.burst("core", 2.4, 4, 0.13, MAGENTA, 1.4)],
                [volley.burst("core", 2.2, 5, 0.11, MAGENTA, 0.8)],
                [
                    volley.burst("core", 2.1, 5, 0.1, MAGENTA, 0.6),
                    volley.aimed("core", 3.1, 3, 13, BLUE, 1.6),
                ],
                [
                    volley.ring("core", 0.5, 5, 17, PURPLE, 0.4),
                    volley.ring("core", 0.5, 5, -19, BLUE, 0.65),
                    volley.burst("core", 2.4, 4, 0.11, MAGENTA, 1.2),
                ],
            ],
        ),
    }
)
