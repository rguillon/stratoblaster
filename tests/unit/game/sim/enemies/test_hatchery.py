# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/sim/enemies/hatchery.py`."""

import math

import pytest
from helpers.enemy_steps import area, run
from helpers.fakes import FakeContext

from game.config.enemy_hatchery import HATCHERY_CONFIG
from game.sim.enemies.hatchery import Hatchery
from game.sim.enemies.wasp import Wasp
from game.sim.enemy_kinds import ENEMY_KINDS

CFG = HATCHERY_CONFIG
KIND = next(kind for kind in ENEMY_KINDS if kind.id == "hatchery")


def test_enm_hatchery_05_the_kind_spawns_a_live_hatchery_just_above_the_playfield() -> None:
    enemies = KIND.spawn(area(width=400, height=600))
    assert len(enemies) == 1
    assert isinstance(enemies[0], Hatchery)
    assert enemies[0].health > 0
    assert enemies[0].y > 600


def test_enm_hatchery_05_it_descends_straight_down_slowly() -> None:
    ctx = FakeContext()
    hatchery = Hatchery(200, 500)
    run(hatchery, ctx, 1.0)
    assert hatchery.x == 200
    assert hatchery.y == pytest.approx(500 - CFG.speed, rel=1e-2)


def test_enm_hatchery_06_its_two_turrets_fire_aimed_bullets_at_the_player() -> None:
    ctx = FakeContext()
    hatchery = Hatchery(200, 580)
    run(hatchery, ctx, 5.0)
    assert ctx.missiles == []
    assert ctx.lasers == []
    assert len(hatchery.turrets) == len(CFG.turrets.pivots) == 2
    # Each turret fires every `fireInterval` once it points at the player, from its own side.
    shots = 1 + math.floor((5 - CFG.turrets.firstShot) / CFG.turrets.fireInterval)
    assert len(ctx.bullets) == 2 * shots
    assert len([x for x, *_rest in ctx.bullets if x < 200]) == shots
    assert len([x for x, *_rest in ctx.bullets if x > 200]) == shots
    for x, y, heading, spec in ctx.bullets:
        want = math.atan2(ctx.player_x - x, ctx.player_y - y)
        assert abs(math.remainder(heading - want, math.tau)) < math.radians(6)
        assert spec == CFG.turrets.bullet


def test_enm_hatchery_06_its_turrets_hold_their_fire_above_the_playfield() -> None:
    ctx = FakeContext()
    hatchery = Hatchery(200, 700)
    run(hatchery, ctx, 3.0)
    assert hatchery.y > ctx.height
    assert ctx.bullets == []


def test_enm_hatchery_07_it_launches_one_wasp_from_each_of_its_three_deck_bays() -> None:
    ctx = FakeContext()
    hatchery = Hatchery(200, 580)
    run(hatchery, ctx, CFG.firstLaunch + 0.05)
    assert len(CFG.bays) == 3
    assert len(ctx.spawned) == 3
    assert all(isinstance(enemy, Wasp) for enemy in ctx.spawned)
    # Each from its bay, along the deck.
    at = hatchery.y + CFG.speed * 0.05
    for wasp, bay in zip(ctx.spawned, CFG.bays, strict=True):
        assert wasp.x == pytest.approx(200 + bay[0])
        assert wasp.y == pytest.approx(at + bay[1], abs=CFG.speed * 0.1)


def test_enm_hatchery_07_its_bay_doors_open_the_wasps_rise_then_the_doors_close() -> None:
    ctx = FakeContext()
    doors = CFG.doors
    hatchery = Hatchery(200, 590)
    bays = len(CFG.bays)
    assert len(hatchery.tracks) == 2 * bays

    def opened() -> float:
        assert len(set(hatchery.tracks[:bays])) == 1
        return hatchery.tracks[0]

    def lift() -> float:
        assert len(set(hatchery.tracks[bays:])) == 1
        return hatchery.tracks[bays]

    # Closed over the loaded Wasps until `openLead` before the launch.
    run(hatchery, ctx, CFG.firstLaunch - doors.openLead - 0.1)
    assert (opened(), lift()) == (0, 0)
    # The doors open...
    run(hatchery, ctx, 0.1 + doors.seconds / 2)
    assert opened() == pytest.approx(0.5, abs=0.05)
    assert lift() == 0
    # ...then the Wasps rise to the deck.
    run(hatchery, ctx, doors.seconds / 2 + doors.riseSeconds / 2)
    assert opened() == 1
    assert lift() == pytest.approx(0.5, abs=0.05)
    run(hatchery, ctx, doors.openLead - doors.seconds - doors.riseSeconds / 2 - 0.05)
    assert ctx.spawned == []
    assert lift() == 1
    # They take off: the bays are empty, the doors stay open a moment, then close.
    run(hatchery, ctx, 0.1)
    assert len(ctx.spawned) == bays
    assert (opened(), lift()) == (1, -1)
    run(hatchery, ctx, doors.closeDelay + doors.seconds / 2 - 0.05)
    assert opened() == pytest.approx(0.5, abs=0.05)
    assert lift() == -1
    run(hatchery, ctx, doors.seconds / 2 + 0.1)
    # Closed again, the next Wasps loaded under them.
    assert (opened(), lift()) == (0, 0)


def test_enm_hatchery_07_it_launches_again_every_interval() -> None:
    ctx = FakeContext()
    hatchery = Hatchery(200, 590)
    run(hatchery, ctx, CFG.firstLaunch + 0.05)
    assert len(ctx.spawned) == 3
    run(hatchery, ctx, CFG.launchInterval)
    assert len(ctx.spawned) == 6


def test_enm_hatchery_03_its_hatch_charges_towards_the_next_launch() -> None:
    ctx = FakeContext()
    hatchery = Hatchery(200, 590)
    run(hatchery, ctx, CFG.firstLaunch + 0.05)
    low = hatchery.charge
    run(hatchery, ctx, CFG.launchInterval / 2)
    assert hatchery.charge > low


def test_enm_hatchery_08_it_does_not_launch_while_above_the_playfield() -> None:
    ctx = FakeContext()
    hatchery = Hatchery(200, 700)
    run(hatchery, ctx, 3.0)
    assert ctx.spawned == []
    assert hatchery.charge == 0


def test_enm_hatchery_08_it_stops_launching_low_on_the_screen() -> None:
    ctx = FakeContext()
    hatchery = Hatchery(200, CFG.lastLaunchFraction * 600 - 1)
    run(hatchery, ctx, CFG.firstLaunch + 1.0)
    assert ctx.spawned == []
    assert hatchery.charge == 0


def test_enm_hatchery_09_it_has_400_health_and_scores_700() -> None:
    hatchery = Hatchery(200, 580)
    assert hatchery.health == 400
    assert hatchery.points == 700
    assert hatchery.model == "hatchery"
