"""Fakes of the entity tests: the world an enemy sees (`EnemyContext`) and a boss whose hooks only
record what they are asked to do. Imported by the test modules of this folder."""

from typing import Any

from core.entities.boss import Boss, BossStats
from core.entities.muzzle import PlanePoint, RaisedPoint
from core.math.rng import create_rng


class FakeContext:
    """An `EnemyContext` that records what the enemy did to the world."""

    def __init__(self) -> None:
        self.width = 400.0
        self.height = 600.0
        self.player_x = 200.0
        self.player_y = 50.0
        self.random = create_rng(1)
        self.fire_rate = 1.0
        self.bullets: list[tuple[float, float, float, Any]] = []
        self.missiles: list[tuple[float, float, float, Any]] = []
        self.lasers: list[tuple[Any, Any]] = []
        self.spawned: list[Any] = []
        self.explosions: list[tuple[float, float, float]] = []
        self.broken: list[Any] = []

    def seen(self, point: RaisedPoint) -> PlanePoint:
        return PlanePoint(point.x, point.y)

    def fire_bullet(self, x: float, y: float, heading: float, spec: Any) -> None:
        self.bullets.append((x, y, heading, spec))

    def fire_missile(self, x: float, y: float, heading: float, spec: Any) -> None:
        self.missiles.append((x, y, heading, spec))

    def fire_laser(self, owner: Any, spec: Any) -> None:
        self.lasers.append((owner, spec))

    def spawn(self, enemy: Any) -> None:
        self.spawned.append(enemy)

    def explode(self, x: float, y: float, radius: float) -> None:
        self.explosions.append((x, y, radius))

    def break_part(self, part: Any) -> None:
        self.broken.append(part)


class ProbeBoss(Boss):
    """A boss whose coming-in, moving and attacking hooks only record their calls."""

    def __init__(self, x: float, y: float, stats: BossStats) -> None:
        super().__init__(x, y, stats)
        self.arrived = False
        self.moves = 0
        self.patterns: list[float] = []

    def enter(self, ctx: Any, dt: float) -> bool:
        return self.arrived

    def move(self, ctx: Any, dt: float) -> None:
        self.moves += 1

    def update_pattern(self, ctx: Any, dt: float) -> None:
        self.patterns.append(dt)
