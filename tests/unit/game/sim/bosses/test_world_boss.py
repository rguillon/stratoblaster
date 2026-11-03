# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/bosses/world_boss.py`."""

import pytest
from helpers.enemy_steps import area
from helpers.fakes import FakeContext

from game.config.bosses.boss_kit import BOSS_TIMING, bullet, part, stages, volley
from game.config.bosses.final_bosses import REFINERY_TITAN
from game.config.bosses.hidden_weapons import region_blasts
from game.config.bosses.mini_bosses import REEF_WARDEN
from game.config.bosses.world_3.stone_idol import STONE_IDOL
from game.config.bosses.world_4.caldera_throne import CALDERA_THRONE
from game.config.record import merge
from game.sim.bosses.world_boss import WorldBoss, boss_half_width


def test_boss_10_the_half_width_reaches_the_farthest_part_or_the_core() -> None:
    assert boss_half_width(REEF_WARDEN) >= REEF_WARDEN.stats["coreRadius"]
    widest = max(abs(p["x"]) + p["radius"] for p in REEF_WARDEN.stats["parts"])
    assert boss_half_width(REEF_WARDEN) >= widest - 1e-9


def test_boss_08_a_boss_comes_in_from_above_the_top_edge_and_brakes_into_place() -> None:
    boss = WorldBoss(REEF_WARDEN, area(width=480, height=640))
    assert boss.y > 640
    ctx = FakeContext()
    for _ in range(60 * 30):
        boss.age += 1 / 60
        boss.update(ctx, 1 / 60)
        if boss.y == boss.stop_y:
            break
    assert boss.y == pytest.approx(REEF_WARDEN.stopFraction * 640)


def test_boss_10_a_boss_sways_only_as_far_as_its_parts_keep_within_the_ship_reach() -> None:
    wide = WorldBoss(REEF_WARDEN, area(width=480, height=640))
    assert 0 <= wide.sway_amplitude <= REEF_WARDEN.sway.amplitude
    narrow = WorldBoss(CALDERA_THRONE, area(width=480, height=640, top_range=(200, 260)))
    assert narrow.sway_amplitude == 0


def test_boss_08_a_boss_starts_at_the_middle_of_its_top_range() -> None:
    boss = WorldBoss(REEF_WARDEN, area(width=480, height=640, top_range=(100, 300)))
    assert boss.center_x == pytest.approx(200)


def test_boss_23_a_destroyed_ring_part_bursts_into_its_ring_of_bullets_once() -> None:
    ctx = FakeContext()
    boss = WorldBoss(REFINERY_TITAN, area(width=480, height=640))
    for ring_id in ("tank-left", "tank-right"):
        boss._by_id[ring_id].destroy()
    boss.on_stage_change(1, ctx)
    assert len(ctx.bullets) == 2 * 12
    before = len(ctx.bullets)
    boss.on_stage_change(2, ctx)
    assert len(ctx.bullets) == before


def test_boss_27_an_angry_boss_fires_its_rage_pattern_and_lights_up_full() -> None:
    ctx = FakeContext()
    boss = WorldBoss(REEF_WARDEN, area(width=480, height=640))
    boss.on_stage_change(0, ctx)
    boss.update_rage(ctx, 0.5)
    assert boss.charge == 1


def test_boss_21_a_boss_turret_follows_nothing_while_its_source_is_destroyed() -> None:
    """Also BOSS-29: its turret follows nothing then."""
    boss = WorldBoss(REEF_WARDEN, area(width=480, height=640))
    part_id = REEF_WARDEN.stats["parts"][0]["id"]
    assert boss._source(part_id) is not None
    boss._by_id[part_id].destroy()
    assert boss._source(part_id) is None
    assert boss._source("core") is boss.core


