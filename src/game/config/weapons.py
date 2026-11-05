# Copyright (c) 2026 Renaud Guillon
"""Tunables of the enemies' and bosses' weapons (`specs/enemies/weapons.md`).

Seconds and logical pixels.
"""

from game.config.record import record

WEAPONS = record({
    # WPN-08: a missile flies straight out of its port this long before it turns.
    "missileLaunchSeconds": 0.25,
    # WPN-09: a missile from an upward silo rises this long, then arcs over to the plane of play
    # along a half loop of this radius.
    "missileClimbSeconds": 0.3,
    "missileArcRadius": 40,
    # WPN-07: a port is empty when its missile has left; the next rocket is seen rising into it
    # over this long after the launch (from `missileReloadShow` of it on, hidden before).
    "missileReloadSeconds": 1.2,
    "missileReloadShow": 0.35,
})
