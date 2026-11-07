# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/core/systems/boss_pattern.py`: volleys fired from gun mounts (BOSS-58)."""

import math
from typing import Any

import pytest
from helpers.fakes import FakeContext

from core.entities.boss_turret import BossTurret, BossTurretSpec
from core.entities.enemy import EnemyBulletSpec, EnemyLaserSpec, EnemyMissileSpec
from core.entities.muzzle import Muzzle, PlanePoint, RaisedPoint
from core.systems.boss_mounts import BossMount, BossMountSpec, MountLaserOwner
from core.systems.boss_pattern import (
    SWEEP_GAP,
    BossAimedShape,
    BossBurstShape,
    BossFanShape,
    BossLaserShape,
    BossLaunchShape,
    BossMissilesShape,
    BossPattern,
    BossRingShape,
    BossVolley,
    _fire_mount,
    _step_sweep,
    _sweep_aim,
    _VolleyState,
)
from core.systems.gun_muzzles import GunMuzzles

DEG = math.pi / 180

DOWN = math.pi

BULLET = EnemyBulletSpec(10, 1, "round")

MISSILE = EnemyMissileSpec(5, 90, 1, 1, 3, "rocket")

LASER = EnemyLaserSpec(1, 1, 2, "beam")

# Fast enough to point anywhere in one turn of the turrets.
SNAP = 100000


class _Piece:
    """A boss's piece at (100, 300), pointing down: it places its mounts' barrels."""

    def __init__(self) -> None:
        self.x = 100.0
        self.y = 300.0
        self.heading = DOWN
        self.age = 1.0
        self.gone = False
        self.health = 10.0
        self.turret: BossTurret | None = None

    @property
    def emitter(self) -> PlanePoint:
        return PlanePoint(self.x, self.y)

    def place(self, muzzle: Muzzle, _on_turret: bool = False) -> RaisedPoint:
        mx, my, mh = muzzle
        return RaisedPoint(self.x + mx, self.y + my, mh)


def _ctx(player: tuple[float, float] = (100, 0)) -> FakeContext:
    """Return a world whose player is straight below the piece by default."""
    ctx = FakeContext()
    ctx.player_x, ctx.player_y = player
    return ctx


def _sources(piece: _Piece) -> Any:  # type: ignore[no-untyped-def]
    return {"core": piece}.get


def _turret(rate: float = SNAP) -> BossTurretSpec:
    return BossTurretSpec(0, 0, rate)


def _twin(turret: BossTurretSpec | None = None) -> BossMount:
    """Return two barrels side by side, pointing down, their tips 10 px below the pivot."""
    return BossMount(
        BossMountSpec("twin", "core", "gun", [[-2, -10, 5, 0], [2, -10, 5, 0]], turret)
    )


def _rotor(barrels: int = 4, turret: BossTurretSpec | None = None) -> BossMount:
    entries: list[list[float]] = []
    for k in range(barrels):
        angle = 360 * k / barrels
        a = angle * DEG
        entries.append([-math.sin(a) * 8, -math.cos(a) * 8, 6, angle])
    return BossMount(BossMountSpec("rotor", "core", "gun", entries, turret))


def _rack() -> BossMount:
    return BossMount(BossMountSpec("rack", "core", "missile", [[-3, 0, 4], [3, 0, 4]]))


def _volley(shape: object, mount: BossMount, every: float = 10, first: float = 0) -> BossVolley:
    return BossVolley("core", every, shape, first=first, mount=mount)  # type: ignore[arg-type]


def _assert_from_barrels(ctx: FakeContext, shots: list[tuple[BossMount, int]]) -> None:
    """Assert each bullet left its barrel's tip, along it (as the mount is now: fixed mounts)."""
    piece = _Piece()
    assert len(ctx.bullets) == len(shots)
    for (x, y, heading, _), (mount, k) in zip(ctx.bullets, shots, strict=True):
        tip = mount.tip(piece, mount.barrels[k])
        assert (x, y) == pytest.approx((tip.x, tip.y))
        assert heading == pytest.approx(mount.heading_of(piece, mount.barrels[k]))


