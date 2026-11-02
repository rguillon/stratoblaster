# Copyright (c) 2026 Renaud Guillon
"""Look of the elite enemies (the elite kinds of specs/enemies/, GFX-ART-05).

Each kind's own neon colour, linear RGB 0..1, in the style of `ENEMY_LOOK.neon`.
"""

from game.config.record import record

# Neon colours of the elite kinds, one distinct colour each (ENM-06; ENM-38: drawn yellow or green).
ELITE_NEON = record({
    # ENM-HYDRA-03: glowing teal eyes (drawn green).
    "hydra": [0.05, 1, 0.78],
    # ENM-ORBITER-03: a white-gold equator (drawn yellow).
    "orbiter": [1, 0.86, 0.5],
    # ENM-SCISSOR-03: crimson (drawn yellow).
    "scissor": [0.95, 0.04, 0.22],
    # ENM-JUGGERNAUT-03: steel blue (drawn green).
    "juggernaut": [0.42, 0.62, 0.95],
    # ENM-HIVE-03: honey-amber cells (drawn yellow).
    "hive": [1, 0.62, 0.12],
})
