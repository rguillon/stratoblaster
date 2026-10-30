"""Unit tests of `src/game/sim/bosses/world_boss.py`."""

import pytest
from helpers.enemy_steps import area
from helpers.fakes import FakeContext

from game.config.bosses.final_bosses import REFINERY_TITAN
from game.config.bosses.mini_bosses import REEF_WARDEN
from game.config.bosses.world_4.caldera_throne import CALDERA_THRONE
from game.sim.bosses.world_boss import WorldBoss, _sign, boss_half_width


def test_p07_r05_sign_is_minus_one_zero_or_one() -> None:
    assert (_sign(3.5), _sign(-2), _sign(0)) == (1, -1, 0)


def test_p07_r05_the_half_width_reaches_the_farthest_part_or_the_core() -> None:
    assert boss_half_width(REEF_WARDEN) >= REEF_WARDEN.stats["coreRadius"]
    widest = max(abs(p["x"]) + p["radius"] for p in REEF_WARDEN.stats["parts"])
    assert boss_half_width(REEF_WARDEN) >= widest - 1e-9


def test_p07_r05_a_boss_comes_in_from_above_the_top_edge_and_brakes_into_place() -> None:
    boss = WorldBoss(REEF_WARDEN, area(width=480, height=640))
    assert boss.y > 640
    ctx = FakeContext()
    for _ in range(60 * 30):
        boss.age += 1 / 60
        boss.update(ctx, 1 / 60)
        if boss.y == boss.stop_y:
            break
    assert boss.y == pytest.approx(REEF_WARDEN.stopFraction * 640)


def test_p07_r05_a_boss_sways_only_as_far_as_its_parts_keep_within_the_ship_reach() -> None:
    wide = WorldBoss(REEF_WARDEN, area(width=480, height=640))
    assert 0 <= wide.sway_amplitude <= REEF_WARDEN.sway.amplitude
    narrow = WorldBoss(CALDERA_THRONE, area(width=480, height=640, top_range=(200, 260)))
    assert narrow.sway_amplitude == 0


def test_p07_r05_a_boss_starts_at_the_middle_of_its_top_range() -> None:
    boss = WorldBoss(REEF_WARDEN, area(width=480, height=640, top_range=(100, 300)))
    assert boss.center_x == pytest.approx(200)


def test_p07_r05_a_destroyed_ring_part_bursts_into_its_ring_of_bullets_once() -> None:
    ctx = FakeContext()
    boss = WorldBoss(REFINERY_TITAN, area(width=480, height=640))
    for ring_id in ("tank-left", "tank-right"):
        boss._by_id[ring_id].destroy()
    boss.on_stage_change(1, ctx)
    assert len(ctx.bullets) == 2 * 12
    before = len(ctx.bullets)
    boss.on_stage_change(2, ctx)
    assert len(ctx.bullets) == before


def test_p07_r05_an_angry_boss_fires_its_rage_pattern_and_lights_up_full() -> None:
    ctx = FakeContext()
    boss = WorldBoss(REEF_WARDEN, area(width=480, height=640))
    boss.on_stage_change(0, ctx)
    boss.update_rage(ctx, 0.5)
    assert boss.charge == 1


def test_p07_r05_a_boss_turret_follows_nothing_while_its_source_is_destroyed() -> None:
    boss = WorldBoss(REEF_WARDEN, area(width=480, height=640))
    part_id = REEF_WARDEN.stats["parts"][0]["id"]
    assert boss._source(part_id) is not None
    boss._by_id[part_id].destroy()
    assert boss._source(part_id) is None
    assert boss._source("core") is boss.core