def test_boss_58_open_fire_makes_every_volley_due_now() -> None:
    ctx = _ctx()
    mount = _twin()
    pattern = BossPattern([_volley(BossAimedShape(1, 0, BULLET), mount, first=8)])
    pattern.step(ctx, 0.1, _sources(_Piece()))
    assert ctx.bullets == []
    pattern.open_fire()
    pattern.step(ctx, 0.01, _sources(_Piece()))
    _assert_from_barrels(ctx, [(mount, 0)])


def test_boss_58_a_fixed_twin_gun_fires_its_aimed_shots_one_barrel_after_the_other() -> None:
    ctx = _ctx(player=(400, 0))
    mount = _twin()
    pattern = BossPattern([_volley(BossAimedShape(1, 0, BULLET), mount, every=1, first=0.5)])
    piece = _Piece()
    for _ in range(3):
        pattern.step(ctx, 1.0, _sources(piece))
    # Fixed barrels: along them, wherever the player is (BOSS-29: guns not on a turret never wait).
    _assert_from_barrels(ctx, [(mount, 0), (mount, 1), (mount, 0)])
    assert mount.barrels[0].fired_at == 1.0


def test_boss_58_a_fixed_gun_s_fan_leaves_as_many_barrels_as_it_has() -> None:
    ctx = _ctx()
    mount = _twin()
    pattern = BossPattern([_volley(BossFanShape(0, 3, 15, BULLET), mount)])
    pattern.step(ctx, 0.01, _sources(_Piece()))
    _assert_from_barrels(ctx, [(mount, 0), (mount, 1)])


def test_boss_58_a_ring_fires_one_bullet_from_each_rotor_barrel() -> None:
    ctx = _ctx()
    mount = _rotor(4)
    pattern = BossPattern([_volley(BossRingShape(4, 15, BULLET), mount, every=1)])
    pattern.step(ctx, 0.01, _sources(_Piece()))
    _assert_from_barrels(ctx, [(mount, k) for k in range(4)])
    assert all(barrel.fired_at == 1.0 for barrel in mount.barrels)


def test_boss_29_a_rotor_turret_spins_on_with_its_ring_s_turn() -> None:
    """Also BOSS-58: the ring never waits for its turret; it leaves the barrels where they are."""
    ctx = _ctx()
    mount = _rotor(4, _turret())
    pattern = BossPattern([_volley(BossRingShape(4, 15, BULLET), mount, every=1)])
    piece = _Piece()
    pattern.step(ctx, 0.01, _sources(piece))
    assert len(ctx.bullets) == 4
    assert mount.turret is not None
    pattern.step(ctx, 0.98, _sources(piece))
    pattern.turn_turrets(ctx, 0.01, _sources(piece))
    # Nearly ready for its next ring: nearly a turn of 15 degrees on.
    assert mount.turret.aim == pytest.approx(15 * DEG, abs=0.5 * DEG)
    pattern.step(ctx, 0.02, _sources(piece))
    headings = sorted(h % (2 * math.pi) for _, _, h, _ in ctx.bullets[4:])
    expected = sorted(mount.heading_of(piece, b) % (2 * math.pi) for b in mount.barrels)
    assert headings == pytest.approx(expected)


def test_boss_29_a_burst_from_a_turret_waits_for_it_then_its_barrels_take_turns() -> None:
    ctx = _ctx(player=(400, 300))
    mount = _twin(_turret(90))
    pattern = BossPattern([_volley(BossBurstShape(3, 0.1, BULLET), mount)])
    piece = _Piece()
    pattern.step(ctx, 0.01, _sources(piece))
    assert ctx.bullets == []
    # A quarter turn at 90 degrees a second: on aim at the player, to the right.
    pattern.turn_turrets(ctx, 1.0, _sources(piece))
    assert mount.turret is not None
    assert mount.turret.aim == pytest.approx(-math.pi / 2)
    pattern.step(ctx, 0.01, _sources(piece))
    pattern.step(ctx, 0.1, _sources(piece))
    pattern.step(ctx, 0.1, _sources(piece))
    assert len(ctx.bullets) == 3
    assert [b.fired_at is not None for b in mount.barrels] == [True, True]
    for x, y, heading, _ in ctx.bullets:
        assert heading == pytest.approx(math.pi / 2)
        assert x > piece.x + 9
        assert y == pytest.approx(piece.y + 2) or y == pytest.approx(piece.y - 2)


