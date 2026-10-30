"""What touches the player's hitbox (GD-21, P11-R05), ported from `core/systems/player-hits.ts`."""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Literal, Protocol  # noqa: E402

from core.systems.enemy_shots import EnemyLaser  # noqa: E402
from core.systems.enemy_world import EnemyWorld  # noqa: E402
from core.systems.player_hull import HullRules  # noqa: E402

PlayerHitKind = Literal["bullet", "missile", "laser", "collision"]


class PlayerHitPoint(Protocol):
    """A point of the playfield."""

    @property
    def x(self) -> float: ...

    @property
    def y(self) -> float: ...


Touches = Callable[[PlayerHitPoint, float], bool]

__pragma__("noskip")


class PlayerHit:
    """Something touching the player's hitbox, and what happens to it if the hit counts.

    `land` is called when the hit counts: the bullet goes, the missile blows up, the rammed enemy
    takes damage...
    """

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self, kind: str, damage: float, x: float, y: float, land: Callable[[], None]
    ) -> None:
        self.kind = kind
        self.damage = damage
        self.x = x
        self.y = y
        self.land = land


def _beam_distance(x: float, y: float, laser: EnemyLaser) -> float:
    """Distance from (x, y) to the segment from the laser along its heading for its length."""
    dx = math.sin(laser.heading)
    dy = math.cos(laser.heading)
    t = max(0, min(laser.length, (x - laser.x) * dx + (y - laser.y) * dy))
    return math.hypot(x - (laser.x + t * dx), y - (laser.y + t * dy))


def _bullet_land(bullet: object) -> Callable[[], None]:
    def land() -> None:
        bullet.alive = False  # type: ignore[attr-defined]

    return land


def _missile_land(missile: object) -> Callable[[], None]:
    def land() -> None:
        missile.health = 0  # type: ignore[attr-defined]

    return land


def _laser_land(laser: EnemyLaser, lasers_hit: set[EnemyLaser]) -> Callable[[], None]:
    def land() -> None:
        lasers_hit.add(laser)

    return land


def _ram_land(enemy: object, damage: float) -> Callable[[], None]:
    def land() -> None:
        # A boss takes no ramming damage (P07-R06).
        if enemy.rammable:  # type: ignore[attr-defined]
            enemy.health = max(0, enemy.health - damage)  # type: ignore[attr-defined]

    return land


def _bullet_hits(world: EnemyWorld, rules: HullRules, touches: Touches) -> list[PlayerHit]:
    hits: list[PlayerHit] = []
    for b in world.shots.bullets:
        if b.alive and touches(b, b.radius):
            hits.append(PlayerHit("bullet", rules.damage.bullet, b.x, b.y, _bullet_land(b)))
    return hits


def _missile_hits(world: EnemyWorld, rules: HullRules, touches: Touches) -> list[PlayerHit]:
    hits: list[PlayerHit] = []
    for m in world.shots.missiles:
        if m.alive and m.health > 0 and touches(m, m.radius):
            # Shot down by the hit: it blows up on the next step.
            hits.append(PlayerHit("missile", rules.damage.missile, m.x, m.y, _missile_land(m)))
    return hits


def _laser_hits(
    world: EnemyWorld,
    rules: HullRules,
    ship: PlayerHitPoint,
    lasers_hit: set[EnemyLaser],
) -> list[PlayerHit]:
    hits: list[PlayerHit] = []
    x = ship.x
    y = ship.y
    for laser in world.shots.lasers:
        if (
            laser.phase == "firing"
            and laser not in lasers_hit
            and _beam_distance(x, y, laser) <= rules.hit_radius + laser.spec.width / 2
        ):
            hits.append(
                PlayerHit("laser", rules.damage.laser, x, y, _laser_land(laser, lasers_hit))
            )
    return hits


def _collision_hits(world: EnemyWorld, rules: HullRules, touches: Touches) -> list[PlayerHit]:
    hits: list[PlayerHit] = []
    for enemy in world.enemies:
        if enemy.gone or enemy.health <= 0:
            continue
        # What can be hit of it: the enemy, or a boss's core and parts (P07-R06).
        body = None
        for target in enemy.hit_targets:
            if target.health > 0 and touches(target, target.radius):
                body = target
                break
        if body is None:
            continue
        hits.append(
            PlayerHit(
                "collision",
                rules.damage.collision,
                body.x,
                body.y,
                _ram_land(enemy, rules.ram_damage),
            )
        )
    return hits


def _sort_most_damaging_first(hits: list[PlayerHit]) -> None:
    """A stable sort by damage, the most damaging first (as `Array.sort` does)."""
    for i in range(1, len(hits)):
        j = i
        while j > 0 and hits[j - 1].damage < hits[j].damage:
            hits[j - 1], hits[j] = hits[j], hits[j - 1]
            j -= 1


def find_player_hits(
    ship: PlayerHitPoint,
    rules: HullRules,
    world: EnemyWorld,
    lasers_hit: set[EnemyLaser],
) -> list[PlayerHit]:
    """The enemy shots and enemies touching the player's hitbox at (`x`, `y`), the most damaging
    first (GD-21: a small hitbox). A laser beam counts once: those in `lasers_hit` are skipped,
    and a beam's hit adds it there when it lands. A collision also hurts the enemy rammed, unless
    it is a boss.
    """

    def touches(p: PlayerHitPoint, radius: float) -> bool:
        return math.hypot(p.x - ship.x, p.y - ship.y) <= rules.hit_radius + radius

    hits: list[PlayerHit] = []
    hits.extend(_bullet_hits(world, rules, touches))
    hits.extend(_missile_hits(world, rules, touches))
    hits.extend(_laser_hits(world, rules, ship, lasers_hit))
    hits.extend(_collision_hits(world, rules, touches))
    _sort_most_damaging_first(hits)
    return hits
