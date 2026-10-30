"""Unit tests of `src/core/systems/boss_pattern.py`."""

import math

import pytest

from core.entities.boss_turret import BossTurret, BossTurretSpec
from core.entities.enemy import EnemyBulletSpec, EnemyBurstSpec, EnemyLaserSpec, EnemyMissileSpec
from core.entities.muzzle import PlanePoint, RaisedPoint
from core.systems.boss_pattern import (
    BossAimedShape,
    BossBurstShape,
    BossFanShape,
    BossLaserShape,
    BossLaunchShape,
    BossMissilesShape,
    BossPattern,
    BossRingShape,
    BossVolley,
    pattern_signature,
)

DEG = math.pi / 180

DOWN = math.pi

TO_PLAYER = math.pi / 2

BULLET = EnemyBulletSpec(10, 1, "round")

MISSILE = EnemyMissileSpec(5, 90, 1, 1, 3, "rocket")

LASER = EnemyLaserSpec(1, 1, 2, "beam")


class _Ctx:
    """What a volley fires with: records every shot."""

    def __init__(self, fire_rate: float = 1.0, player: tuple[float, float] = (100, 0)) -> None:
        self.fire_rate = fire_rate
        self.player_x, self.player_y = player
        self.bullets: list[tuple[float, float, float, EnemyBulletSpec]] = []
        self.missiles: list[tuple[float, float, float, EnemyMissileSpec]] = []
        self.lasers: list[tuple[object, EnemyLaserSpec]] = []
        self.spawned: list[object] = []

    def seen(self, point: RaisedPoint) -> PlanePoint:
        return PlanePoint(point.x, point.y)

    def fire_bullet(self, x: float, y: float, heading: float, spec: EnemyBulletSpec) -> None:
        self.bullets.append((x, y, heading, spec))

    def fire_missile(self, x: float, y: float, heading: float, spec: EnemyMissileSpec) -> None:
        self.missiles.append((x, y, heading, spec))

    def fire_laser(self, owner: object, spec: EnemyLaserSpec) -> None:
        self.lasers.append((owner, spec))

    def spawn(self, enemy: object) -> None:
        self.spawned.append(enemy)


class _Src:
    """A piece of a boss: where it is, its turret if any; it places its muzzles (`MuzzleSource`)."""

    def __init__(
        self,
        x: float = 0,
        y: float = 0,
        heading: float = DOWN,
        turret: BossTurret | None = None,
    ) -> None:
        self.x = x
        self.y = y
        self.heading = heading
        self.gone = False
        self.health = 10
        self.turret = turret

    @property
    def emitter(self) -> PlanePoint:
        return PlanePoint(self.x, self.y)

    def place(self, muzzle, on_turret=False):  # type: ignore[no-untyped-def]
        mx, my, mh = muzzle
        return RaisedPoint(self.x + mx, self.y + my, mh)


def _sources(parts: dict[str, _Src]):  # type: ignore[no-untyped-def]
    return parts.get


def _volley(shape: object, from_: str = "core", every: float = 10, **kwargs: object) -> BossVolley:
    return BossVolley(from_, every, shape, **kwargs)  # type: ignore[arg-type]


def _aimed(count: int = 1, spacing: float = 0) -> BossAimedShape:
    return BossAimedShape(count, spacing, BULLET)


def _turret(turn_rate: float, laser_rate: float | None = None, x: float = 0) -> BossTurret:
    return BossTurret(BossTurretSpec(x, 0, turn_rate, laser_rate))


def test_p07_r04_a_volley_keeps_its_fields() -> None:
    shape = _aimed()
    volley = BossVolley("arm", 3, shape, [(1, 2, 3)], True, "radar", "core", 0.5)
    assert (volley.from_, volley.every, volley.shape) == ("arm", 3, shape)
    assert (volley.muzzles, volley.turret, volley.needs, volley.after, volley.first) == (
        [(1, 2, 3)],
        True,
        "radar",
        "core",
        0.5,
    )