def _hidden_gun_design() -> object:
    """Return the Reef Warden with one more gun, hidden until its transformation."""
    stats = REEF_WARDEN.stats
    parts = [*stats["parts"], part("hidden-gun", [0, -10], 8, 50, {"reveal": 1, "shields": False})]
    guns = merge(REEF_WARDEN.guns, {"hidden-gun": {"gun": [[0, -14, 3]]}})
    shot = volley.aimed("hidden-gun", 0.5, 1, 0, bullet("magenta", 150), 0)
    return merge(
        REEF_WARDEN,
        {
            "stats": merge(stats, {"parts": parts}),
            "guns": guns,
            "stages": stages([shot], [[]]),
            "rage": None,
        },
    )


def test_a_hidden_weapon_fires_only_once_revealed_and_its_armour_blows_off() -> None:
    """BOSS-38; also BOSS-37: the blasts as it transforms."""
    ctx = FakeContext()
    boss = WorldBoss(_hidden_gun_design(), area(width=480, height=640))
    boss.state = "fighting"
    for _ in range(60):
        boss.update(ctx, 1 / 60)
    assert ctx.bullets == []
    for piece in boss.parts:
        if piece.spec.reveal is None:
            piece.destroy()
    boss.update(ctx, 0.0)
    assert boss.state == "transforming"
    # Its armour regions burst (D-224), and a blast where each weapon comes out.
    bursts = [b for r in REEF_WARDEN.armour for b in region_blasts(r, BOSS_TIMING.regionBlasts)]
    weapons = [p for p in boss.parts if p.spec.reveal == 1]
    assert len(ctx.explosions) == len(bursts) + len(weapons)
    for _ in range(60 * 4):
        boss.update(ctx, 1 / 60)
    assert boss.form == 1
    assert len(ctx.bullets) > 0


def test_boss_25_a_part_s_launches_go_out_from_it_while_it_stands() -> None:
    """A launch from a part the boss does not have has no side, and never goes out."""
    launches = [
        {"from": "cannon-left", "kind": "hornets", "count": 2, "every": 1, "first": 0.1},
        {"from": "ghost", "kind": "hornets", "count": 1, "every": 1, "first": 0.1},
    ]
    boss = WorldBoss(merge(REEF_WARDEN, {"launches": launches}), area(width=480, height=640))
    ctx = FakeContext()
    for _ in range(5):
        boss.update_pattern(ctx, 0.1)
    assert [type(enemy).__name__ for enemy in ctx.spawned] == ["Hornet", "Hornet"]


def _turret_aims(boss: WorldBoss) -> list[float]:
    return [p.turret.aim for p in [boss.core, *boss.parts] if p.turret is not None]


def test_boss_29_a_dying_boss_turns_its_turrets_no_more() -> None:
    living = WorldBoss(STONE_IDOL, area(width=480, height=640))
    dying = WorldBoss(STONE_IDOL, area(width=480, height=640))
    ctx = FakeContext()
    for _ in range(30):
        living.update(ctx, 1 / 30)
        dying.update(ctx, 1 / 30)
    dying.hurt_core(0)
    assert dying.state == "dying"
    held = _turret_aims(dying)
    ctx.player_x = 0
    for _ in range(30):
        living.update(ctx, 1 / 30)
        dying.update(ctx, 1 / 30)
    assert _turret_aims(dying) == held
    assert _turret_aims(living) != held


def test_boss_37_a_transformation_bursts_only_the_armour_it_sheds() -> None:
    """Also BOSS-42: the regions of the other transformation stay on."""
    boss = WorldBoss(REFINERY_TITAN, area(width=480, height=640))
    assert {region.form for region in REFINERY_TITAN.armour} == {1, 2}
    ctx = FakeContext()
    boss.on_transform(2, ctx)
    expected = [
        (boss.x + b[0], boss.y + b[1], b[2])
        for region in REFINERY_TITAN.armour
        if region.form == 2
        for b in region_blasts(region, BOSS_TIMING.regionBlasts)
    ]
    expected.extend((p.x, p.y, p.radius) for p in boss.parts if p.spec.reveal == 2)
    assert ctx.explosions == expected
