# Copyright (c) 2026 Renaud Guillon
"""The player's bombs (GAME-BOMB-01, D-091).

3 at the start (then those kept from the level completed before, reviewer 2026-10-28), after a
Continue, and again after a lost life if fewer are left (GAME-BOMB-02); as many as bomb bonuses add.
One deals 100 to every enemy on screen, enough to destroy every World 1 kind up to the Rocketeer
(100 HP, GAME-BOMB-04), clears the enemy shots (GAME-BOMB-05), and keeps the ship safe for 1 s
(GAME-BOMB-06).
"""

from game.config.record import record

BOMB_RULES = record({
    "start": 3,
    "damage": 100,
    "seconds": 1,
})
