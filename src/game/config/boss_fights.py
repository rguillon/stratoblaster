"""How boss fights go (P07, tunable values), ported from `config/boss-fights.ts`.

The ground eases to the fight's speed and back over 2 s (`boss_speed_ease`), and the health bar
fills up over 1 s (`health_bar_fill`).
"""

from game.config.record import record

BOSS_FIGHT_RULES = record({"speedEaseSeconds": 2, "barFillSeconds": 1})
