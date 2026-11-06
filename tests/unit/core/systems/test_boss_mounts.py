# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/core/systems/boss_mounts.py` (BOSS-58)."""

import math

import pytest
from helpers.fakes import FakeContext

from core.entities.boss_turret import BossTurretSpec
from core.entities.muzzle import Muzzle, PlanePoint, RaisedPoint
from core.systems.boss_mounts import BossMount, BossMountSpec, Fire, Launch, MountLaserOwner

DEG = math.pi / 180

DOWN = math.pi


class _AgelessPiece:
    """A boss's piece without a clock of its own (`age`): its barrels recoil from 0."""

    def __init__(self, x: float = 100, y: float = 300, heading: float = DOWN) -> None:
        self.x = x
        self.y = y
        self.heading = heading
        self.gone = False
        self.health = 40.0

    @property
    def emitter(self) -> PlanePoint:
        return PlanePoint(self.x, self.y)

    def place(self, muzzle: Muzzle, _on_turret: bool = False) -> RaisedPoint:
        mx, my, mh = muzzle
        return RaisedPoint(self.x + mx, self.y + my, mh)


class _Piece(_AgelessPiece):
    """A boss's piece a mount is on: where it is, its heading and age; it places its muzzles."""

    def __init__(self, x: float = 100, y: float = 300, heading: float = DOWN) -> None:
        super().__init__(x, y, heading)
        self.age = 2.0


def _twin(turret: BossTurretSpec | None = None) -> BossMount:
    """Return a twin gun: two barrels side by side, 4 px apart, both pointing down."""
    return BossMount(
        BossMountSpec("twin", "core", "gun", [[-2, -10, 5, 0], [2, -10, 5, 0]], turret)
    )


def _rotor(barrels: int = 4) -> BossMount:
    """Return a rotor of `barrels` barrels all round its hub, the first pointing down."""
    entries: list[list[float]] = []
    for k in range(barrels):
        angle = 360 * k / barrels
        a = angle * DEG
        entries.append([-math.sin(a) * 8, -math.cos(a) * 8, 6, angle])
    return BossMount(BossMountSpec("rotor", "core", "gun", entries))


def _rack(ports: list[list[float]]) -> BossMount:
    return BossMount(BossMountSpec("rack", "core", "missile", ports))


def _fire_log(ctx: FakeContext) -> Fire:
    def fire(x: float, y: float, heading: float) -> None:
        ctx.bullets.append((x, y, heading, None))

    return fire


def test_boss_58_a_mount_spec_keeps_its_piece_kind_barrels_and_turret() -> None:
    turret = BossTurretSpec(0, -5, 90)
    spec = BossMountSpec("gun-a", "arm", "gun", [[0, -10, 5, 0]], turret)
    assert (spec.id, spec.piece, spec.kind, spec.barrels, spec.turret) == (
        "gun-a",
        "arm",
        "gun",
        [[0, -10, 5, 0]],
        turret,
    )
    mount = BossMount(spec)
    assert (mount.id, mount.kind, mount.shown_at) == ("gun-a", "gun", None)
    assert mount.turret is not None
    assert BossMount(BossMountSpec("fixed", "core", "gun", [[0, 0, 0, 0]])).turret is None


def test_boss_58_a_fixed_barrel_tip_goes_with_its_piece() -> None:
    mount = _twin()
    tip = mount.tip(_Piece(), mount.barrels[0])
    assert (tip.x, tip.y, tip.height) == (98, 290, 5)
    assert mount.heading_of(_Piece(), mount.barrels[0]) == pytest.approx(DOWN)


def test_boss_29_a_turret_turns_its_barrels_tips_and_their_way_with_it() -> None:
    mount = _twin(BossTurretSpec(0, 0, 90))
    assert mount.turret is not None
    mount.turret.aim = math.pi / 2
    tip = mount.tip(_Piece(), mount.barrels[0])
    # (-2, -10) a quarter turn clockwise on screen round the pivot: (-10, 2).
    assert (tip.x, tip.y) == pytest.approx((90, 302))
    assert mount.heading_of(_Piece(), mount.barrels[0]) == pytest.approx(DOWN + math.pi / 2)


def test_boss_58_a_port_without_an_angle_points_its_piece_s_way() -> None:
    mount = _rack([[0, 0, 3]])
    assert mount.barrels[0].angle is None
    assert mount.heading_of(_Piece(heading=1.0), mount.barrels[0]) == pytest.approx(1.0)


def test_boss_58_twin_barrels_side_by_side_take_turns_and_recoil() -> None:
    """Also WPN-03: each barrel fired is thrown back at its piece's age."""
    ctx = FakeContext()
    mount = _twin()
    piece = _Piece()
    mount.fire(ctx, piece, 1, _fire_log(ctx))
    assert mount.barrels[0].fired_at == 2.0
    assert mount.barrels[1].fired_at is None
    piece.age = 3.0
    mount.fire(ctx, piece, 1, _fire_log(ctx))
    assert mount.barrels[1].fired_at == 3.0
    assert mount.barrels[1].recoil_at(3.0) == 1
    assert [(x, y) for x, y, _, _ in ctx.bullets] == [(98, 290), (102, 290)]
    assert [h for _, _, h, _ in ctx.bullets] == pytest.approx([DOWN, DOWN])


