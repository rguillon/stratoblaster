"""Unit tests of `src/game/config/enemy_look.py`."""

import pytest

from core.math.color import in_family, snap_to_hues
from game.config.enemies_veteran import VETERAN_NEON
from game.config.enemy_look import ENEMY_LOOK, glow, laser_palette, times, whiter
from game.config.readability import READABILITY


def test_gfx_shot_10_times_scales_each_channel() -> None:
    """The shades of a bullet's body and halo."""
    assert times([1, 2, 3], 0.5) == pytest.approx([0.5, 1, 1.5])


def test_gfx_shot_10_whiter_moves_each_channel_towards_one() -> None:
    """The whiter swirls of a bullet, and a laser's white-hot core (GFX-SHOT-17)."""
    assert whiter([0, 0.5, 1], 0.5) == pytest.approx([0.5, 0.75, 1])
    assert whiter([0.2, 0.3, 0.4], 0) == pytest.approx([0.2, 0.3, 0.4])


def test_gfx_shot_15_glow_is_core_mid_rim_and_black_at_the_edge() -> None:
    """The enemy missile's flame."""
    assert glow([1, 1, 1], [0.5, 0.5, 0.5], [0, 0, 1]) == [
        [1, 1, 1],
        [0.5, 0.5, 0.5],
        [0, 0, 1],
        [0, 0, 0],
    ]


def test_gfx_shot_17_laser_palette_has_warning_beam_and_emitter_colours() -> None:
    """Also BOSS-32 (a boss's lasers in its own colour)."""
    palette = laser_palette([1, 0, 0])
    assert palette.warning[0] == [1, 0, 0]
    assert palette.beam[1] == [1, 0, 0]
    assert palette.emitter[-1] == [0, 0, 0]


def test_enm_06_enemy_look_has_the_effect_sections_the_renderer_reads() -> None:
    for section in ("hull", "neon", "bullets", "laser", "missile", "blasts"):
        assert ENEMY_LOOK[section] is not None, section


@pytest.mark.parametrize("style", list(ENEMY_LOOK.bullets.styles.keys()))
def test_gfx_shot_11_every_bullet_style_is_in_the_enemy_shots_family(style: str) -> None:
    """Also GFX-ART-07, GFX-READ-04."""
    rim = ENEMY_LOOK.bullets.styles[style].halo[0]
    assert in_family(rim, READABILITY.families.enemyShot), style


def test_enm_mortar_03_every_basic_neon_and_the_mortar_are_as_bright_as_the_bright_family() -> None:
    """The bright yellow and green of GFX-ART-05 have a largest channel of 1 (HSV value 1). Each
    basic kind's neon and the Mortar's, once drawn at the enemy hues, keep that brightness."""
    bright = 1.0
    neons = [(kind, color) for kind, color in ENEMY_LOOK.neon.items()]
    neons.append(("mortar", VETERAN_NEON.mortar))
    for kind, color in neons:
        drawn = snap_to_hues(color, READABILITY.enemyHues)
        assert max(drawn) == pytest.approx(bright), kind
