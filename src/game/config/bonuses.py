"""Weapon bonuses (phase 6 review; they level the weapon up, GAME-WPN-14)

The chance a destroyed enemy drops one grows with its health (GAME-BONUS-02): 6 % for the small
ones (Gnat to Splitter), a Lancer 12 %, a Rocketeer 15 %, a Bulwark or a Carrier 20 %. A
play-through shooting most enemies gets about 8 (1-1) to 23 (1-5), the first within about a minute
and a half (D-049). They fall a little slower than the ground scrolls, so there is time to fly over
them (GAME-BONUS-07); the ship picks one up within `pickupRadius` (GAME-BONUS-08).

GAME-BONUS-03: a destroyed enemy may drop a life (1 %) or a bomb (3 %) bonus instead, drawn first,
so it never drops two; a mini boss always drops a life (GAME-BONUS-04). At the most, they score
points (GAME-BONUS-10).
"""

from game.config.record import record
from game.config.scoring import SCORING

BONUS_RULES = record(
    {
        "chance": {"perHealth": 0.0015, "min": 0.06, "max": 0.2},
        "fallSpeed": 45,
        "pickupRadius": 22,
        "special": {"life": 0.01, "bomb": 0.03},
        "overflowPoints": SCORING.overflow,
    }
)