def test_boss_58_a_mount_never_fires_more_bullets_than_it_has_barrels() -> None:
    ctx = FakeContext()
    mount = _twin()
    mount.fire(ctx, _Piece(), 5, _fire_log(ctx))
    assert len(ctx.bullets) == 2
    mount.fire(ctx, _Piece(), 0, _fire_log(ctx))
    assert len(ctx.bullets) == 2


def test_boss_58_of_barrels_pointing_different_ways_the_middle_ones_fire() -> None:
    ctx = FakeContext()
    mount = _rotor(4)
    mount.fire(ctx, _Piece(), 2, _fire_log(ctx))
    assert [b.fired_at for b in mount.barrels] == [None, 2.0, 2.0, None]
    assert [h for _, _, h, _ in ctx.bullets] == pytest.approx([DOWN + math.pi / 2, 2 * math.pi])


def test_boss_58_a_ring_fires_one_bullet_from_each_rotor_barrel() -> None:
    ctx = FakeContext()
    mount = _rotor(4)
    piece = _Piece()
    mount.fire_all(ctx, piece, _fire_log(ctx))
    assert len(ctx.bullets) == 4
    for barrel, (x, y, heading, _) in zip(mount.barrels, ctx.bullets, strict=True):
        tip = mount.tip(piece, barrel)
        assert (x, y) == (tip.x, tip.y)
        assert heading == pytest.approx(mount.heading_of(piece, barrel))
        # Along its barrel: from the hub out through its tip.
        assert math.atan2(x - piece.x, y - piece.y) % (2 * math.pi) == pytest.approx(
            heading % (2 * math.pi)
        )
        assert barrel.fired_at == 2.0


def test_boss_58_a_barrel_of_a_piece_without_a_clock_recoils_from_0() -> None:
    ctx = FakeContext()
    mount = _twin()
    mount.fire_all(ctx, _AgelessPiece(), _fire_log(ctx))
    assert [b.fired_at for b in mount.barrels] == [0, 0]


# One launch: the port's mouth, where it is seen, the missile's heading and its side (WPN-09).
Launched = tuple[RaisedPoint, PlanePoint, float, float]


def _launcher(log: list[Launched]) -> Launch:
    def fire(mouth: RaisedPoint, seen: PlanePoint, heading: float, side: float) -> None:
        log.append((mouth, seen, heading, side))

    return fire


def test_wpn_07_missiles_leave_the_ports_in_turn_in_a_fan_round_the_player() -> None:
    """Also BOSS-58: each port reloads as its missile leaves; WPN-09: it drifts off its side."""
    ctx = FakeContext()
    ctx.player_x, ctx.player_y = 100, 0
    log: list[Launched] = []
    mount = _rack([[-3, 0, 4], [3, 0, 4]])
    mount.launch(ctx, _Piece(), (3, 10), _launcher(log))
    mouths = [mouth for mouth, _, _, _ in log]
    assert [(m.x, m.y, m.height) for m in mouths] == [(97, 300, 4), (103, 300, 4), (97, 300, 4)]
    assert [(seen.x, seen.y) for _, seen, _, _ in log] == [(97, 300), (103, 300), (97, 300)]
    to_player = [math.atan2(100 - m.x, 0 - m.y) for m in mouths]
    assert [h for _, _, h, _ in log] == pytest.approx([
        to_player[0] - 10 * DEG,
        to_player[1],
        to_player[2] + 10 * DEG,
    ])
    # Off to their side of the block: the left port to the left, the right one to the right.
    sides = [side for _, _, _, side in log]
    assert sides == pytest.approx([-math.pi / 2, math.pi / 2, -math.pi / 2])
    assert mount.barrels[0].fired_at == 2.0
    assert mount.barrels[1].fired_at == 2.0


def test_wpn_09_a_lone_silo_s_missile_drifts_its_own_way() -> None:
    log: list[Launched] = []
    _rack([[0, 0, 4]]).launch(FakeContext(), _Piece(), (1, 0), _launcher(log))
    _, _, heading, side = log[0]
    assert side == heading


def test_boss_58_a_mount_without_ports_launches_nothing() -> None:
    log: list[Launched] = []
    _rack([]).launch(FakeContext(), _Piece(), (2, 10), _launcher(log))
    assert log == []


def test_boss_58_a_laser_leaves_its_lens_along_its_barrel_as_the_turret_turns() -> None:
    """Also WPN-06: the laser follows its piece: gone and health are its piece's."""
    mount = BossMount(
        BossMountSpec("eye", "core", "laser", [[0, -10, 7, 0]], BossTurretSpec(0, 0, 45))
    )
    piece = _Piece()
    owner = mount.laser(piece)
    assert isinstance(owner, MountLaserOwner)
    assert (owner.emitter.x, owner.emitter.y) == (100, 290)
    assert owner.heading == pytest.approx(DOWN)
    assert mount.turret is not None
    mount.turret.aim = -math.pi / 2
    assert (owner.emitter.x, owner.emitter.y) == pytest.approx((110, 300))
    assert owner.heading == pytest.approx(math.pi / 2)
    assert (owner.gone, owner.health) == (False, 40.0)
    piece.gone = True
    piece.health = 0
    assert (owner.gone, owner.health) == (True, 0)
