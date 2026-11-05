# Copyright (c) 2026 Renaud Guillon
"""The Hatchery (`specs/enemies/hatchery.md`)."""

from core.entities.barrel import Barrel
from core.entities.boss_turret import BossTurret, BossTurretSpec
from core.entities.enemy import Enemy
from core.systems.projectile_motion import heading_to, turn_towards, wrap_angle
from game.config.enemy_hatchery import HATCHERY_CONFIG
from game.sim.enemies.enemy_helpers import DEG, DOWN, Cadence, on_playfield
from game.sim.enemies.wasp import Wasp

# isort: split
# __pragma__ ("skip")
from core.entities.enemy import EnemyContext

# __pragma__ ("noskip")


CFG = HATCHERY_CONFIG
GUNS = CFG.turrets
INFINITY = float("Infinity")
# A turret fires once it points within this of the player (WPN-02).
AIMED = 6 * DEG


def ramp(t: float, length: float) -> float:
    """Return how far a move `length` seconds long is after `t` seconds, 0 to 1."""
    return min(1, max(0, t / length))


class Hatchery(Enemy):
    """ENM-HATCHERY-05: a big, slow flight deck.

    It descends straight down. A gun turret on each side turns towards the player and fires an
    aimed bullet once it points at them, each every `fireInterval` (it no longer holds its fire,
    ENM-HATCHERY-06). Every 6 s the doors of its three deck bays slide open, the Wasp loaded in
    each rises to the deck, and they take off together, flying down ahead of it over its deck; the
    doors close behind them while the next Wasps are loaded (ENM-HATCHERY-07). It stops launching
    in the lower part of the screen (ENM-HATCHERY-08). Its `charge` is how close the next launch
    is (the bays' edges glow).

    `tracks` tells the model where its moving parts are: each bay's doors (how open, 0 to 1), then
    each bay's Wasp (how far risen, 0 to 1; below 0 when the bay is empty).
    """

    def __init__(self, x: float, y: float) -> None:
        super().__init__(x, y, CFG.stats)
        self._launcher = Cadence(CFG.launchInterval, CFG.firstLaunch)
        self._launched_at: float | None = None
        self.tracks = [0.0 for _i in range(2 * len(CFG.bays))]
        self.heading = DOWN
        # Its two turrets (each turns on its own, `turrets`), each with its barrel, pointing down
        # the screen at rest; the shot each owes, waiting for it to point at the player.
        self.turrets = [BossTurret(BossTurretSpec(p[0], p[1], GUNS.turnDeg)) for p in GUNS.pivots]
        self.barrels = [Barrel([p[0], p[1] - GUNS.barrel, GUNS.height]) for p in GUNS.pivots]
        self._gun = Cadence(GUNS.fireInterval, GUNS.firstShot)
        self._due = [0 for _p in GUNS.pivots]

    def update(self, ctx: EnemyContext, dt: float) -> None:
        """Advance the enemy by `dt` seconds."""
        self.y -= CFG.speed * dt
        if on_playfield(self, ctx):
            self._turrets(ctx, dt)
        if not on_playfield(self, ctx) or self.y < CFG.lastLaunchFraction * ctx.height:
            self.charge = 0
            self._move_bays(INFINITY)
            return
        _count = self._launcher.tick(dt)
        for _i in range(_count):
            self._launch(ctx)
        self.charge = self._launcher.progress
        self._move_bays((1 - self._launcher.progress) * CFG.launchInterval)

    def _turrets(self, ctx: EnemyContext, dt: float) -> None:
        """Turn each turret towards the player, and fire the shot it owes once it points at them."""
        shots = self._gun.tick(dt * ctx.fire_rate)
        for k, turret in enumerate(self.turrets):
            # One shot owed at most: a turret slow to come round does not fire a burst.
            self._due[k] = min(1, self._due[k] + shots)
            pivot = ctx.seen(self.place((turret.spec.x, turret.spec.y, GUNS.height)))
            target = heading_to(pivot.x, pivot.y, ctx.player_x, ctx.player_y)
            rate = turret.spec.turn_rate_deg * DEG * dt
            turret.aim = wrap_angle(turn_towards(turret.aim, target - self.heading, rate))
            own = self.heading + turret.aim
            if self._due[k] <= 0 or abs(wrap_angle(own - target)) > AIMED:
                continue
            barrel = self.barrels[k]
            tip = ctx.seen(self.place(turret.turned(barrel.muzzle)))
            barrel.kick(self.age)
            ctx.fire_bullet(tip.x, tip.y, own, GUNS.bullet)
            self._due[k] -= 1

    def _move_bays(self, next_launch: float) -> None:
        """Set the doors and the Wasps' lifts, `next_launch` seconds before the next launch."""
        doors = CFG.doors
        since = INFINITY if self._launched_at is None else self.age - self._launched_at
        closing = since - doors.closeDelay
        if closing < doors.seconds:
            # The Wasps just left: the doors stay open a moment, then close over an empty bay.
            opened = 1 - ramp(closing, doors.seconds)
            lift = -1.0
        else:
            # The next Wasp is loaded under the closed doors; they open, then it rises.
            opened = ramp(doors.openLead - next_launch, doors.seconds)
            lift = ramp(doors.openLead - doors.seconds - next_launch, doors.riseSeconds)
        bays = len(CFG.bays)
        for k in range(bays):
            self.tracks[k] = opened
            self.tracks[bays + k] = lift

    def _launch(self, ctx: EnemyContext) -> None:
        """Each bay's Wasp takes off from the deck, flying down to its pause."""
        for bay in CFG.bays:
            at = ctx.seen(self.place((bay[0], bay[1], 0)))
            ctx.spawn(Wasp(at.x, at.y, at.y - CFG.launchDrop))
        self._launched_at = self.age
