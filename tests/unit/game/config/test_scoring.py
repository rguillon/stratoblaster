# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/game/config/scoring.py`."""

import pytest

from game.config.enemies import ENEMY_CONFIG
from game.config.enemies_elite import ELITE_CONFIG
from game.config.enemies_veteran import VETERAN_CONFIG
from game.config.scoring import SCORING, boss_part_points


def test_game_score_04_scoring_constants_match_the_design() -> None:
    """Also GAME-BONUS-10 (the overflow points)."""
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
def test_game_score_04_a_destroyed_part_scores_a_tenth_of_the_boss_rounded_to_ten(
    boss_points: float, expected: float
) -> None:
    assert boss_part_points(boss_points) == expected


def test_game_score_04_part_points_are_always_a_multiple_of_round_to() -> None:
    for points in range(0, 9000, 37):
        assert boss_part_points(points) % SCORING.roundTo == 0


def test_game_score_03_no_kind_scores_less_than_a_kind_with_half_its_health_or_less() -> None:
    """Over every enemy kind, a kind with at least twice another's health never scores less than it.

    The kinds are those of the game's basic, veteran and elite rosters (GAME-SCORE-03).
    """
    kinds = [
        *ENEMY_CONFIG.values(),
        *VETERAN_CONFIG.values(),
        *ELITE_CONFIG.values(),
    ]
    stats = [(kind["stats"]["health"], kind["stats"]["points"]) for kind in kinds]
    assert len(stats) == 22
    for health, points in stats:
        for other_health, other_points in stats:
            if health >= 2 * other_health:
                assert points >= other_points, (health, other_health)
