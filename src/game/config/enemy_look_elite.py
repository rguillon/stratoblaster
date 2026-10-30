"""Look of the elite enemies (P05-R19 to P05-R23, GD-61)

Each kind's own neon colour, linear RGB 0..1, in the style of `ENEMY_LOOK.neon`.
"""

from game.config.record import record

# Neon colours of the elite kinds, one distinct colour each (P05-R19 to P05-R23).
ELITE_NEON = record(
    {
        # P05-R19: glowing teal eyes.
        "hydra": [0.05, 1, 0.78],
        # P05-R20: a white-gold equator.
        "orbiter": [1, 0.86, 0.5],
        # P05-R21: crimson.
        "scissor": [0.95, 0.04, 0.22],
        # P05-R22: steel blue.
        "juggernaut": [0.42, 0.62, 0.95],
        # P05-R23: honey-amber cells.
        "hive": [1, 0.62, 0.12],
    }
)