def test_p07_r04_each_shape_names_its_kind() -> None:
    assert BossAimedShape(1, 0, BULLET).kind == "aimed"
    assert BossFanShape(0, 3, 10, BULLET).kind == "fan"
    assert BossRingShape(4, 15, BULLET).kind == "ring"
    assert BossBurstShape(3, 0.2, BULLET).kind == "burst"
    assert BossMissilesShape(2, 10, MISSILE).kind == "missiles"
    assert BossLaserShape(LASER).kind == "laser"
    assert BossLaunchShape(lambda x, y: []).kind == "launch"


def test_p07_r04_an_aimed_volley_fans_its_bullets_around_the_player() -> None:
    ctx = _Ctx()
    pattern = BossPattern([_volley(_aimed(count=3, spacing=10), first=0)])
    pattern.step(ctx, 0.1, _sources({"core": _Src()}))
    headings = [h for _, _, h, _ in ctx.bullets]
    assert headings == pytest.approx([TO_PLAYER - 10 * DEG, TO_PLAYER, TO_PLAYER + 10 * DEG])


def test_p07_r04_a_volley_fires_once_per_its_interval() -> None:
    ctx = _Ctx()
    pattern = BossPattern([_volley(_aimed(), every=2, first=1)])
    sources = _sources({"core": _Src()})
    pattern.step(ctx, 0.5, sources)
    assert len(ctx.bullets) == 0
    pattern.step(ctx, 0.5, sources)
    assert len(ctx.bullets) == 1
    for _ in range(3):
        pattern.step(ctx, 0.5, sources)
    assert len(ctx.bullets) == 1
    pattern.step(ctx, 0.5, sources)
    assert len(ctx.bullets) == 2


def test_p07_r04_the_fire_rate_speeds_up_the_timers() -> None:
    ctx = _Ctx(fire_rate=2)
    pattern = BossPattern([_volley(_aimed(), every=2, first=1)])
    pattern.step(ctx, 0.5, _sources({"core": _Src()}))
    assert len(ctx.bullets) == 1


def test_p07_r04_a_volley_without_a_first_time_waits_one_interval() -> None:
    pattern = BossPattern([_volley(_aimed(), every=2)])
    assert pattern._states[0].left == 2


def test_p07_r04_a_volley_whose_piece_is_gone_does_not_fire_or_count_down() -> None:
    ctx = _Ctx()
    pattern = BossPattern([_volley(_aimed(), from_="arm", first=0)])
    pattern.step(ctx, 1, _sources({"core": _Src()}))
    assert ctx.bullets == []
    assert pattern._states[0].left == 0


def test_p07_r04_a_volley_needs_its_other_piece_to_stand() -> None:
    ctx = _Ctx()
    pattern = BossPattern([_volley(_aimed(), needs="radar", first=0)])
    pattern.step(ctx, 0.1, _sources({"core": _Src()}))
    assert ctx.bullets == []
    pattern.step(ctx, 0.1, _sources({"core": _Src(), "radar": _Src()}))
    assert len(ctx.bullets) == 1


def test_p07_r04_a_volley_after_a_piece_fires_only_once_that_piece_is_gone() -> None:
    ctx = _Ctx()
    pattern = BossPattern([_volley(_aimed(), after="shield", first=0)])
    pattern.step(ctx, 0.1, _sources({"core": _Src(), "shield": _Src()}))
    assert ctx.bullets == []
    pattern.step(ctx, 0.1, _sources({"core": _Src()}))
    assert len(ctx.bullets) == 1


def test_p07_r04_the_charge_is_how_close_the_next_volley_is() -> None:
    pattern = BossPattern([_volley(_aimed(), every=10)])
    assert pattern.charge == 0
    pattern.step(_Ctx(), 0.5, _sources({"core": _Src()}))
    assert pattern.charge == pytest.approx(0.05)
    pattern._states[0].left = 0
    assert pattern.charge == 1


def test_p07_r04_an_empty_pattern_has_no_charge_and_does_nothing() -> None:
    pattern = BossPattern([])
    pattern.step(_Ctx(), 1, _sources({}))
    pattern.turn_turrets(_Ctx(), 1, _sources({}))
    assert pattern.charge == 0


