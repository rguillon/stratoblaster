"""Unit tests of `src/game/config/scoring.py`."""

import pytest

from game.config.scoring import SCORING, boss_part_points


def test_p11_r01_scoring_constants_match_the_design() -> None:
    assert SCORING.bossPartShare == pytest.approx(0.1)
    assert SCORING.roundTo == 10
    assert SCORING.overflow.life == 5000
    assert SCORING.overflow.bomb == 2000


@pytest.mark.parametrize(
    ("boss_points", "expected"),
    [
        (1000, 100),
        (1230, 120),
        (1250, 130),  # 125 rounds half up to 130
        (960, 100),
        (0, 0),
    ],
)
def test_p11_r01_a_destroyed_part_scores_a_tenth_of_the_boss_rounded_to_ten(
    boss_points: float, expected: float
) -> None:
    assert boss_part_points(boss_points) == expected


def test_p11_r01_part_points_are_always_a_multiple_of_round_to() -> None:
    for points in range(0, 9000, 37):
        assert boss_part_points(points) % SCORING.roundTo == 0
