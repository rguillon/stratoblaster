"""Enemies (`core.entities.enemy`, P05): base behaviour, spawn areas and kind validation."""

import math
from typing import Any

import pytest
from fakes import FakeContext

from core.entities.enemy import (
    Enemy,
    EnemyBulletSpec,
    EnemyBurstSpec,
    EnemyEntry,
    EnemyKindDefinition,
    EnemyLaserSpec,
    EnemyMissileSpec,
    EnemySpawnArea,
    EnemyStats,
    validate_enemy_kinds,
)
from core.math.rng import create_rng


class Walker(Enemy):
    """An enemy that does nothing when it updates."""

    def update(self, ctx: Any, dt: float) -> None:
        self.age += dt


class Gunner(Walker):
    """An enemy whose hit targets are overridden by the hook, as a subclass does."""

    def _hit_targets(self) -> list[Any]:
        return [self, "extra"]


def make_enemy(x: float = 100.0, y: float = 200.0, cls: type[Enemy] = Walker) -> Enemy:
    return cls(x, y, EnemyStats("drone", 8, 5, 10))


def test_enemy_stats_keep_their_fields() -> None:
    stats = EnemyStats("drone", 8, 5, 10)
    assert (stats.model, stats.radius, stats.health, stats.points) == ("drone", 8, 5, 10)


def test_a_new_enemy_starts_at_full_health_facing_down() -> None:
    enemy = make_enemy()
    assert enemy.health == enemy.max_health == 5
    assert enemy.heading == pytest.approx(math.pi)
    assert enemy.id == 0
    assert enemy.age == 0
    assert enemy.charge == 0
    assert enemy.gone is False
    assert enemy.drop_chance is None
    assert enemy.model == "drone"
    assert enemy.points == 10


def test_enemy_kinds_of_the_base_class_expire_and_can_be_rammed() -> None:
    assert Enemy.expires is True
    assert Enemy.rammable is True
    assert Enemy.on_destroyed is None


def test_the_base_update_is_abstract() -> None:
    with pytest.raises(NotImplementedError):
        make_enemy(cls=Enemy).update(FakeContext(), 0.1)


def test_a_muzzle_of_a_facing_down_enemy_keeps_its_offset() -> None:
    point = make_enemy().place((0, 10, 3))
    assert (point.x, point.y, point.height) == pytest.approx((100, 210, 3))


def test_place_ignores_the_turret_flag() -> None:
    with_turret = make_enemy().place((0, 10, 3), on_turret=True)
    without = make_enemy().place((0, 10, 3))
    assert (with_turret.x, with_turret.y) == pytest.approx((without.x, without.y))


def test_the_emitter_is_one_radius_ahead_of_the_centre() -> None:
    emitter = make_enemy().emitter
    assert (emitter.x, emitter.y) == pytest.approx((100, 192))


def test_the_emitter_follows_the_heading() -> None:
    enemy = make_enemy()
    enemy.heading = math.pi / 2
    emitter = enemy.emitter
    assert (emitter.x, emitter.y) == pytest.approx((108, 200))


def test_an_enemy_is_its_own_hit_target() -> None:
    enemy = make_enemy()
    assert enemy.hit_targets == [enemy]
    assert enemy.shot_targets == [enemy]


def test_shot_targets_follow_the_hit_target_hook() -> None:
    gunner = make_enemy(cls=Gunner)
    assert gunner.shot_targets == [gunner, "extra"]
    assert gunner.hit_targets == [gunner, "extra"]


def test_a_spawn_area_keeps_its_settings() -> None:
    random = create_rng(1)
    area = EnemySpawnArea(400, 600, random)
    assert (area.width, area.height, area.random) == (400, 600, random)
    assert area.entry is None
    assert area.top_range is None


def test_p06_r07_an_entry_is_an_edge_and_a_position_along_it() -> None:
    entry = EnemyEntry("left", 0.25)
    assert (entry.side, entry.position) == ("left", 0.25)
    area = EnemySpawnArea(400, 600, create_rng(1), entry=entry, top_range=(10, 300))
    assert area.entry is entry
    assert area.top_range == (10, 300)


def test_an_enemy_kind_keeps_its_name_and_spawn() -> None:
    def spawn(area: EnemySpawnArea) -> list[Enemy]:
        return []

    kind = EnemyKindDefinition("drone", "Drone", spawn)
    assert (kind.id, kind.name, kind.spawn) == ("drone", "Drone", spawn)


def test_the_kinds_must_not_be_empty() -> None:
    with pytest.raises(ValueError, match="at least one enemy kind"):
        validate_enemy_kinds([])


def test_the_kind_ids_must_be_unique() -> None:
    kinds = [
        EnemyKindDefinition("drone", "A", lambda area: []),
        EnemyKindDefinition("drone", "B", lambda area: []),
    ]
    with pytest.raises(ValueError, match='Duplicate enemy kind id "drone"'):
        validate_enemy_kinds(kinds)


def test_valid_kinds_pass() -> None:
    validate_enemy_kinds([EnemyKindDefinition("drone", "A", lambda area: [])])


def test_bullet_missile_and_laser_specs_keep_their_fields() -> None:
    bullet = EnemyBulletSpec(120, 3, "dot")
    assert (bullet.speed, bullet.radius, bullet.style, bullet.burst) == (120, 3, "dot", None)

    burst = EnemyBurstSpec(1.0, 8, bullet)
    assert (burst.after, burst.count, burst.bullet) == (1.0, 8, bullet)

    missile = EnemyMissileSpec(150, 90, 2.0, 4, 2, "rocket")
    assert (missile.turn_rate_deg, missile.homing_seconds, missile.health) == (90, 2.0, 2)

    laser = EnemyLaserSpec(0.5, 1.5, 4, "beam")
    assert (laser.warning_seconds, laser.firing_seconds, laser.width) == (0.5, 1.5, 4)
    assert laser.sweeps is False
