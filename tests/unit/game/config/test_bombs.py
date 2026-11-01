"""Unit tests of `src/game/config/bombs.py`."""

from game.config.bombs import BOMB_RULES
from game.config.enemies import ENEMY_CONFIG


def test_game_bomb_01_the_player_starts_with_three_bombs_dealing_damage_for_one_second() -> None:
    """Also GAME-BOMB-04 (the damage) and GAME-BOMB-06 (the second the ship is safe)."""
    assert BOMB_RULES.start == 3
    assert BOMB_RULES.damage == 100
    assert BOMB_RULES.seconds == 1


def test_game_bomb_04_one_bomb_destroys_every_world_1_kind_up_to_the_rocketeer() -> None:
    assert ENEMY_CONFIG.rocketeer.stats.health <= BOMB_RULES.damage
