"""Enemies with moving parts (P05-R13), ported from `core/entities/jointed-enemy.ts`.

Parts hang on swinging joints (as a boss's limbs, D-061) or orbit the hull, each with its own hit
circle, health and guns. A destroyed part blows up and stops; the enemy goes with its hull, taking
its parts with it.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.entities.boss_joint import BossJoints
from core.entities.enemy import Enemy
from core.entities.muzzle import PlanePoint, muzzle_point

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from core.entities.boss_joint import BossJointSpec  # noqa: E402
from core.entities.enemy import EnemyContext, EnemyStats  # noqa: E402
from core.entities.muzzle import Muzzle, RaisedPoint  # noqa: E402
from core.entities.shot_target import ShotTarget  # noqa: E402

__pragma__("noskip")

INFINITY = float("Infinity")


class EnemyPartSpec:
    """A part of a `JointedEnemy`."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        id: str,
        x: float,
        y: float,
        radius: float,
        health: float,
        joint: str | None = None,
        orbits: bool = False,
        aim: float = 0,
        shields: bool = False,
    ) -> None:
        """`x` and `y` are its centre, from the enemy's centre, as drawn facing down at rest (X
        right, Y up). `joint` is the joint it hangs on, if any: it moves with it. `orbits`: whether
        it turns around the centre with the enemy's `spin` (it cannot hang on a joint). `aim` is in
        radians, clockwise on screen, from the enemy's nose to the way the part points at rest.
        `shields`: whether the hull cannot be hit while it stands (a shield, as a boss's, P07-R01).
        """
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.health = health
        self.joint = joint
        self.orbits = orbits
        self.aim = aim
        self.shields = shields


class JointedDesign:
    """How a `JointedEnemy` is built: its parts and the joints they hang on."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        parts: list[EnemyPartSpec],
        joints: dict[str, BossJointSpec] | None = None,
    ) -> None:
        self.parts = parts
        self.joints = joints


class EnemyPart:
    """A destroyable part of a `JointedEnemy`, where it is now. It is a `DropSource` and a
    `LaserOwner`.
    """

    # Parts never drop a bonus (P05-R13).
    drop_chance = 0
    # Parts have no points of their own (none scored when destroyed).
    points = None

    def __init__(self, spec: EnemyPartSpec, index: int, owner: "JointedEnemy") -> None:
        self.spec = spec
        self.index = index
        self._owner = owner
        self.x = 0.0
        self.y = 0.0
        # The way it points now (radians from +Y, clockwise): its guns fire along it.
        self.heading = math.pi
        # Seconds since it last took damage (for the hit flash); infinity before.
        self.since_hit = INFINITY
        # Set once its destruction was handled (it blew up).
        self.broken = False
        self.radius = spec.radius
        self.max_health = spec.health
        self._health = spec.health

    @property
    def id(self) -> int:
        """Unique among the world's targets: below 0, apart from every enemy's id."""
        return -(self._owner.id * 64 + self.index + 1)

    @property
    def health(self) -> float:
        return self._health

    @health.setter
    def health(self, value: float) -> None:
        next_health = max(0, value)
        if next_health < self._health:
            self.since_hit = 0
        self._health = next_health

    @property
    def destroyed(self) -> bool:
        return self._health <= 0

    @property
    def gone(self) -> bool:
        return self._owner.gone or self.destroyed

    @property
    def emitter(self) -> PlanePoint:
        """Lasers leave one radius ahead of its centre, along its heading."""
        return PlanePoint(
            self.x + math.sin(self.heading) * self.radius,
            self.y + math.cos(self.heading) * self.radius,
        )

    def place(self, muzzle: Muzzle) -> RaisedPoint:
        """Where `muzzle` (from the enemy's centre, as drawn facing down at rest) is now: moved by
        the joint the part hangs on, or turned by the spin if it orbits, then with the enemy's nose.
        """
        x, y = self._owner.joints.move(self.spec.joint, muzzle[0], muzzle[1])
        moved: Muzzle = (x, y, muzzle[2])
        return muzzle_point(self._owner, moved, self._owner.spin if self.spec.orbits else 0)

    def destroy(self) -> None:
        """Destroys it at once (its enemy's death)."""
        self._health = 0


class JointedEnemy(Enemy):
    """Base of the enemies with moving parts (P05-R13). Each step swings the joints, runs the
    kind's `act`, then puts the parts where they are now; parts the player destroyed blow up.
    """

    def __init__(self, x: float, y: float, stats: EnemyStats, design: JointedDesign) -> None:
        super().__init__(x, y, stats)
        # Radians, clockwise on screen, the orbiting parts are turned by.
        self.spin = 0.0
        # Whether the joints swing on; a kind holds them still while this is false.
        self.swinging = True
        self._specs: dict[str, BossJointSpec] = design.joints if design.joints is not None else {}
        self.joints = BossJoints(self._specs, design.parts)
        self.parts = [EnemyPart(spec, i, self) for i, spec in enumerate(design.parts)]
        self._place_parts()

    def part(self, id: str) -> EnemyPart | None:
        """Its part `id`, if it is still there."""
        for part in self.parts:
            if part.spec.id == id and not part.destroyed:
                return part
        return None

    @property
    def shielded(self) -> bool:
        """Whether a standing part shields the hull."""
        return any([part.spec.shields and not part.destroyed for part in self.parts])

    def _hit_targets(self) -> list[ShotTarget]:
        """The hull and its standing parts: what shots hit and the player can bump into."""
        targets: list[ShotTarget] = [self]
        for part in self.parts:
            if not part.destroyed:
                targets.append(part)
        return targets

    def _shot_targets(self) -> list[ShotTarget]:
        """Shots pass through a shielded hull (as a boss's core, P07-R01)."""
        targets = self.hit_targets
        if self.shielded:
            return [target for target in targets if target is not self]
        return targets

    def update(self, ctx: EnemyContext, dt: float) -> None:
        self._break_destroyed(ctx)
        if self.swinging:
            self.joints.step(dt)
        self.act(ctx, dt)
        self._place_parts()

    def act(self, ctx: EnemyContext, dt: float) -> None:
        """Moves and attacks for `dt` seconds, as `Enemy.update`; the parts are placed after.
        Abstract.
        """
        raise NotImplementedError

    def on_destroyed(self, ctx: EnemyContext) -> None:
        """Its death blows up every part still on it."""
        for part in self.parts:
            if part.broken:
                continue
            part.destroy()
            part.broken = True
            ctx.break_part(part)

    def _turn(self, joint_id: str | None) -> float:
        """How far joint `joint_id` and those it hangs on are turned now, in all."""
        angle = 0.0
        j = joint_id
        while j is not None:
            angle += self.joints.angle(j)
            spec = self._specs.get(j)
            j = spec.parent if spec is not None else None
        return angle

    def _place_parts(self) -> None:
        for part in self.parts:
            spec = part.spec
            at = part.place((spec.x, spec.y, 0))
            part.x = at.x
            part.y = at.y
            turn = self.spin if spec.orbits else self._turn(spec.joint)
            part.heading = self.heading + spec.aim + turn

    def _break_destroyed(self, ctx: EnemyContext) -> None:
        for part in self.parts:
            if not part.destroyed or part.broken:
                continue
            part.broken = True
            ctx.break_part(part)
