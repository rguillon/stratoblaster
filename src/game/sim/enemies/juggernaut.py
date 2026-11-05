# Copyright (c) 2026 Renaud Guillon
"""The Juggernaut (`specs/enemies/juggernaut.md`)."""

import math

from core.entities.barrel import Barrel
from core.entities.boss_turret import BossTurret, BossTurretSpec
from core.entities.jointed_enemy import JointedEnemy
from core.systems.enemy_motion import approach
from core.systems.gun_muzzles import GunMuzzles
from core.systems.projectile_motion import heading_to, turn_towards, wrap_angle
from game.config.enemies_elite import ELITE_CONFIG
from game.sim.enemies.enemy_helpers import DEG, DOWN, Cadence, on_playfield
from game.sim.joints import jointed_design

# isort: split
# __pragma__ ("skip")
from core.entities.enemy import EnemyContext

# __pragma__ ("noskip")


CFG = ELITE_CONFIG.juggernaut


class Juggernaut(JointedEnemy):
    """ENM-JUGGERNAUT-08: an armoured brute.

    It comes down slowly to the upper third, drifts left and right for 10 s, then leaves downward.
    Its two shoulder cannons swing to and fro (ENM-JUGGERNAUT-09; moving parts, ENM-27), each firing
    a burst of 3 bullets along its barrel every 1.6 s (ENM-JUGGERNAUT-10); its two front plates are
    parts too, and while one stands the core cannot be hit (a shield, as a boss's,
    ENM-JUGGERNAUT-12). The back turret fires a spread of 7 bullets 9° apart centred on the player
    every 2.5 s (ENM-JUGGERNAUT-11): its seven parallel barrels fire one after the other as it
    sweeps across the spread, each bullet along the turret's heading at that instant (WPN-01,
    WPN-02); its charge lights follow it (ENM-JUGGERNAUT-04). Its cannons
    and plates come from its config, as the engine's specs (ENM-JUGGERNAUT-15).
    """

    def __init__(self, center_x: float, y: float, stop_y: float) -> None:
        super().__init__(center_x, y, CFG.stats, jointed_design(CFG.design))
        self.center_x = center_x
        self.stop_y = stop_y
        self.state = "enter"
        self._gun = Cadence(CFG.fireInterval, CFG.firstShot)
        self._muzzles = GunMuzzles(CFG.muzzles, True)
        self.turret = BossTurret(BossTurretSpec(CFG.turret.x, CFG.turret.y, CFG.turret.turnDeg))
        # The spread being swept: its bullets' headings relative to the nose, the next one's
        # number (None when no sweep is under way), and seconds until a barrel may fire again.
        self._sweep: list[float] = []
        self._sweep_next: int | None = None
        self._sweep_clock = 0.0
        # The back turret's seven barrels, then one per shoulder cannon (WPN-03).
        self.barrels = list(self._muzzles.barrels)
        for c in CFG.cannons:
            self.barrels.append(Barrel(c.muzzle))
        self._cannons = Cadence(CFG.cannonInterval, CFG.firstBurst)
        # Bullets left in the cannons' burst, and seconds until the next one.
        self._burst_left = 0
        self._burst_clock = 0.0
        self._drift_for = 0.0
        self.heading = DOWN

    def act(self, ctx: EnemyContext, dt: float) -> None:
        """Advance the enemy by `dt` seconds."""
        if self.state == "enter":
            self.y = approach(self.y, self.stop_y, CFG.entrySpeed * dt)
            if self.y == self.stop_y:
                self.state = "drift"
        elif self.state == "drift":
            self._drift_for += dt
            self.x = self.center_x + CFG.drift * math.sin(
                (2 * math.pi * self._drift_for) / CFG.driftPeriod
            )
            if self._drift_for >= CFG.stay:
                self.state = "exit"
        else:
            self.y -= CFG.exitSpeed * dt
        if on_playfield(self, ctx):
            self._fire(ctx, dt * ctx.fire_rate)

    def _fire(self, ctx: EnemyContext, dt: float) -> None:
        if self._gun.tick(dt) > 0 and self._sweep_next is None:
            self._start_sweep(ctx)
        self._turn_turret(ctx, dt)
        self.charge = self._gun.progress
        if self._cannons.tick(dt) > 0:
            self._burst_left = CFG.burstCount
            self._burst_clock = 0.0
        self._burst_clock -= dt
        while self._burst_left > 0 and self._burst_clock <= 0:
            self._fire_cannons(ctx)
            self._burst_left -= 1
            self._burst_clock += CFG.burstGap

    def _start_sweep(self, ctx: EnemyContext) -> None:
        """Set the spread's headings, centred on the player now, for the turret to sweep."""
        centre = wrap_angle(heading_to(self.x, self.y, ctx.player_x, ctx.player_y) - self.heading)
        spacing = CFG.spreadSpacing * DEG
        half = (CFG.spreadCount - 1) / 2
        # It starts from the side the turret is already nearest.
        side = 1 if self.turret is not None and wrap_angle(self.turret.aim - centre) > 0 else -1
        self._sweep = [centre + side * (half - k) * spacing for k in range(CFG.spreadCount)]
        self._sweep_next = 0
        self._sweep_clock = 0.0

    def _turn_turret(self, ctx: EnemyContext, dt: float) -> None:
        """Turn the turret: across the spread while one is swept, else towards the player.

        A barrel fires as the turret reaches its bullet's heading, `sweepGap` after the last one.
        """
        turret = self.turret
        if turret is None:
            return
        step = turret.spec.turn_rate_deg * DEG * dt
        self._sweep_clock -= dt
        if self._sweep_next is None:
            aim = heading_to(self.x, self.y, ctx.player_x, ctx.player_y) - self.heading
            turret.aim = turn_towards(turret.aim, aim, step)
            return
        target = self._sweep[self._sweep_next]
        turret.aim = turn_towards(turret.aim, target, step)
        if abs(wrap_angle(turret.aim - target)) > 1e-9 or self._sweep_clock > 0:
            return
        barrel = self.barrels[self._sweep_next]
        tip = ctx.seen(self.place(barrel.muzzle, True))
        barrel.kick(self.age)
        ctx.fire_bullet(tip.x, tip.y, self.heading + turret.aim, CFG.bullet)
        self._sweep_clock = CFG.sweepGap
        self._sweep_next += 1
        if self._sweep_next >= len(self._sweep):
            self._sweep_next = None

    def _fire_cannons(self, ctx: EnemyContext) -> None:
        """Each standing shoulder cannon fires a bullet along its barrel."""
        for k, spec in enumerate(CFG.cannons):
            cannon = self.part(spec.id)
            if cannon is None:
                continue
            point = ctx.seen(cannon.place(spec.muzzle))
            # Along the barrel as its joint is turned now (the part's heading is set after `act`).
            heading = self.heading + self.joints.angle(spec.joint)
            self.barrels[len(CFG.muzzles) + k].kick(self.age)
            ctx.fire_bullet(point.x, point.y, heading, CFG.cannonBullet)
