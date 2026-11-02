# Copyright (c) 2026 Renaud Guillon
"""Bosses (BOSS-07).

Bosses are big enemies made of a core and destroyable parts (BOSS-12). Positions are playfield
logical pixels, X to the right, Y up. A boss faces down the screen and does not turn: its parts
keep their offsets from its centre, unless they hang on one of its joints.

Subclasses override the hooks `_hit_targets` and `_shot_targets`, never the properties.
"""

import math

from core.entities.boss_joint import BossJoints
from core.entities.boss_pieces import BossCore, BossPart
from core.entities.boss_roll import roll_towards
from core.entities.enemy import Enemy, EnemyStats

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from collections.abc import Callable
from typing import Literal

from core.entities.boss_joint import BossJointSpec
from core.entities.boss_roll import BossRoll
from core.entities.boss_turret import BossTurretSpec
from core.entities.enemy import EnemyContext
from core.entities.shot_target import ShotTarget

BossState = Literal["entering", "fighting", "transforming", "dying"]
# __pragma__ ("noskip")


class BossPartSpec:
    """A destroyable part of a boss (BOSS-12): a turret, a pod, an armour plate..."""

    def __init__(
        self,
        id_: str,
        x: float,
        y: float,
        radius: float,
        health: float,
        shields_core: bool,
        drop_chance: float,
        orbits: bool = False,
        joint: str | None = None,
        reveal: int | None = None,
        retire: int | None = None,
    ) -> None:
        """`x` and `y` are its offset from the boss's centre (X right, Y up).

        `shields_core`: while this part is there, the core takes no damage. `drop_chance` is the
        chance (0..1) that it drops a bonus when the player destroys it (BOSS-57). `orbits`: whether
        it turns around the boss's centre with `BossStats.spin` (e.g. on a turning ring). `joint`:
        the joint it hangs on (phase 7 review): it moves with it, see `BossStats.joints`. `reveal`:
        the transformation that reveals it (1 for the first); hidden until then, it cannot be hit,
        does not shield the core and does not fire (BOSS-38). None for a part there from the start.
        `retire`: the transformation it leaves the fight at (D-228: another part takes over from
        it), from the moment it starts: hidden from then on, it is not destroyed (the boss's stage
        does not change) and no longer counts in its health. None for a part there to the end.
        """
        self.id = id_
        self.x = x
        self.y = y
        self.radius = radius
        self.health = health
        self.shields_core = shields_core
        self.drop_chance = drop_chance
        self.orbits = orbits
        self.joint = joint
        self.reveal = reveal
        self.retire = retire


class BossDeath:
    """A boss's death (BOSS-19): a blast every `every` seconds over its hull for `seconds`."""

    def __init__(self, seconds: float, every: float) -> None:
        if not every > 0:
            msg = "A boss's death blasts need a positive interval"
            raise ValueError(msg)
        self.seconds = seconds
        self.every = every


