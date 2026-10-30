"""Unit tests of `src/core/systems/player_hits.py`."""

import math
from types import SimpleNamespace

import pytest

from core.entities.enemy import Enemy, EnemyBulletSpec, EnemyLaserSpec, EnemyMissileSpec, EnemyStats
from core.entities.muzzle import PlanePoint
from core.systems.enemy_shots import EnemyShots, EnemyShotsOptions
from core.systems.player_hits import PlayerHit, _beam_distance, find_player_hits
from core.systems.player_hull import HullDamage, HullRules


class _Ship:
    def __init__(self, x: float = 0, y: float = 0) -> None:
        self.x = x
        self.y = y


class _Owner:
    def __init__(self, emitter: PlanePoint, heading: float) -> None:
        self.emitter = emitter
        self.heading = heading
        self.gone = False
        self.health = 10


class _Boss(Enemy):
    rammable = False

    def __init__(self, x: float, y: float, parts: list[Enemy]) -> None:
        super().__init__(x, y, EnemyStats("boss", 10, 10, 0))
        self._parts = parts

    def _hit_targets(self) -> list:  # type: ignore[override]
        return self._parts


RULES = HullRules(
    3,
    1,
    3,
    HullDamage(bullet=10, missile=20, laser=5, collision=30),
    15,
)


def _world(enemies: list[Enemy] | None = None) -> SimpleNamespace:
    shots = EnemyShots(EnemyShotsOptions(100, 100, 10))
    return SimpleNamespace(shots=shots, enemies=enemies if enemies is not None else [])


def _enemy(x: float, y: float, health: float = 10, rammable: bool = True) -> Enemy:
    enemy = Enemy(x, y, EnemyStats("e", 4, health, 1))
    enemy.rammable = rammable
    return enemy


def test_gd21_a_bullet_touching_the_hitbox_is_a_hit_that_removes_it() -> None:
    world = _world()
    world.shots.fire_bullet(0, 4, 0, EnemyBulletSpec(0, 2, "s"))
    hits = find_player_hits(_Ship(), RULES, world, set())
    assert len(hits) == 1
    hit = hits[0]
    assert isinstance(hit, PlayerHit)
    assert (hit.kind, hit.damage, hit.x, hit.y) == ("bullet", 10, 0, 4)
    hit.land()
    assert world.shots.bullets[0].alive is False


def test_gd21_a_missile_touching_the_hitbox_blows_up_on_the_next_step() -> None:
    world = _world()
    world.shots.fire_missile(0, 4, 0, EnemyMissileSpec(0, 0, 0, 2, 5, "m"))
    hits = find_player_hits(_Ship(), RULES, world, set())
    assert [(h.kind, h.damage) for h in hits] == [("missile", 20)]
    hits[0].land()
    assert world.shots.missiles[0].health == 0


def test_gd21_a_laser_beam_firing_across_the_ship_hits_once() -> None:
    world = _world()
    world.shots.fire_laser(_Owner(PlanePoint(0, 10), math.pi), EnemyLaserSpec(0, 1, 4, "b"))
    world.shots.step(0.1, 0, 0)
    lasers_hit: set = set()
    hits = find_player_hits(_Ship(), RULES, world, lasers_hit)
    assert [(h.kind, h.damage) for h in hits] == [("laser", 5)]
    hits[0].land()
    assert lasers_hit == {world.shots.lasers[0]}
    assert find_player_hits(_Ship(), RULES, world, lasers_hit) == []


def test_gd21_a_laser_beam_misses_a_ship_beside_it_or_past_its_end() -> None:
    world = _world()
    world.shots.fire_laser(_Owner(PlanePoint(0, 10), math.pi), EnemyLaserSpec(0, 1, 4, "b"))
    world.shots.step(0.1, 0, 0)
    assert find_player_hits(_Ship(10, 0), RULES, world, set()) == []
    assert find_player_hits(_Ship(0, -50), RULES, world, set()) == []


def test_gd21_the_beam_distance_is_to_the_segment_not_the_line() -> None:
    world = _world()
    world.shots.fire_laser(_Owner(PlanePoint(0, 10), math.pi), EnemyLaserSpec(0, 1, 4, "b"))
    world.shots.step(0.1, 0, 0)
    laser = world.shots.lasers[0]
    # Behind the start of the beam: the distance is to its start point (0, 10).
    assert _beam_distance(0, 20, laser) == pytest.approx(10)
    # Beside the middle of the beam.
    assert _beam_distance(4, 5, laser) == pytest.approx(4)


def test_gd21_an_enemy_ramming_the_ship_is_a_collision_that_damages_it_too() -> None:
    world = _world()
    enemy = _enemy(0, 5)
    world.enemies = [enemy]
    hits = find_player_hits(_Ship(), RULES, world, set())
    assert [(h.kind, h.damage, h.x, h.y) for h in hits] == [("collision", 30, 0, 5)]
    hits[0].land()
    assert enemy.health == 0


def test_p07_r06_a_boss_takes_no_ramming_damage() -> None:
    world = _world()
    boss = _enemy(0, 5, rammable=False)
    world.enemies = [boss]
    hits = find_player_hits(_Ship(), RULES, world, set())
    hits[0].land()
    assert boss.health == 10


def test_gd21_a_ram_never_takes_an_enemy_below_zero_health() -> None:
    world = _world()
    enemy = _enemy(0, 5, health=3)
    world.enemies = [enemy]
    find_player_hits(_Ship(), RULES, world, set())[0].land()
    assert enemy.health == 0


def test_gd21_gone_or_dead_enemies_do_not_ram() -> None:
    world = _world()
    gone = _enemy(0, 5)
    gone.gone = True
    dead = _enemy(0, 5, health=0)
    world.enemies = [gone, dead]
    assert find_player_hits(_Ship(), RULES, world, set()) == []


def test_p07_r06_a_boss_collides_through_the_first_part_that_is_touched() -> None:
    world = _world()
    far = _enemy(50, 50)
    dead_part = _enemy(0, 5, health=0)
    near = _enemy(0, 6)
    world.enemies = [_Boss(0, 0, [far, dead_part, near])]
    hits = find_player_hits(_Ship(), RULES, world, set())
    assert [(h.kind, h.x, h.y) for h in hits] == [("collision", 0, 6)]


def test_p07_r06_a_boss_part_that_is_out_of_reach_is_no_collision() -> None:
    world = _world()
    world.enemies = [_Boss(0, 0, [_enemy(50, 50)])]
    assert find_player_hits(_Ship(), RULES, world, set()) == []