def test_p07_r04_missiles_are_aimed_like_an_aimed_volley() -> None:
    ctx = _Ctx()
    pattern = BossPattern([_volley(BossMissilesShape(2, 20, MISSILE), first=0)])
    pattern.step(ctx, 0.1, _sources({"core": _Src()}))
    assert len(ctx.missiles) == 2
    assert all(spec is MISSILE for *_, spec in ctx.missiles)
    headings = [h for _, _, h, _ in ctx.missiles]
    assert headings == pytest.approx([TO_PLAYER - 10 * DEG, TO_PLAYER + 10 * DEG])


def test_p07_r04_a_fan_fires_bullets_around_its_preset_heading() -> None:
    ctx = _Ctx()
    pattern = BossPattern([_volley(BossFanShape(0, 3, 10, BULLET), first=0)])
    pattern.step(ctx, 0.1, _sources({"core": _Src()}))
    headings = [h for _, _, h, _ in ctx.bullets]
    assert headings == pytest.approx([DOWN - 10 * DEG, DOWN, DOWN + 10 * DEG])


def test_p07_r04_a_burst_fires_its_bullets_a_gap_apart_aimed_at_the_player() -> None:
    ctx = _Ctx()
    pattern = BossPattern([_volley(BossBurstShape(3, 0.5, BULLET), first=0)])
    sources = _sources({"core": _Src()})
    counts = []
    for _ in range(4):
        before = len(ctx.bullets)
        pattern.step(ctx, 0.25, sources)
        counts.append(len(ctx.bullets) - before)
    assert counts == [1, 1, 0, 1]
    assert all(h == pytest.approx(TO_PLAYER) for _, _, h, _ in ctx.bullets)


def test_p07_r04_a_laser_fires_its_warning_and_beam_and_resets_its_age() -> None:
    ctx = _Ctx()
    source = _Src(turret=_turret(90))
    pattern = BossPattern([_volley(BossLaserShape(LASER), first=0, turret=True)])
    pattern.step(ctx, 0.1, _sources({"core": source}))
    assert len(ctx.lasers) == 1
    owner, spec = ctx.lasers[0]
    assert spec is LASER
    assert owner.heading == pytest.approx(DOWN)
    assert pattern._states[0].laser_age == 0


def test_p07_r04_a_launch_spawns_the_enemies_its_function_gives() -> None:
    ctx = _Ctx()
    seen: list[tuple[float, float]] = []

    def launch(x: float, y: float) -> list[object]:
        seen.append((x, y))
        return ["drone", "drone"]

    pattern = BossPattern([_volley(BossLaunchShape(launch), first=0)])
    pattern.step(ctx, 0.1, _sources({"core": _Src(x=7, y=8)}))
    assert seen == [(7, 8)]
    assert ctx.spawned == ["drone", "drone"]


def test_p07_r04_a_gun_with_muzzles_fires_from_the_muzzle() -> None:
    ctx = _Ctx()
    pattern = BossPattern([_volley(_aimed(), muzzles=[(5, 0, 0)], first=0)])
    pattern.step(ctx, 0.1, _sources({"core": _Src()}))
    x, y, heading, _ = ctx.bullets[0]
    assert (x, y) == pytest.approx((5, 0))
    assert heading == pytest.approx(TO_PLAYER)


def test_p07_r04_the_pattern_keeps_its_volleys_and_one_timer_for_each() -> None:
    volleys = [_volley(_aimed()), _volley(BossLaserShape(LASER), from_="arm")]
    pattern = BossPattern(volleys)
    assert pattern.volleys == volleys
    assert len(pattern._states) == 2


def test_p07_r04_a_volley_on_a_turret_turns_it_towards_the_player() -> None:
    ctx = _Ctx(player=(100, 0))
    turret = _turret(90)
    pattern = BossPattern([_volley(_aimed(), turret=True, first=10)])
    sources = _sources({"core": _Src(turret=turret)})
    pattern.turn_turrets(ctx, 0.5, sources)
    # Straight down to the player on the right: a quarter turn, at 90 deg/s, half a second.
    assert turret.aim == pytest.approx(-45 * DEG)
    pattern.turn_turrets(ctx, 0.5, sources)
    assert turret.aim == pytest.approx(-math.pi / 2)


def test_p07_r04_a_turret_turns_at_most_its_turn_rate() -> None:
    turret = _turret(10)
    pattern = BossPattern([_volley(BossFanShape(90, 1, 0, BULLET), turret=True, first=10)])
    pattern.turn_turrets(_Ctx(), 0.5, _sources({"core": _Src(turret=turret)}))
    assert turret.aim == pytest.approx(-5 * DEG)


