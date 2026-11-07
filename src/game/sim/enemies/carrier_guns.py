# Copyright (c) 2026 Renaud Guillon
"""The gun turrets of the carriers, the Hatchery and the Broodmother (WPN-02)."""

from core.entities.barrel import Barrel
from core.entities.boss_turret import BossTurret, BossTurretSpec
from core.entities.enemy import Enemy
from core.systems.projectile_motion import heading_to, turn_towards, wrap_angle
from game.sim.enemies.enemy_helpers import DEG, Cadence

# isort: split
# __pragma__ ("skip")
from typing import Any

from core.entities.enemy import EnemyContext

# __pragma__ ("noskip")


# A turret fires once it points within this of the player (WPN-02).
AIMED = 6 * DEG


class CarrierGuns:
    """A carrier's gun turrets, from its `turrets` config: each turns on its own.

    Each turret (`turrets`, pointing down the screen at rest) has its barrel (`barrels`); it turns
    towards the player at `turnDeg` per second and fires an aimed bullet once it points at them,
    a shot each every `fireInterval`, the first `firstShot` after it shows.
    """

    def __init__(self, guns: Any) -> None:
        self._guns = guns
        self.turrets = [BossTurret(BossTurretSpec(p[0], p[1], guns.turnDeg)) for p in guns.pivots]
        self.barrels = [Barrel([p[0], p[1] - guns.barrel, guns.height]) for p in guns.pivots]
        self._cadence = Cadence(guns.fireInterval, guns.firstShot)
        # The shot each owes, waiting for it to point at the player.
        self._due = [0 for _p in guns.pivots]

    def update(self, enemy: Enemy, ctx: EnemyContext, dt: float) -> None:
        """Turn each turret of `enemy` towards the player, and fire the shot it owes once aimed."""
        guns = self._guns
        shots = self._cadence.tick(dt * ctx.fire_rate)
        for k, turret in enumerate(self.turrets):
            # One shot owed at most: a turret slow to come round does not fire a burst.
            self._due[k] = min(1, self._due[k] + shots)
            pivot = ctx.seen(enemy.place((turret.spec.x, turret.spec.y, guns.height)))
            target = heading_to(pivot.x, pivot.y, ctx.player_x, ctx.player_y)
            rate = turret.spec.turn_rate_deg * DEG * dt
            turret.aim = wrap_angle(turn_towards(turret.aim, target - enemy.heading, rate))
            own = enemy.heading + turret.aim
            if self._due[k] <= 0 or abs(wrap_angle(own - target)) > AIMED:
                continue
            barrel = self.barrels[k]
            tip = ctx.seen(enemy.place(turret.turned(barrel.muzzle)))
            barrel.kick(enemy.age)
            ctx.fire_bullet(tip.x, tip.y, own, guns.bullet)
            self._due[k] -= 1
