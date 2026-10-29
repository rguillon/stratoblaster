"""Enemies (P05), ported from `core/entities/enemy.ts`.

Positions are playfield logical pixels, X to the right, Y up; headings are in radians from +Y,
positive to the right (pi points straight down, towards the player's side).

Subclasses override the hooks `_hit_targets` and `_shot_targets`, never the `hit_targets` and
`shot_targets` properties: Transcrypt cannot redefine a property in a subclass.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.entities.muzzle import PlanePoint, muzzle_point

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Literal, Protocol  # noqa: E402

from core.entities.muzzle import Muzzle, RaisedPoint  # noqa: E402
from core.entities.shot_target import ShotTarget  # noqa: E402
from core.math.rng import Random  # noqa: E402

EnemySide = Literal["top", "left", "right"]


class LaserOwner(Protocol):
    """What a laser leaves from and follows (an enemy, or a part of a boss): it fires along
    `heading` from `emitter`, and stops once its owner is gone or has no health left.
    """

    @property
    def emitter(self) -> PlanePoint | RaisedPoint: ...

    @property
    def heading(self) -> float: ...

    @property
    def gone(self) -> bool: ...

    @property
    def health(self) -> float: ...


class DropSource(ShotTarget, Protocol):
    """Something destroyed that may drop a bonus: a shot target with, optionally, its own chance
    (0..1) of dropping one instead of the game's rule (P07-R07).
    """

    @property
    def drop_chance(self) -> float | None: ...

    @property
    def points(self) -> float | None: ...


class EnemyContext(Protocol):
    """What an enemy can see and do while it updates."""

    @property
    def width(self) -> float: ...

    @property
    def height(self) -> float: ...

    @property
    def player_x(self) -> float: ...

    @property
    def player_y(self) -> float: ...

    @property
    def random(self) -> Random: ...

    @property
    def fire_rate(self) -> float: ...

    def seen(self, point: RaisedPoint) -> PlanePoint:
        """Where shots must start to look as if they left from `point`, above the playfield."""
        ...

    def fire_bullet(self, x: float, y: float, heading: float, spec: "EnemyBulletSpec") -> None: ...

    def fire_missile(
        self, x: float, y: float, heading: float, spec: "EnemyMissileSpec"
    ) -> None: ...

    def fire_laser(self, owner: LaserOwner, spec: "EnemyLaserSpec") -> None: ...

    def spawn(self, enemy: "Enemy") -> None: ...

    def explode(self, x: float, y: float, radius: float) -> None: ...

    def break_part(self, part: DropSource) -> None: ...


EnemyKindSpawn = Callable[["EnemySpawnArea"], list["Enemy"]]

__pragma__("noskip")


class EnemyBurstSpec:
    """A burst (phase 8): `after` seconds from its firing the bullet is gone, and `count` bullets
    of `bullet` leave from where it was, evenly all around, the first one on its way.
    """

    def __init__(self, after: float, count: int, bullet: "EnemyBulletSpec") -> None:
        self.after = after
        self.count = count
        self.bullet = bullet


class EnemyBulletSpec:
    """A bullet an enemy fires: it flies straight at constant speed."""

    def __init__(
        self,
        speed: float,
        radius: float,
        style: str,
        burst: EnemyBurstSpec | None = None,
    ) -> None:
        """`style` is the look of the bullet, a key the game's enemy shot renderer knows. `burst`
        makes a bullet that bursts (phase 8), when given.
        """
        self.speed = speed
        self.radius = radius
        self.style = style
        self.burst = burst


class EnemyMissileSpec:
    """A missile an enemy launches: it turns towards the player for a while and can be shot
    down.
    """

    def __init__(
        self,
        speed: float,
        turn_rate_deg: float,
        homing_seconds: float,
        radius: float,
        health: float,
        style: str,
    ) -> None:
        """`turn_rate_deg` is in degrees a second; `homing_seconds` is how long it homes on the
        player before it flies straight on.
        """
        self.speed = speed
        self.turn_rate_deg = turn_rate_deg
        self.homing_seconds = homing_seconds
        self.radius = radius
        self.health = health
        self.style = style


class EnemyLaserSpec:
    """A laser an enemy fires straight along its heading: a warning line first, then the beam."""

    def __init__(
        self,
        warning_seconds: float,
        firing_seconds: float,
        width: float,
        style: str,
        sweeps: bool = False,
    ) -> None:
        """`width` is the width of the beam. `sweeps`: whether the beam keeps turning with its
        owner while it fires (P05-R13: lasers on moving parts); otherwise it keeps the heading its
        owner had when it started firing.
        """
        self.warning_seconds = warning_seconds
        self.firing_seconds = firing_seconds
        self.width = width
        self.style = style
        self.sweeps = sweeps


class EnemyStats:
    """Fixed numbers of an enemy kind."""

    def __init__(self, model: str, radius: float, health: float, points: float) -> None:
        """`model` is the key of the enemy's model in the game view; `radius` the hit radius
        (GD-21: about the size of the model); `points` the points scored when it is destroyed
        (GD-50).
        """
        self.model = model
        self.radius = radius
        self.health = health
        self.points = points


class Enemy:
    """Base of every enemy (GD-45): a circle with health that the player's shots can hit, moved
    and armed by `update`. Concrete enemies live in the game; the engine only steps them.
    """

    # Whether the world removes it once it has left the playfield or is too old (a boss stays
    # until it is destroyed).
    expires = True
    # Whether ramming the player hurts it (not a boss, P07-R06).
    rammable = True
    # Called once when the player destroys it, if defined (see JointedEnemy.on_destroyed).
    on_destroyed: Callable[[EnemyContext], None] | None = None

    def __init__(self, x: float, y: float, stats: EnemyStats) -> None:
        self.x = x
        self.y = y
        # Set by the world when the enemy is added.
        self.id = 0
        self.radius = stats.radius
        self.health = stats.health
        self.max_health = stats.health
        self.model = stats.model
        self.points = stats.points
        # Direction the nose points to.
        self.heading = math.pi
        # Seconds since the enemy was added.
        self.age = 0
        # How ready the next attack is, 0..1, for the visuals (e.g. a charging light).
        self.charge: float = 0
        # Set when the enemy is done (left for good); the world then removes it.
        self.gone = False
        # Its own chance of dropping a bonus when destroyed; the game's rule when None.
        self.drop_chance: float | None = None
        self._self_targets: list[ShotTarget] = [self]

    def place(self, muzzle: Muzzle, on_turret: bool = False) -> RaisedPoint:
        """Where `muzzle`, one of its guns' (see `muzzle.py`), is now: it turns with its nose.
        `on_turret` is accepted for `MuzzleSource` but ignored: an enemy has no turret
        (`enemy.ts`' `place` takes only the muzzle, and so does not turn it either).
        """
        return muzzle_point(self, muzzle)

    @property
    def emitter(self) -> PlanePoint | RaisedPoint:
        """Where its laser leaves from. Defaults to the nose, one radius ahead of the centre."""
        return PlanePoint(
            self.x + math.sin(self.heading) * self.radius,
            self.y + math.cos(self.heading) * self.radius,
        )

    @property
    def hit_targets(self) -> list[ShotTarget]:
        """What the player's shots can hit and the player can bump into: the enemy itself, or
        e.g. a boss's parts and core (P07-R01). Empty when nothing of it can be hit.
        """
        return self._hit_targets()

    @property
    def shot_targets(self) -> list[ShotTarget]:
        """What the player's shots can hit: its `hit_targets`, unless some of them let shots
        through (e.g. a boss's shielded core, phase 7 review).
        """
        return self._shot_targets()

    def _hit_targets(self) -> list[ShotTarget]:
        """Hook behind `hit_targets`: the enemy itself."""
        return self._self_targets

    def _shot_targets(self) -> list[ShotTarget]:
        """Hook behind `shot_targets`: the same as `hit_targets`."""
        return self.hit_targets

    def update(self, ctx: EnemyContext, dt: float) -> None:
        """Moves and attacks for `dt` seconds. `age` is already advanced. Abstract."""
        raise NotImplementedError


class EnemyEntry:
    """Where a group comes in (P06-R07): an edge, and a position along it as a fraction (0..1)
    of that edge, from the left for the top edge and from the bottom for the side edges.
    """

    def __init__(self, side: EnemySide, position: float) -> None:
        self.side = side
        self.position = position


class EnemySpawnArea:
    """Where a group of enemies may appear."""

    def __init__(
        self,
        width: float,
        height: float,
        random: Random,
        entry: EnemyEntry | None = None,
        top_range: tuple[float, float] | None = None,
    ) -> None:
        """`entry` is where the group should come in (a wave script's choice); kinds follow it as
        far as their movement allows, and without it they pick at random. `top_range` is the X
        range (logical pixels) that enemies coming in from the top keep to (phase 6 review); the
        whole width when None.
        """
        self.width = width
        self.height = height
        self.random = random
        self.entry = entry
        self.top_range = top_range


class EnemyKindDefinition:
    """A kind of enemy a game offers: a name, and how one group of it appears (P05)."""

    def __init__(self, id: str, name: str, spawn: EnemyKindSpawn) -> None:
        """`spawn` creates one group of this kind (one enemy, or e.g. a swarm), just outside the
        playfield.
        """
        self.id = id
        self.name = name
        self.spawn = spawn


def validate_enemy_kinds(kinds: list[EnemyKindDefinition]) -> None:
    """Raises a descriptive error if the kinds are empty or have duplicate ids."""
    if len(kinds) == 0:
        raise ValueError("A game needs at least one enemy kind")
    ids: list[str] = []
    for kind in kinds:
        if kind.id in ids:
            raise ValueError('Duplicate enemy kind id "' + kind.id + '"')
        ids.append(kind.id)