def test_p07_r04_a_fan_turret_turns_along_its_heading() -> None:
    turret = _turret(1000)
    pattern = BossPattern([_volley(BossFanShape(90, 1, 0, BULLET), turret=True, first=10)])
    pattern.turn_turrets(_Ctx(), 1, _sources({"core": _Src(turret=turret)}))
    assert turret.aim == pytest.approx(-math.pi / 2)


def test_p07_r04_a_ring_turret_turns_to_the_barrel_nearest_its_next_turn() -> None:
    turret = _turret(1000)
    ctx = _Ctx()
    pattern = BossPattern([_volley(BossRingShape(4, 30, BULLET), turret=True, first=0)])
    sources = _sources({"core": _Src(turret=turret)})
    pattern.step(ctx, 0.5, sources)
    pattern.turn_turrets(ctx, 0.5, sources)
    # The ring's next turn is 30 degrees, 5% of the way to ready: its barrel nearest there.
    assert turret.aim == pytest.approx(1.5 * DEG)


def test_p07_r04_a_laser_turret_aims_at_the_player_slowly_while_the_warning_shows() -> None:
    ctx = _Ctx(player=(100, 0))
    turret = _turret(1000, laser_rate=10)
    pattern = BossPattern([_volley(BossLaserShape(LASER), turret=True, first=0)])
    sources = _sources({"core": _Src(turret=turret)})
    pattern.step(ctx, 0.5, sources)
    pattern.turn_turrets(ctx, 0.5, sources)
    # The laser's turret follows the player at 10 degrees a second.
    assert turret.aim == pytest.approx(-5 * DEG)


def test_p07_r04_a_laser_turret_holds_still_while_the_beam_fires() -> None:
    ctx = _Ctx(player=(100, 0))
    turret = _turret(1000, laser_rate=10)
    pattern = BossPattern([_volley(BossLaserShape(LASER), turret=True, first=0)])
    sources = _sources({"core": _Src(turret=turret)})
    pattern.step(ctx, 0.5, sources)
    pattern.turn_turrets(ctx, 0.5, sources)
    pattern.turn_turrets(ctx, 0.5, sources)
    held = turret.aim
    pattern.turn_turrets(ctx, 0.5, sources)
    assert turret.aim == pytest.approx(held)


def test_p07_r04_a_laser_turret_without_a_laser_rate_uses_its_normal_rate() -> None:
    ctx = _Ctx(player=(100, 0))
    turret = _turret(20)
    pattern = BossPattern([_volley(BossLaserShape(LASER), turret=True, first=0)])
    sources = _sources({"core": _Src(turret=turret)})
    pattern.step(ctx, 0.5, sources)
    pattern.turn_turrets(ctx, 0.5, sources)
    assert turret.aim == pytest.approx(-10 * DEG)


def test_p07_r04_a_turret_is_left_alone_without_a_source_or_a_turret() -> None:
    turret = _turret(90)
    pattern = BossPattern([_volley(_aimed(), turret=True, first=10)])
    pattern.turn_turrets(_Ctx(), 1, _sources({}))
    assert turret.aim == 0
    pattern.turn_turrets(_Ctx(), 1, _sources({"core": _Src(turret=None)}))
    assert turret.aim == 0


def test_p07_r04_a_burst_under_way_decides_where_its_turret_turns() -> None:
    turret = _turret(100000)
    ctx = _Ctx(player=(100, 0))
    fan = _volley(BossFanShape(0, 1, 0, BULLET), turret=True, every=10, first=0.1)
    burst = _volley(BossBurstShape(3, 1, BULLET), turret=True, every=10, first=0)
    pattern = BossPattern([fan, burst])
    sources = _sources({"core": _Src(turret=turret)})
    pattern.step(ctx, 0.2, sources)
    pattern.turn_turrets(ctx, 0.2, sources)
    # The burst is under way, so the turret aims at the player, not along the fan's heading (0).
    assert turret.aim == pytest.approx(-math.pi / 2)


