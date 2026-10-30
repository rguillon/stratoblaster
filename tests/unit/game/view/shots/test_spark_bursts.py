"""Unit tests of `src/game/view/shots/spark_bursts.py`."""

import math
from types import SimpleNamespace

import pytest

from core.math.rng import create_rng
from game.view.shots.spark_bursts import SparkBursts

OPTIONS = SimpleNamespace(
    spreadDeg=30,
    count=5,
    speed=[100, 200],
    life=[0.2, 0.4],
    length=[4, 8],
    twinkleHz=[10, 20],
    drag=3.0,
    twinkle=0.5,
)


def bursts(seed: int = 1) -> SparkBursts:
    return SparkBursts(OPTIONS, create_rng(seed))


def test_p03_r01_a_burst_throws_count_sparks_from_the_hit():
    b = bursts()
    b.emit(10.0, 20.0)
    assert b.count == OPTIONS.count
    spots = b.step(0.0)
    assert len(spots) == OPTIONS.count
    assert all(s.x == pytest.approx(10.0) and s.y == pytest.approx(20.0) for s in spots)


def test_p03_r01_sparks_fly_back_from_the_hit_within_the_spread():
    b = bursts(seed=3)
    b.emit(0.0, 0.0)
    spread = math.radians(OPTIONS.spreadDeg)
    # Headings are measured from +Y: sparks thrown back fly down, within the spread of -Y.
    for s in b.step(0.0):
        assert abs(s.heading) >= math.pi - spread - 1e-9


def test_p03_r01_sparks_move_and_slow_down_with_drag():
    b = bursts()
    b.emit(0.0, 0.0)
    before = [(s.vx, s.vy) for s in b._sparks]
    b.step(0.1)
    after = [(s.vx, s.vy) for s in b._sparks]
    for (vx0, vy0), (vx1, vy1) in zip(before, after, strict=True):
        assert abs(vx1) < abs(vx0)
        assert abs(vy1) < abs(vy0)
        assert vx1 == pytest.approx(vx0 * math.exp(-OPTIONS.drag * 0.1))


def test_p03_r01_a_spark_fades_and_shrinks_over_its_life():
    b = bursts()
    b.emit(0.0, 0.0)
    early = b.step(0.01)
    late = b.step(0.1)
    assert all(s.brightness <= 1 for s in early + late)
    assert max(s.length_ for s in late) < max(s.length_ for s in early)


def test_p03_r01_sparks_die_after_their_life_and_are_removed():
    b = bursts()
    b.emit(0.0, 0.0)
    assert b.step(OPTIONS.life[1] + 1) == []
    assert b.count == 0


def test_p03_r01_bursts_accumulate_until_their_sparks_die():
    b = bursts()
    b.emit(0.0, 0.0)
    b.emit(5.0, 5.0)
    assert b.count == 2 * OPTIONS.count
    b.step(0.01)
    assert b.count == 2 * OPTIONS.count


def test_p03_r01_a_spark_is_a_streak_along_its_motion():
    b = bursts()
    b.emit(0.0, 0.0)
    spot = b.step(0.0)[0]
    assert spot.length_ > 0
    assert 0 < spot.brightness <= 1