def test_boss_29_a_single_aimed_shot_from_a_turret_is_held_until_it_points_its_way() -> None:
    ctx = _ctx(player=(400, 300))
    mount = _twin(_turret(45))
    pattern = BossPattern([_volley(BossAimedShape(1, 0, BULLET), mount)])
    piece = _Piece()
    pattern.step(ctx, 0.01, _sources(piece))
    pattern.turn_turrets(ctx, 1.0, _sources(piece))
    pattern.step(ctx, 0.01, _sources(piece))
    assert ctx.bullets == []
    pattern.turn_turrets(ctx, 1.0, _sources(piece))
    pattern.step(ctx, 0.01, _sources(piece))
    assert len(ctx.bullets) == 1
    assert ctx.bullets[0][2] == pytest.approx(math.pi / 2)


def _sweep(ctx: FakeContext, pattern: BossPattern, piece: _Piece, dt: float) -> None:
    """Turn the turrets, then fire: a boss's step (BOSS-58: they turn before it fires)."""
    pattern.turn_turrets(ctx, dt, _sources(piece))
    pattern.step(ctx, dt, _sources(piece))


def test_boss_58_a_turret_sweeps_its_aimed_spread_one_bullet_at_a_time() -> None:
    """A sweep may fire more bullets than its turret has barrels; they take turns."""
    ctx = _ctx()
    mount = _twin(_turret())
    pattern = BossPattern([_volley(BossAimedShape(3, 10, BULLET), mount)])
    piece = _Piece()
    pattern.step(ctx, 0.01, _sources(piece))
    # Its first bullet goes 10 degrees off the player: not until the turret points there.
    assert ctx.bullets == []
    for _ in range(3):
        _sweep(ctx, pattern, piece, SWEEP_GAP)
    headings = [h for _, _, h, _ in ctx.bullets]
    assert headings == pytest.approx([DOWN - 10 * DEG, DOWN, DOWN + 10 * DEG])
    assert [x for x, _, _, _ in ctx.bullets][1] == pytest.approx(102)
    # Done: the turret now aims at the player for its next volley.
    _sweep(ctx, pattern, piece, SWEEP_GAP)
    assert len(ctx.bullets) == 3
    assert mount.turret is not None
    assert mount.turret.aim == pytest.approx(0)


def test_boss_58_a_sweep_s_bullets_are_at_least_the_sweep_gap_apart() -> None:
    ctx = _ctx()
    mount = _twin(_turret())
    pattern = BossPattern([_volley(BossAimedShape(2, 0, BULLET), mount)])
    piece = _Piece()
    pattern.step(ctx, 0.01, _sources(piece))
    assert len(ctx.bullets) == 1
    _sweep(ctx, pattern, piece, SWEEP_GAP / 2)
    assert len(ctx.bullets) == 1
    _sweep(ctx, pattern, piece, SWEEP_GAP / 2)
    assert len(ctx.bullets) == 2
    _assert_from_barrels(ctx, [(mount, 0), (mount, 1)])


def test_boss_58_a_turret_sweeps_a_fan_round_its_preset_heading() -> None:
    ctx = _ctx()
    mount = _twin(_turret())
    pattern = BossPattern([_volley(BossFanShape(30, 2, 20, BULLET), mount)])
    piece = _Piece()
    pattern.step(ctx, 0.01, _sources(piece))
    for _ in range(3):
        _sweep(ctx, pattern, piece, SWEEP_GAP)
    # A preset heading of 30 degrees is 30 degrees towards the right of the screen from down.
    headings = [h for _, _, h, _ in ctx.bullets]
    assert headings == pytest.approx([DOWN - 40 * DEG, DOWN - 20 * DEG])


