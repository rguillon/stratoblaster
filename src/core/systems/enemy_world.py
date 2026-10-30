"""The enemies and their shots (P05)

Updates every enemy, removes the destroyed ones (scoring them, GD-50, and letting them spawn
parts) and the ones that left, and moves their shots. Its `targets` are what the player's shots
can hit. Pure and deterministic.
"""

from org.transcrypt.stubs.browser import __pragma__

from core.entities.enemy import EnemyBulletSpec, EnemyBurstSpec
from core.entities.muzzle import PlanePoint, seen_on_playfield
from core.entities.shot_target import is_alive
from core.systems.enemy_shots import EnemyShots, EnemyShotsOptions

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from core.entities.enemy import (  # noqa: E402
    DropSource,
    Enemy,
    EnemyLaserSpec,
    EnemyMissileSpec,
    LaserOwner,
)
from core.entities.muzzle import PlayfieldEye, RaisedPoint  # noqa: E402
from core.entities.shot_target import ShotTarget  # noqa: E402
from core.math.rng import Random  # noqa: E402

__pragma__("noskip")


class EnemyBlast:
    """Something that blew up during the last step, for the explosions (GD-62). `kind` is
    "enemy" or "missile"; `radius` is the size of what blew up (its hit radius).
    """

    def __init__(self, kind: str, x: float, y: float, radius: float) -> None:
        self.kind = kind
        self.x = x
        self.y = y
        self.radius = radius


class EnemyWorldOptions(EnemyShotsOptions):
    """The playfield and what the world culls by.

    `cull_margin`: enemies are removed once they have been on the playfield and are this far
    outside it, and shots once they are this far outside. `max_enemy_age`: enemies older than
    this are removed, whatever they do (a safety net).
    """

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        width: float,
        height: float,
        cull_margin: float,
        max_enemy_age: float,
        eye: PlayfieldEye | None = None,
    ) -> None:
        super().__init__(width, height, cull_margin, eye)
        self.max_enemy_age = max_enemy_age


class EnemyDifficulty:
    """How hard the enemies are, as factors on each kind's own values (1 = as tuned): their
    bullets' speed and how fast their attacks come (P06-R08).
    """

    def __init__(self, bullet_speed: float, fire_rate: float) -> None:
        self.bullet_speed = bullet_speed
        self.fire_rate = fire_rate


def _faster(spec: EnemyBulletSpec, factor: float) -> EnemyBulletSpec:
    """`spec` (and the bullets it bursts into) `factor` times as fast."""
    burst = spec.burst
    speed = spec.speed * factor
    if burst:
        return EnemyBulletSpec(
            speed,
            spec.radius,
            spec.style,
            EnemyBurstSpec(burst.after, burst.count, _faster(burst.bullet, factor)),
        )
    return EnemyBulletSpec(speed, spec.radius, spec.style, None)


class _WorldContext:
    """What an enemy sees and does while it updates: the world's `EnemyContext`."""

    def __init__(
        self,
        world: "EnemyWorld",
        options: EnemyWorldOptions,
        shots: EnemyShots,
        random: Random,
        difficulty: EnemyDifficulty,
    ) -> None:
        self._world = world
        self._options = options
        self._shots = shots
        self._bullet_speed = difficulty.bullet_speed
        self.width = options.width
        self.height = options.height
        self.random = random
        self.fire_rate = difficulty.fire_rate
        self.player_x = 0.0
        self.player_y = 0.0

    def seen(self, point: RaisedPoint) -> PlanePoint:
        return seen_on_playfield(self._options.eye, point)

    def fire_bullet(self, x: float, y: float, heading: float, spec: EnemyBulletSpec) -> None:
        self._shots.fire_bullet(x, y, heading, _faster(spec, self._bullet_speed))

    def fire_missile(self, x: float, y: float, heading: float, spec: EnemyMissileSpec) -> None:
        self._shots.fire_missile(x, y, heading, spec)

    def fire_laser(self, owner: LaserOwner, spec: EnemyLaserSpec) -> None:
        self._shots.fire_laser(owner, spec)

    def spawn(self, enemy: Enemy) -> None:
        self._world.spawned_enemies.append(enemy)

    def explode(self, x: float, y: float, radius: float) -> None:
        self._world.blasts.append(EnemyBlast("enemy", x, y, radius))

    def break_part(self, part: DropSource) -> None:
        self._world.blasts.append(EnemyBlast("enemy", part.x, part.y, part.radius))
        self._world.broken_parts.append(part)
        self._world.score += part.points if part.points is not None else 0


