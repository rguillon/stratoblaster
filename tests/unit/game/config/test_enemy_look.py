"""Unit tests of `src/game/config/enemy_look.py`."""

import pytest

from game.config.enemy_look import ENEMY_LOOK, glow, laser_palette, times, whiter


def test_p16_r01_times_scales_each_channel() -> None:
    assert times([1, 2, 3], 0.5) == pytest.approx([0.5, 1, 1.5])


def test_p16_r01_whiter_moves_each_channel_towards_one() -> None:
    assert whiter([0, 0.5, 1], 0.5) == pytest.approx([0.5, 0.75, 1])
    assert whiter([0.2, 0.3, 0.4], 0) == pytest.approx([0.2, 0.3, 0.4])


def test_p16_r01_glow_is_core_mid_rim_and_black_at_the_edge() -> None:
    assert glow([1, 1, 1], [0.5, 0.5, 0.5], [0, 0, 1]) == [
        [1, 1, 1],
        [0.5, 0.5, 0.5],
        [0, 0, 1],
        [0, 0, 0],
    ]


def test_p16_r01_laser_palette_has_warning_beam_and_emitter_colours() -> None:
    palette = laser_palette([1, 0, 0])
    assert palette.warning[0] == [1, 0, 0]
    assert palette.beam[1] == [1, 0, 0]
    assert palette.emitter[-1] == [0, 0, 0]


def test_p16_r01_enemy_look_has_the_effect_sections_the_renderer_reads() -> None:
    for section in ("hull", "neon", "bullets", "laser", "missile", "blasts"):
        assert ENEMY_LOOK[section] is not None, section