@pytest.mark.parametrize(("up", "heights"), [(True, [4, 4]), (False, [0, 0])])
def test_wpn_09_missiles_leave_the_mount_s_ports_up_or_flat(up: bool, heights: list[float]) -> None:
    """Also BOSS-58, WPN-07: one missile a port, in turn."""
    ctx = _ctx(player=(100, 0))
    mount = _rack()
    pattern = BossPattern([_volley(BossMissilesShape(2, 20, MISSILE, up), mount)])
    pattern.step(ctx, 0.01, _sources(_Piece()))
    assert [(x, y) for x, y, _, _ in ctx.missiles] == [(97, 300), (103, 300)]
    assert ctx.missile_heights == heights
    headings = [h for _, _, h, _ in ctx.missiles]
    if up:
        # Climbing, each drifts off its side of the block (WPN-09).
        assert headings == pytest.approx([-math.pi / 2, math.pi / 2])
    else:
        to_player = [math.atan2(100 - x, 0 - 300) for x in (97, 103)]
        assert headings == pytest.approx([to_player[0] - 10 * DEG, to_player[1] + 10 * DEG])


def test_boss_31_a_mount_s_laser_leaves_its_lens_and_its_turret_follows_the_player() -> None:
    """Also BOSS-58: its beam leaves the lens along the barrel."""
    ctx = _ctx(player=(400, 300))
    mount = BossMount(BossMountSpec("eye", "core", "laser", [[0, -10, 7, 0]], _turret(90)))
    pattern = BossPattern([_volley(BossLaserShape(LASER), mount)])
    piece = _Piece()
    pattern.step(ctx, 0.01, _sources(piece))
    owner, spec = ctx.lasers[0]
    assert spec is LASER
    assert isinstance(owner, MountLaserOwner)
    assert (owner.emitter.x, owner.emitter.y) == (100, 290)
    # During its warning line, its turret turns towards the player; its beam with it.
    pattern.turn_turrets(ctx, 0.5, _sources(piece))
    assert owner.heading == pytest.approx(DOWN - 45 * DEG)
    assert owner.emitter.x > 100


def test_boss_25_a_launch_from_a_piece_with_a_mount_still_launches_from_the_piece() -> None:
    ctx = _ctx()
    launched: list[tuple[float, float]] = []

    def launch(x: float, y: float) -> list[Any]:
        launched.append((x, y))
        return ["drone"]

    pattern = BossPattern([_volley(BossLaunchShape(launch), _twin())])
    pattern.step(ctx, 0.01, _sources(_Piece()))
    assert launched == [(100, 300)]
    assert ctx.spawned == ["drone"]
    assert ctx.bullets == []


def test_boss_29_each_turret_mount_turns_on_its_own() -> None:
    """Two volleys of one mount share its turret; a fixed mount has none to turn."""
    ctx = _ctx(player=(400, 300))
    left = _twin(_turret(90))
    right = _twin(_turret(45))
    fixed = _twin()
    pattern = BossPattern([
        _volley(BossAimedShape(1, 0, BULLET), left, first=5),
        _volley(BossBurstShape(2, 0.1, BULLET), left, first=6),
        _volley(BossAimedShape(1, 0, BULLET), right, first=5),
        _volley(BossAimedShape(1, 0, BULLET), fixed, first=5),
    ])
    pattern.turn_turrets(ctx, 0.5, _sources(_Piece()))
    assert left.turret is not None
    assert right.turret is not None
    assert left.turret.aim == pytest.approx(-45 * DEG)
    assert right.turret.aim == pytest.approx(-22.5 * DEG)


def _state(sweep: int) -> _VolleyState:
    state = _VolleyState(0, GunMuzzles(None, None))
    state.sweep = sweep
    state.sweep_centre = 0.25
    return state


def test_boss_58_only_a_fan_or_an_aimed_spread_sweeps() -> None:
    """A sweep's aim stays at its middle for any other shape, and no other shape fires one."""
    ring = BossRingShape(4, 15, BULLET)
    assert _sweep_aim(ring, _state(2)) == 0.25
    ctx = _ctx()
    state = _state(2)
    mount = _twin(_turret())
    _step_sweep(ctx, _volley(ring, mount), state, _Piece(), 1.0)  # type: ignore[arg-type]
    assert ctx.bullets == []
    assert state.sweep == 2


def test_boss_58_a_mount_fires_nothing_for_a_launch() -> None:
    ctx = _ctx()
    state = _state(0)
    shape = BossLaunchShape(lambda _x, _y: [])
    _fire_mount(ctx, _twin(), shape, state, _Piece())  # type: ignore[arg-type]
    assert (ctx.bullets, ctx.missiles, ctx.lasers, ctx.spawned) == ([], [], [], [])