def test_p07_r04_the_soonest_volley_decides_where_a_turret_turns_otherwise() -> None:
    turret = _turret(100000)
    ctx = _Ctx(player=(100, 0))
    soon = _volley(BossFanShape(0, 1, 0, BULLET), turret=True, every=10, first=0.5)
    later = _volley(BossFanShape(90, 1, 0, BULLET), turret=True, every=10, first=5)
    pattern = BossPattern([later, soon])
    pattern.turn_turrets(ctx, 0.1, _sources({"core": _Src(turret=turret)}))
    assert turret.aim == pytest.approx(0)


def test_p07_r04_a_turret_with_no_volley_ready_still_aims_at_the_first_one() -> None:
    turret = _turret(100000)
    pattern = BossPattern([_volley(_aimed(), turret=True, needs="radar", first=10)])
    pattern.turn_turrets(_Ctx(player=(100, 0)), 1, _sources({"core": _Src(turret=turret)}))
    assert turret.aim == pytest.approx(-math.pi / 2)


def test_p07_r04_volleys_from_the_same_turret_share_one_turret_group() -> None:
    pattern = BossPattern(
        [
            _volley(_aimed(), turret=True),
            _volley(_aimed(), from_="arm", turret=True),
            _volley(_aimed(), turret=True),
        ]
    )
    assert [(g.from_, g.volleys) for g in pattern._turrets] == [("core", [0, 2]), ("arm", [1])]


def test_p07_r04_a_turret_aims_from_its_pivot_not_the_piece_centre() -> None:
    ctx = _Ctx(player=(100, 0))
    turret = _turret(100000, x=10)
    pattern = BossPattern([_volley(_aimed(), turret=True, first=10)])
    pattern.turn_turrets(ctx, 1, _sources({"core": _Src(turret=turret)}))
    assert turret.aim == pytest.approx(-math.pi / 2)


def test_p07_r04_a_laser_from_a_turret_gun_follows_the_turned_barrel() -> None:
    ctx = _Ctx()
    turret = _turret(90)
    turret.aim = 0.5
    pattern = BossPattern([_volley(BossLaserShape(LASER), turret=True, first=0)])
    pattern.step(ctx, 0.1, _sources({"core": _Src(heading=0.2, turret=turret)}))
    owner, _ = ctx.lasers[0]
    assert owner.heading == pytest.approx(0.7)
    assert owner.gone is False
    assert owner.health == 10
    assert (owner.emitter.x, owner.emitter.y) == (0, 0)


def test_p07_r04_a_laser_owner_on_a_turret_forwards_its_piece_state() -> None:
    ctx = _Ctx()
    source = _Src(turret=_turret(90))
    pattern = BossPattern([_volley(BossLaserShape(LASER), turret=True, first=0)])
    pattern.step(ctx, 0.1, _sources({"core": source}))
    owner, _ = ctx.lasers[0]
    source.gone = True
    source.health = 4
    assert owner.gone is True
    assert owner.health == 4


def test_p07_r04_a_laser_from_a_piece_without_a_turret_is_a_plain_owner() -> None:
    ctx = _Ctx()
    pattern = BossPattern([_volley(BossLaserShape(LASER), first=0)])
    pattern.step(ctx, 0.1, _sources({"core": _Src()}))
    owner, _ = ctx.lasers[0]
    assert owner.heading == pytest.approx(DOWN)


def test_p07_r04_the_stage_signature_names_only_the_volleys_that_still_fire() -> None:
    volleys = [
        _volley(_aimed(), from_="core"),
        _volley(_aimed(), from_="arm"),
        _volley(_aimed(), from_="core", after="arm"),
    ]
    arm_gone = lambda f: f == "core"  # noqa: E731
    full = pattern_signature(volleys, lambda f: True)
    partial = pattern_signature(volleys, arm_gone)
    assert full != partial
    assert partial == pattern_signature([volleys[0], volleys[2]], arm_gone)
    assert partial != pattern_signature([volleys[0]], arm_gone)


def test_p07_r04_the_signature_does_not_depend_on_the_order_of_the_volleys() -> None:
    a = _volley(_aimed(), from_="core")
    b = _volley(BossFanShape(0, 3, 10, BULLET), from_="arm")
    assert pattern_signature([a, b], lambda f: True) == pattern_signature([b, a], lambda f: True)


