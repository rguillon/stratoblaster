"""Unit tests of `src/game/config/enemy_look_elite.py`."""

from game.config.enemy_look_elite import ELITE_NEON


def test_p05_r19_every_elite_kind_has_a_neon_colour_in_range() -> None:
    for name, color in ELITE_NEON.items():
        assert len(color) == 3, name
        assert all(0 <= c <= 1 for c in color), name
