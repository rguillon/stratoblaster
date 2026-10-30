"""Bosses (P07), ported from `core/entities/boss.ts`.

Bosses are big enemies made of a core and destroyable parts (GD-46). Positions are playfield
logical pixels, X to the right, Y up. A boss faces down the screen and does not turn: its parts
keep their offsets from its centre, unless they hang on one of its joints.

Subclasses override the hooks `_hit_targets` and `_shot_targets`, never the properties.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.entities.boss_joint import BossJoints
from core.entities.boss_pieces import BossCore, BossPart
from core.entities.boss_roll import roll_towards
from core.entities.enemy import Enemy, EnemyStats

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Literal  # noqa: E402

from core.entities.boss_joint import BossJointSpec  # noqa: E402
from core.entities.boss_roll import BossRoll  # noqa: E402
from core.entities.boss_turret import BossTurretSpec  # noqa: E402
from core.entities.enemy import EnemyContext  # noqa: E402
from core.entities.shot_target import ShotTarget  # noqa: E402

BossState = Literal["entering", "fighting", "dying"]

__pragma__("noskip")


class BossPartSpec:
    """A destroyable part of a boss (P07-R01): a turret, a pod, an armour plate..."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        id: str,
        x: float,
        y: float,
        radius: float,
        health: float,
        shields_core: bool,
        drop_chance: float,
        orbits: bool = False,
        joint: str | None = None,
    ) -> None:
        """`x` and `y` are its offset from the boss's centre (X right, Y up). `shields_core`: while
        this part is there, the core takes no damage. `drop_chance` is the chance (0..1) that it
        drops a bonus when the player destroys it (P07-R07). `orbits`: whether it turns around the
        boss's centre with `BossStats.spin` (e.g. on a turning ring). `joint`: the joint it hangs on
        (phase 7 review): it moves with it, see `BossStats.joints`.
        """
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.health = health
        self.shields_core = shields_core
        self.drop_chance = drop_chance
        self.orbits = orbits
        self.joint = joint


class BossDeath:
    """A boss's death (P07-R06): a blast every `every` seconds over its hull for `seconds`."""

    def __init__(self, seconds: float, every: float) -> None:
        if not every > 0:
            raise ValueError("A boss's death blasts need a positive interval")
        self.seconds = seconds
        self.every = every