def test_p07_r04_the_signature_separates_volleys_that_fire_differently() -> None:
    variants = [
        _volley(_aimed()),
        _volley(_aimed(count=2)),
        _volley(_aimed(), every=11),
        _volley(_aimed(), first=1),
        _volley(_aimed(), muzzles=[(1, 2, 3)]),
        _volley(_aimed(), turret=True),
        _volley(_aimed(), turret=False),
        _volley(_aimed(), needs="radar"),
        _volley(_aimed(), after="shield"),
        _volley(BossAimedShape(1, 0, EnemyBulletSpec(11, 1, "round"))),
        _volley(
            BossAimedShape(1, 0, EnemyBulletSpec(10, 1, "round", EnemyBurstSpec(1, 2, BULLET)))
        ),
        _volley(BossAimedShape(1, 0, EnemyBulletSpec(10, 1, "other"))),
        _volley(BossFanShape(0, 1, 0, BULLET)),
        _volley(BossFanShape(5, 1, 0, BULLET)),
        _volley(BossRingShape(4, 30, BULLET)),
        _volley(BossRingShape(4, 31, BULLET)),
        _volley(BossBurstShape(3, 0.5, BULLET)),
        _volley(BossBurstShape(3, 0.6, BULLET)),
        _volley(BossMissilesShape(2, 5, MISSILE)),
        _volley(BossMissilesShape(2, 5, EnemyMissileSpec(5, 90, 1, 1, 9, "rocket"))),
        _volley(BossLaserShape(LASER)),
        _volley(BossLaserShape(EnemyLaserSpec(1, 1, 2, "beam", True))),
        _volley(BossLaserShape(EnemyLaserSpec(2, 1, 2, "beam"))),
    ]
    signatures = {pattern_signature([v], lambda f: True) for v in variants}
    assert len(signatures) == len(variants)


def test_p07_r04_a_launch_is_named_without_its_function() -> None:
    a = _volley(BossLaunchShape(lambda x, y: []))
    b = _volley(BossLaunchShape(lambda x, y: [object()]))
    text = pattern_signature([a], lambda f: True)
    assert text == pattern_signature([b], lambda f: True)
    assert '"kind":"launch"' in text


def test_p07_r04_the_signature_quotes_its_names() -> None:
    text = pattern_signature([_volley(_aimed())], lambda f: True)
    assert text.startswith('{"from":"core","every":10')
    assert '"style":"round"' in text


def test_p07_r04_a_pattern_with_no_live_volley_has_an_empty_signature() -> None:
    assert pattern_signature([_volley(_aimed(), from_="arm")], lambda f: f == "core") == ""


def test_p07_r04_a_turret_follows_the_laser_still_showing_when_an_older_one_is_over() -> None:
    ctx = _Ctx(player=(100, 0))
    turret = _turret(1000, laser_rate=10)
    pattern = BossPattern(
        [
            _volley(BossLaserShape(LASER), turret=True, first=10),
            _volley(BossLaserShape(LASER), turret=True, first=10),
        ]
    )
    pattern._states[0].laser_age = 100
    pattern._states[1].laser_age = 0
    pattern.turn_turrets(ctx, 0.5, _sources({"core": _Src(turret=turret)}))
    assert turret.aim == pytest.approx(-5 * DEG)


def test_p07_r04_the_soonest_volley_wins_whichever_order_they_are_listed_in() -> None:
    turret = _turret(100000)
    soon = _volley(BossFanShape(90, 1, 0, BULLET), turret=True, every=10, first=0.5)
    later = _volley(BossFanShape(0, 1, 0, BULLET), turret=True, every=10, first=5)
    pattern = BossPattern([soon, later])
    pattern.turn_turrets(_Ctx(), 0.1, _sources({"core": _Src(turret=turret)}))
    assert turret.aim == pytest.approx(-math.pi / 2)


def test_p07_r04_a_turret_for_a_launch_has_no_aim_of_its_own() -> None:
    turret = _turret(100000)
    turret.aim = 0.5
    pattern = BossPattern([_volley(BossLaunchShape(lambda x, y: []), turret=True, first=10)])
    pattern.turn_turrets(_Ctx(), 1, _sources({"core": _Src(turret=turret)}))
    assert turret.aim == pytest.approx(0)
