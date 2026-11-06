# Copyright (c) 2026 Renaud Guillon
"""Tunables of the enemies' and bosses' weapons (`specs/enemies/weapons.md`).

Seconds and logical pixels.
"""

from game.config.record import record

WEAPONS = record({
    # WPN-08: a missile flies straight out of its port this long before it turns.
    "missileLaunchSeconds": 0.25,
    # WPN-09: a missile from an upward silo lofts this long, leaving straight up at this speed
    # (px/s), slowing to its top and coming down level onto the plane of play; only then it homes.
    "missileLoftSeconds": 2.1,
    "missileLoftSpeed": 260,
    # WPN-09: and drifts off to its side (away from its block's middle), at most this fast (px/s, a
    # third of the way through), so the missiles of a block part.
    "missileLoftDrift": 110,
    # WPN-07: a port is empty when its missile has left; the next rocket is seen rising into it
    # over this long after the launch (from `missileReloadShow` of it on, hidden before).
    "missileReloadSeconds": 1.2,
    "missileReloadShow": 0.35,
})