class BossStats(EnemyStats):
    """Fixed numbers of a boss. `health` is its core's, `radius` the size of the whole boss."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        model: str,
        radius: float,
        health: float,
        points: float,
        name: str,
        core_radius: float,
        parts: list[BossPartSpec],
        ground_speed: float,
        stage_pause: float,
        death: BossDeath,
        rage_seconds: float | None = None,
        core_drop_chance: float | None = None,
        part_points: float | None = None,
        roll: BossRoll | None = None,
        turrets: dict[str, BossTurretSpec] | None = None,
        joints: dict[str, BossJointSpec] | None = None,
    ) -> None:
        """The optional fields come last, as in the TypeScript:

        - `core_radius`: hit radius of the core.
        - `ground_speed`: factor on the level's ground speed while it is fought (P07-R03).
        - `stage_pause`: seconds it does not fire after one of its parts is destroyed (P07-R04).
        - `rage_seconds`: seconds it is angry after that pause (phase 7 review): it fires its
          angry pattern (`Boss.update_rage`) instead of its stage's. Never angry when None.
        - `core_drop_chance`: chance its core drops a bonus when destroyed; the game's rule when
          None.
        - `part_points`: points scored for each of its parts the player destroys (P11-R01); none
          when None.
        - `roll`: it rolls into its sideways moves (phase 7 review); it does not roll when None.
        - `turrets`: the turrets of its pieces, by part id (`core` for the core's).
        - `joints`: its moving limbs' joints, by id (phase 7 review).
        """
        super().__init__(model, radius, health, points)
        self.name = name
        self.core_radius = core_radius
        self.parts = parts
        self.ground_speed = ground_speed
        self.stage_pause = stage_pause
        self.death = death
        self.rage_seconds = rage_seconds
        self.core_drop_chance = core_drop_chance
        self.part_points = part_points
        self.roll = roll
        self.turrets = turrets
        self.joints = joints


class Boss(Enemy):
    """Base of every boss (P07-R01, R04, GD-46): a core and destroyable parts that the player's
    shots hit one by one. It goes through stages, one more each time a part is destroyed, pausing
    its fire for `stage_pause` at each; it blows up over `death.seconds` once its core has no health
    left; after each pause it may be angry for `rage_seconds`. Concrete bosses (in the game) say how
    they come in (`enter`), move (`move`), fire (`update_pattern`) and fire when angry
    (`update_rage`, optional: set it in the subclass); they may react to a new stage
    (`on_stage_change`, optional).

    Its `health` (as an `Enemy`) only says whether it is still there: it drops to 0 when its death
    blasts are over, and the enemy world then removes it as destroyed.
    """

    expires = False
    rammable = False
    # Optional hooks; a subclass defines them as methods to enable them.
    update_rage: Callable[[EnemyContext, float], None] | None = None
    on_stage_change: Callable[[int, EnemyContext], None] | None = None

    def __init__(self, x: float, y: float, stats: BossStats) -> None:
        super().__init__(x, y, stats)
        self.stats = stats
        self.heading = math.pi
        self.name = stats.name
        self.ground_speed = stats.ground_speed
        self.drop_chance = stats.core_drop_chance
        self.state: BossState = "entering"
        # Number of parts destroyed so far (P07-R04).
        self.stage = 0
        # Seconds left without firing, after a stage change.
        self.pause = 0.0
        # Seconds left being angry, once the pause after a stage change is over (phase 7 review).
        self.rage = 0.0
        # How far its orbiting parts have turned, in radians, clockwise on screen.
        self.spin = 0.0
        # How far it is rolled into its sideways move, in radians (see `MuzzleBody.roll`).
        self.roll = 0.0
        # Its moving limbs (phase 7 review), swinging all the time it is there.
        self.joints = BossJoints(stats.joints, stats.parts)
        self._last_x = x
        self._core_health = stats.health
        self._dying_for = 0.0
        self._blasts = 0
        self._targets: list[ShotTarget] = []
        self._intact_parts: list[ShotTarget] = []
        self.parts = [BossPart(spec, i, self) for i, spec in enumerate(stats.parts)]
        self.core = BossCore(self)
        self._place()
        self._rebuild_targets()

    @property
    def vulnerable(self) -> bool:
        """Whether shots damage it: once it is in place, until it blows up."""
        return self.state == "fighting"

    @property
    def core_shielded(self) -> bool:
        """Whether some part that shields the core is still there."""
        return any([part.shields_core and not part.destroyed for part in self.parts])

    @property
    def core_health(self) -> float:
        return 0 if self.state == "dying" else self._core_health

    @property
    def full_health(self) -> float:
        """Health of the core and every part when it arrives (its health bar's full length)."""
        total = self.stats.health
        for part in self.parts:
            total += part.max_health
        return total

    @property
    def remaining_health(self) -> float:
        """Health of the core and the parts left."""
        total = self.core_health
        for part in self.parts:
            total += part.health
        return total

    def _hit_targets(self) -> list[ShotTarget]:
        """Its intact parts and its core, until it blows up."""
        return self._targets

    def _shot_targets(self) -> list[ShotTarget]:
        """Its intact parts, and its core unless it is fighting with its core shielded (phase 7
        review): shots then go through the core to the parts behind it. Coming in, shots spark on
        all of it (P07-R05).
        """
        if self.vulnerable and self.core_shielded:
            return self._intact_parts
        return self._targets

    def hurt_core(self, value: float) -> None:
        """Sets the core's health; at 0 the boss starts blowing up. Used by its `core`."""
        if value > 0:
            self._core_health = value
        else:
            self._start_dying()

    def break_next(self) -> None:
        """Destroys its next intact part, or its core once they are all gone (debug, P07-R09)."""
        if self.state == "dying":
            return
        for part in self.parts:
            if not part.destroyed:
                part.destroy()
                return
        self._start_dying()

    def update(self, ctx: EnemyContext, dt: float) -> None:
        self.core.since_hit += dt
        for part in self.parts:
            part.since_hit += dt
        self.joints.step(dt)
        if self.state == "dying":
            self._die(ctx, dt)
            return
        self._break_parts(ctx)
        if self.state == "entering":
            if self.enter(ctx, dt):
                self.state = "fighting"
        else:
            self.move(ctx, dt)
        self._place()
        self._roll(dt)
        if self.state != "fighting" or self.pause > 0:
            self.pause = max(0, self.pause - dt)
            self.charge = 0
            return
        if self.rage > 0 and self.update_rage is not None:
            self.rage = max(0, self.rage - dt)
            self.update_rage(ctx, dt)
            return
        self.update_pattern(ctx, dt)

    def enter(self, ctx: EnemyContext, dt: float) -> bool:
        """Comes in for `dt` seconds; returns True once in place (it can then be damaged).
        Abstract.
        """
        raise NotImplementedError

    def move(self, ctx: EnemyContext, dt: float) -> None:
        """Moves for `dt` seconds once in place. Abstract."""
        raise NotImplementedError

    def update_pattern(self, ctx: EnemyContext, dt: float) -> None:
        """Fires the pattern of the current stage for `dt` seconds (not during a pause).
        Abstract.
        """
        raise NotImplementedError

    def _break_parts(self, ctx: EnemyContext) -> None:
        """Takes the parts destroyed since the last step into account: a stage more for each."""
        changed = False
        for part in self.parts:
            if not part.destroyed or part.broken:
                continue
            part.broken = True
            changed = True
            self.stage += 1
            self.pause = self.stats.stage_pause
            self.rage = self.stats.rage_seconds if self.stats.rage_seconds is not None else 0
            ctx.break_part(part)
            if self.on_stage_change is not None:
                self.on_stage_change(self.stage, ctx)
        if changed:
            self._rebuild_targets()

    def _start_dying(self) -> None:
        self.state = "dying"
        self._core_health = 0
        self.charge = 0
        self.rage = 0
        for part in self.parts:
            part.destroy()
            part.broken = True
        self._targets = []
        self._intact_parts = []

    def _die(self, ctx: EnemyContext, dt: float) -> None:
        """Blasts over the hull, one by one, then it is destroyed (its last, big blast)."""
        seconds = self.stats.death.seconds
        every = self.stats.death.every
        self._dying_for += dt
        while self._blasts * every <= min(self._dying_for, seconds):
            index = self._blasts % max(1, len(self.parts))
            part = self.parts[index] if index < len(self.parts) else None
            spread = (part.radius if part is not None else self.stats.core_radius) * 0.6
            if part is not None:
                x, y = part.x, part.y
            else:
                x, y = self.x, self.y
            blast_x = x + (ctx.random() * 2 - 1) * spread
            blast_y = y + (ctx.random() * 2 - 1) * spread
            ctx.explode(
                blast_x,
                blast_y,
                part.radius if part is not None else self.stats.core_radius,
            )
            self._blasts += 1
        if self._dying_for >= seconds:
            self.health = 0

    def _roll(self, dt: float) -> None:
        """Rolls into its move across the screen since the last step, easing in and out."""
        rule = self.stats.roll
        vx = (self.x - self._last_x) / dt if dt > 0 else 0
        self._last_x = self.x
        if rule is not None and dt > 0:
            self.roll = roll_towards(rule, self.roll, vx, dt)

    def _place(self) -> None:
        c, s = math.cos(self.spin), math.sin(self.spin)
        for part in self.parts:
            orbits = part.spec.orbits
            x, y = self.joints.move(part.spec.joint, part.spec.x, part.spec.y)
            # Clockwise on screen (X right, Y up) by `spin` for the orbiting ones.
            part.x = self.x + (x * c + y * s if orbits else x)
            part.y = self.y + (-x * s + y * c if orbits else y)

    def _rebuild_targets(self) -> None:
        self._intact_parts = [part for part in self.parts if not part.destroyed]
        targets: list[ShotTarget] = list(self._intact_parts)
        targets.append(self.core)
        self._targets = targets
