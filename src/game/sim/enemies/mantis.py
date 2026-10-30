"""The Mantis (P05-R16)"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.entities.boss_joint import BossJointSpec, JointSwing
from core.entities.jointed_enemy import EnemyPartSpec, JointedDesign, JointedEnemy
from core.systems.gun_muzzles import GunMuzzles, fire_aimed
from game.config.enemies_veteran import VETERAN_CONFIG
from game.sim.enemies.enemy_helpers import DEG, DOWN, Cadence, bullet_shot, on_playfield

__pragma__("skip")
from core.entities.enemy import EnemyContext  # noqa: E402
from core.entities.muzzle import Muzzle  # noqa: E402

__pragma__("noskip")

CFG = VETERAN_CONFIG.mantis
ARM = CFG.arm

# Slowest speed while braking to its stop, px/s.
CREEP = 20


def _side_name(s: int) -> str:
    """The name of the arm on the side `s` (-1 left, 1 right)."""
    return "left" if s == -1 else "right"


def _arm_design(s: int) -> tuple[str, BossJointSpec, EnemyPartSpec]:
    """The arm on the side `s` (1 right, -1 left): its shoulder joint and its blade."""
    side = _side_name(s)
    out = s * ARM.outDeg * DEG
    sx = s * CFG.shoulder[0]
    sy = CFG.shoulder[1]
    # Out of step: the right arm a quarter swing behind the left one.
    phase = 0.25 if s == 1 else 0
    swing = JointSwing(ARM.swing.amplitudeDeg, ARM.swing.period, phase)
    joint = BossJointSpec(sx, sy, swing)
    part = EnemyPartSpec(
        side + "-arm",
        sx + math.sin(out) * ARM.centre,
        sy - math.cos(out) * ARM.centre,
        ARM.radius,
        ARM.health,
        side + "-shoulder",
        False,
        # Clockwise on screen from its nose: turned out to its side.
        -out,
    )
    return (side + "-shoulder", joint, part)


def _mantis_design() -> JointedDesign:
    joints: dict[str, BossJointSpec] = {}
    parts: list[EnemyPartSpec] = []
    for s in (-1, 1):
        joint_name, joint, part = _arm_design(s)
        joints[joint_name] = joint
        parts.append(part)
    return JointedDesign(parts, joints)


MANTIS_DESIGN = _mantis_design()


class Mantis(JointedEnemy):
    """P05-R16: an insect-like hull with two scythe arms (moving parts, P05-R13) swinging out and
    in, out of step. It comes down to the upper half, stops for 6 s, then leaves downward. While
    it is stopped, each standing arm fires a pair of bullets straight along its blade every 1.2 s,
    so its shots sweep as the arm swings; its head fires a bullet aimed at the player every 2 s.
    """

    def __init__(self, x: float, y: float, stop_y: float) -> None:
        super().__init__(x, y, CFG.stats, MANTIS_DESIGN)
        self.stop_y = stop_y
        self.state = "enter"
        self._arms = Cadence(ARM.fireInterval, ARM.fireInterval / 2)
        self._head = Cadence(CFG.head.fireInterval, CFG.head.firstShot)
        self._head_muzzles = GunMuzzles(CFG.head.muzzles)
        self._stayed = 0.0
        self.heading = DOWN

    def act(self, ctx: EnemyContext, dt: float) -> None:
        if self.state == "enter":
            self._enter(dt)
        elif self.state == "stay":
            self._stay(ctx, dt)
        else:
            self.y -= CFG.exitSpeed * dt
        if on_playfield(self, ctx):
            self._fire_head(ctx, dt)

    def _enter(self, dt: float) -> None:
        left = self.y - self.stop_y
        speed = max(CREEP, CFG.entrySpeed * min(1, left / CFG.brakeDistance))
        self.y = max(self.stop_y, self.y - speed * dt)
        if self.y == self.stop_y:
            self.state = "stay"

    def _stay(self, ctx: EnemyContext, dt: float) -> None:
        self._stayed += dt
        _count = self._arms.tick(dt * ctx.fire_rate)
        for _i in range(_count):
            for s in (-1, 1):
                self._fire_arm(ctx, s)
        self.charge = self._arms.progress
        if self._stayed < CFG.stay:
            return
        self.state = "exit"
        self.charge = 0

    def _fire_arm(self, ctx: EnemyContext, s: int) -> None:
        """The arm on side `s` fires its pair straight along its blade, if it still stands."""
        arm = self.part(_side_name(s) + "-arm")
        if arm is None:
            return
        muzzles: list[Muzzle] = ARM.muzzles[_side_name(s)]
        for muzzle in muzzles:
            point = ctx.seen(arm.place(muzzle))
            ctx.fire_bullet(point.x, point.y, arm.heading, ARM.bullet)

    def _fire_head(self, ctx: EnemyContext, dt: float) -> None:
        _count = self._head.tick(dt * ctx.fire_rate)
        for _i in range(_count):
            fire_aimed(
                ctx,
                self._head_muzzles,
                self,
                (1, 0),
                bullet_shot(ctx, CFG.head.bullet),
            )
