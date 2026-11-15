# Copyright (c) 2026 Renaud Guillon
"""What hurts the player (phase 6 review; GAME-LIFE-03).

3 lives at the start (GAME-LIFE-02; then those kept from the level completed before, reviewer
2026-10-28), as many as life bonuses add, each a full health bar (GAME-LIFE-01: the ship's
`maxHealth`, 100); 2 s of invincibility after a hit (GAME-LIFE-07); a
hitbox of 5 px around the ship's centre, much smaller than its model (GAME-SHIP-06). Bullets take
10, missiles 20, a laser beam 25 (once per beam), ramming an enemy 30, and the rammed enemy takes 40
(small ones blow up) (GAME-LIFE-03, GAME-LIFE-05, D-050).
"""

from game.config.record import record

HULL_RULES = record({
    "lives": 3,
    "invincibleSeconds": 2,
    "hitRadius": 5,
    "damage": {"bullet": 10, "missile": 20, "laser": 25, "collision": 30},
    "ramDamage": 40,
})
