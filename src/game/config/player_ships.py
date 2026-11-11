# Copyright (c) 2026 Renaud Guillon
"""The player ship and its stats (GAME-SHIP-01; top speed GAME-SHIP-02, health GAME-SHIP-03).

The game has one ship, the Balanced one (D-326). Its speed is a multiple of the base speed, raised
from 100 to 150 px/s, then to 225 px/s, at the reviewer's requests in phase 6 (D-044, D-047).
"""

from game.config.record import record

PLAYER_SHIPS = record({
    "baseSpeedPxPerSec": 225,
    "ships": [
        {"id": "balanced", "name": "Balanced", "maxSpeedFactor": 1, "maxHealth": 100},
    ],
})