class EnemyWorld:
    """The enemies and their shots (P05). `enemies` are updated every step; `targets` are rebuilt
    every step (the living enemies' shot targets and the living missiles): the player's shots aim
    at these.
    """

    def __init__(
        self,
        options: EnemyWorldOptions,
        random: Random,
        difficulty: EnemyDifficulty | None = None,
    ) -> None:
        if difficulty is None:
            difficulty = EnemyDifficulty(1, 1)
        self.options = options
        self.enemies: list[Enemy] = []
        self.shots = EnemyShots(options)
        self.targets: list[ShotTarget] = []
        # Blasts of the last step.
        self.blasts: list[EnemyBlast] = []
        # Enemies the player's shots destroyed during the last step (e.g. to drop bonuses).
        self.destroyed: list[Enemy] = []
        # Pieces of enemies (a boss's parts) the player's shots destroyed during the last step.
        self.broken_parts: list[DropSource] = []
        # Enemies destroyed and points scored since the world was created: each enemy's points,
        # and each boss part's (P11-R01). The run adds its bonus points to the score.
        self.kills = 0
        self.score = 0.0
        # Enemies added (their parts and launches included) and their total health, since then.
        self.spawned = 0
        self.spawned_health = 0.0
        self.player_x = 0.0
        self.player_y = 0.0
        self._next_id = 1
        self._entered: set[Enemy] = set()
        self.spawned_enemies: list[Enemy] = []
        self._context = _WorldContext(self, options, self.shots, random, difficulty)

    def add(self, *enemies: Enemy) -> None:
        """Adds enemies, updated from the next step."""
        for enemy in enemies:
            enemy.id = self._next_id
            self._next_id += 1
            self.enemies.append(enemy)
            self.spawned += 1
            self.spawned_health += enemy.max_health
        self._rebuild_targets()

    @property
    def on_screen(self) -> int:
        """Number of enemies whose centre is over the playfield."""
        count = 0
        for enemy in self.enemies:
            if self._within(enemy, 0):
                count += 1
        return count

    def clear(self) -> None:
        """Removes every enemy and shot."""
        self.enemies.clear()
        self.shots.clear()
        self.blasts = []
        self.destroyed = []
        self.broken_parts = []
        self._rebuild_targets()

    def step(self, dt: float) -> None:
        """Advances everything by `dt` seconds."""
        self.blasts = []
        self.destroyed = []
        self.broken_parts = []
        self._context.player_x = self.player_x
        self._context.player_y = self.player_y
        self._collect_destroyed()
        for enemy in self.enemies:
            # Entities start `age` at the int 0; it is a float from here on.
            enemy.age += dt  # type: ignore[assignment]
            enemy.update(self._context, dt)
            self._check_gone(enemy)
        self._collect_destroyed()
        for missile in self.shots.missiles:
            if missile.alive and missile.health <= 0:
                self.blasts.append(EnemyBlast("missile", missile.x, missile.y, missile.radius))
        self.shots.step(dt, self.player_x, self.player_y)
        self._remove_gone()
        spawned = list(self.spawned_enemies)
        self.spawned_enemies.clear()
        self.add(*spawned)

    def _collect_destroyed(self) -> None:
        """Scores the enemies the player's shots destroyed and lets them spawn their parts."""
        for enemy in self.enemies:
            if enemy.gone or is_alive(enemy):
                continue
            enemy.gone = True
            self.kills += 1
            self.score += enemy.points
            self.blasts.append(EnemyBlast("enemy", enemy.x, enemy.y, enemy.radius))
            self.destroyed.append(enemy)
            if enemy.on_destroyed is not None:
                enemy.on_destroyed(self._context)

    def _within(self, enemy: Enemy, margin: float) -> bool:
        """Whether the enemy's centre is within `margin` of the playfield."""
        x = enemy.x
        y = enemy.y
        return (
            x >= -margin
            and x <= self.options.width + margin
            and y >= -margin
            and y <= self.options.height + margin
        )

    def _check_gone(self, enemy: Enemy) -> None:
        """Marks an enemy gone once it has been on the playfield and then left it, or is too old;
        one that does not expire (a boss) only goes once destroyed.
        """
        if not enemy.expires:
            return
        if self._within(enemy, enemy.radius):
            self._entered.add(enemy)
        left = not self._within(enemy, self.options.cull_margin) and enemy in self._entered
        if left or enemy.age > self.options.max_enemy_age:
            enemy.gone = True

    def _remove_gone(self) -> None:
        i = len(self.enemies) - 1
        while i >= 0:
            if self.enemies[i].gone:
                self.enemies.pop(i)
            i -= 1

    def _rebuild_targets(self) -> None:
        self.targets.clear()
        for enemy in self.enemies:
            if not enemy.gone:
                self.targets.extend(enemy.shot_targets)
        for missile in self.shots.missiles:
            if missile.alive:
                self.targets.append(missile)