class BossStats(EnemyStats):
    """Fixed numbers of a boss. `health` is its core's, `radius` the size of the whole boss."""

    def __init__(
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
        transforms: list[int] | None = None,
        transform_seconds: float = 1.5,
        transform_parts: list[list[str]] | None = None,
        turns: list[float] | None = None,
    ) -> None:
        """Set the boss's fixed numbers; the optional fields come last.

        - `core_radius`: hit radius of the core.
        - `ground_speed`: factor on the level's ground speed while it is fought (BOSS-03).
        - `stage_pause`: seconds it does not fire after one of its parts is destroyed (BOSS-22).
        - `rage_seconds`: seconds it is angry after that pause (BOSS-27): it fires its
          angry pattern (`Boss.update_rage`) instead of its stage's. Never angry when None.
        - `core_drop_chance`: chance its core drops a bonus when destroyed; the game's rule when
          None.
        - `part_points`: points scored for each of its parts the player destroys
          (GAME-SCORE-04); none when None.
        - `roll`: it rolls into its sideways moves (BOSS-11); it does not roll when None.
        - `turrets`: the turrets of its pieces, by part id (`core` for the core's).
        - `joints`: its moving limbs' joints, by id (BOSS-33).
        - `transforms`: how many of its original parts (those not hidden) must be destroyed for
          each of its transformations (BOSS-36), in order (e.g. `[2, 4]`); it never transforms
          when None.
        - `transform_seconds`: how long a transformation lasts: it neither fires nor takes damage
          (BOSS-37).
        - `transform_parts`: for each transformation, the parts (by id) whose destruction calls for
          it, all of them (D-228), in place of `transforms`; None to count parts.
        - `turns`: how far (radians, clockwise on screen) the whole boss turns during each of its
          transformations (D-228), its parts and guns with it; it does not turn when None.
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
        self.transforms = transforms
        self.transform_seconds = transform_seconds
        self.transform_parts = transform_parts
        self.turns = turns


class Boss(Enemy):
    """Base of every boss (BOSS-12, BOSS-20).

    A core and destroyable parts that the player's shots hit one by one. It goes through stages, one
    more each time a part is destroyed, pausing its fire for `stage_pause` at each; it blows up over
    `death.seconds` once its core has no health left; after each pause it may be angry for
    `rage_seconds`. Concrete bosses (in the game) say how they come in (`enter`), move (`move`),
    fire (`update_pattern`) and fire when angry (`update_rage`, optional: set it in the subclass);
    they may react to a new stage (`on_stage_change`, optional).

    Its `health` (as an `Enemy`) only says whether it is still there: it drops to 0 when its death
    blasts are over, and the enemy world then removes it as destroyed.
    """

    # It stays until it is destroyed (BOSS-04) and takes no ramming damage (BOSS-16).
    expires = False
    rammable = False
    # Optional hooks (ENG-148); a subclass defines them as methods to enable them.
    update_rage: Callable[[EnemyContext, float], None] | None = None
    on_stage_change: Callable[[int, EnemyContext], None] | None = None
    # Called as transformation k (1 for the first) starts.
    on_transform: Callable[[int, EnemyContext], None] | None = None

    def __init__(self, x: float, y: float, stats: BossStats) -> None:
        super().__init__(x, y, stats)
        self.stats = stats
        self.heading = math.pi
        self.name = stats.name
        self.ground_speed = stats.ground_speed
        self.drop_chance = stats.core_drop_chance
        self.state: BossState = "entering"
        # Number of parts destroyed so far (BOSS-20).
        self.stage = 0
        # Seconds left without firing, after a stage change.
        self.pause = 0.0
        # Seconds left being angry, once the pause after a stage change is over (phase 7 review).
        self.rage = 0.0
        # How far its orbiting parts have turned, in radians, clockwise on screen.
        self.spin = 0.0
        # How far it is rolled into its sideways move, in radians (see `MuzzleBody.roll`).
        self.roll = 0.0
        # Transformations done (its hidden parts with `reveal` up to it are revealed), and how far
        # the one going on is (0..1; 0 when none is).
        self.form = 0
        self.transform = 0.0
        self._transform_for = 0.0
        # Its heading as its transformation started (it turns from there, D-228).
        self._heading_from = math.pi
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
    def transforming_into(self) -> int:
        """The transformation going on (1 for the first), 0 when none is."""
        return self.form + 1 if self.state == "transforming" else 0

    @property
    def core_shielded(self) -> bool:
        """Whether some part that shields the core is still there (and not hidden, BOSS-14)."""
        return any(
            part.shields_core and not part.destroyed and not part.hidden for part in self.parts
        )

    @property
    def core_health(self) -> float:
        """Health the core has left: 0 once the boss is dying."""
        return 0 if self.state == "dying" else self._core_health

    @property
    def full_health(self) -> float:
        """Health of the core and every part when it arrives.

        This is its health bar's full length (BOSS-54).
        """
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
        """Return its intact parts, and its core unless it is fighting with its core shielded.

        With its core shielded (BOSS-15), shots go through the core to the parts behind it. Coming
        in, shots spark on all of it (BOSS-09).
        """
        if self.vulnerable and self.core_shielded:
            return self._intact_parts
        return self._targets

    def hurt_core(self, value: float) -> None:
        """Set the core's health; at 0 the boss starts blowing up. Used by its `core`."""
        if value > 0:
            self._core_health = value
        else:
            self._start_dying()

    def break_next(self) -> None:
        """Destroys its next intact part, or its core once they are all gone (debug, DEV-OPT-09).

        Hidden parts are skipped; a transformation going on is finished at once, and one it had no
        time for (all its parts broken as it came in) is done at once.
        """
        if self.state == "dying":
            return
        if self.state == "transforming":
            self._end_transform()
            return
        for part in self.parts:
            if not part.destroyed and not part.hidden:
                part.destroy()
                return
        if any(part.hidden and not part.retired for part in self.parts):
            # Its parts all broken before it could transform (coming in): it reveals its next
            # weapons at once.
            self.form += 1
            self._rebuild_targets()
            return
        self._start_dying()

    def update(self, ctx: EnemyContext, dt: float) -> None:
        """Step the boss for `dt` seconds: its joints swing, a dying boss blows up.

        Otherwise its destroyed parts are broken off, it enters or moves, and its parts are placed.
        """
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
                # Parts broken as it came in (a debug key) may call for a transformation.
                self._maybe_transform(ctx)
        else:
            self.move(ctx, dt)
        self._place()
        self._roll(dt)
        if self.state == "transforming":
            self.charge = 0
            self._transforming(ctx, dt)
            return
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
        """Move for `dt` seconds once in place. Abstract."""
        raise NotImplementedError

    def update_pattern(self, ctx: EnemyContext, dt: float) -> None:
        """Fire the pattern of the current stage for `dt` seconds (not during a pause).

        Abstract.
        """
        raise NotImplementedError

    def _break_parts(self, ctx: EnemyContext) -> None:
        """Take the parts destroyed since the last step into account: a stage more for each."""
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
            self._maybe_transform(ctx)

    def _forms_due(self) -> int:
        """How many transformations its destroyed original parts call for."""
        wanted = self.stats.transform_parts
        if wanted is not None:
            destroyed = [p.spec.id for p in self.parts if p.destroyed]
            due = 0
            for ids in wanted:
                if not all(i in destroyed for i in ids):
                    break
                due += 1
            return due
        thresholds = self.stats.transforms
        if thresholds is None:
            return 0
        lost = len([p for p in self.parts if p.spec.reveal is None and p.destroyed])
        return len([t for t in thresholds if lost >= t])

    def _turn_of(self, form: int) -> float:
        """How far it turns during transformation `form` (D-228, BOSS-46)."""
        turns = self.stats.turns
        if turns is None or form > len(turns):
            return 0
        turn: float = turns[form - 1]
        return turn

    def _maybe_transform(self, ctx: EnemyContext) -> None:
        """Start its next transformation if one is due and it is fighting."""
        if self.state != "fighting" or self._forms_due() <= self.form:
            return
        self.state = "transforming"
        self.transform = 0
        self._transform_for = 0
        self._heading_from = self.heading
        self.rage = 0
        # A part retiring at it leaves now (`BossPartSpec.retire`).
        self._rebuild_targets()
        if self.on_transform is not None:
            self.on_transform(self.form + 1, ctx)

    def _transforming(self, ctx: EnemyContext, dt: float) -> None:
        """Goes on with its transformation; once over, it reveals its parts.

        And may start the next one.
        """
        seconds = self.stats.transform_seconds
        self._transform_for += dt
        self.transform = min(1, self._transform_for / seconds) if seconds > 0 else 1
        k = self.transform
        self.heading = self._heading_from + self._turn_of(self.form + 1) * k * k * (3 - 2 * k)
        if self._transform_for >= seconds:
            self._end_transform()
            self._maybe_transform(ctx)

    def _end_transform(self) -> None:
        """Its transformation is over: its parts of that form are revealed, and it is angry."""
        self.heading = self._heading_from + self._turn_of(self.form + 1)
        self.form += 1
        self.transform = 0
        self.state = "fighting"
        self.rage = self.stats.rage_seconds if self.stats.rage_seconds is not None else 0
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
        """Roll into its move across the screen since the last step, easing in and out."""
        rule = self.stats.roll
        vx = (self.x - self._last_x) / dt if dt > 0 else 0
        self._last_x = self.x
        if rule is not None and dt > 0:
            self.roll = roll_towards(rule, self.roll, vx, dt)

    def _place(self) -> None:
        c, s = math.cos(self.spin), math.sin(self.spin)
        # Facing down (heading pi) the offsets are as given; turned, they turn with it (D-228).
        hc, hs = -math.cos(self.heading), -math.sin(self.heading)
        for part in self.parts:
            orbits = part.spec.orbits
            x, y = self.joints.move(part.spec.joint, part.spec.x, part.spec.y)
            # Clockwise on screen (X right, Y up) by `spin` for the orbiting ones (BOSS-34).
            ox = x * c + y * s if orbits else x
            oy = -x * s + y * c if orbits else y
            part.x = self.x + ox * hc + oy * hs
            part.y = self.y - ox * hs + oy * hc

    def _rebuild_targets(self) -> None:
        self._intact_parts = [part for part in self.parts if not part.destroyed and not part.hidden]
        targets: list[ShotTarget] = list(self._intact_parts)
        targets.append(self.core)
        self._targets = targets
