"""Unit tests of `src/game/config/readability.py`."""

import pytest

from core.math.color import in_family
from game.config.bonus_look import BONUS_LOOK
from game.config.enemy_look import ENEMY_LOOK
from game.config.readability import READABILITY

YELLOW = (1, 1, 0)
LIME = (0.5, 1, 0)
GREEN = (0, 1, 0)


def test_p14_r02_each_gameplay_family_has_a_hue_window_and_a_saturation_floor() -> None:
    families = READABILITY.families
    assert set(families.keys()) == {"player", "enemy", "enemyShot", "pickup"}
    for name, family in families.items():
        assert 0 <= family["from"] < 360, name
        assert 0 <= family["to"] < 360, name
        assert 0 < family.minSaturation <= 1, name


def _hues(family: dict[str, float]) -> set[int]:
    """The whole degrees `family`'s hue range covers."""
    span = (family["to"] - family["from"] + 360) % 360
    return {(family["from"] + d) % 360 for d in range(int(span) + 1)}


def test_d231_enemies_and_bosses_are_yellow_to_green_with_no_pink() -> None:
    enemy = READABILITY.families.enemy
    assert all(in_family(color, enemy) for color in (YELLOW, LIME, GREEN))
    for pink in ((1, 0, 1), (1, 0.2, 0.6), (0.6, 0.2, 1), (1, 0, 0.1)):
        assert not in_family(pink, enemy)


def test_d231_the_enemies_two_hues_are_a_yellow_and_a_green_in_their_family() -> None:
    yellow, green = READABILITY.enemyHues
    assert 55 <= yellow <= 65
    assert 115 <= green <= 135
    family = READABILITY.families.enemy
    for hue in (yellow, green):
        assert (hue - family["from"]) % 360 <= (family["to"] - family["from"]) % 360


def test_p14_r02_families_do_not_share_their_hues() -> None:
    families = READABILITY.families
    names = list(families.keys())
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            assert not _hues(families[a]) & _hues(families[b]), (a, b)


def _saturated(color: list[float]) -> bool:
    high = max(color)
    return high > 0 and (high - min(color)) / high >= 0.5


@pytest.mark.parametrize("style", list(ENEMY_LOOK.bullets.styles.keys()))
def test_p14_r02_every_bullet_style_is_in_the_enemy_shots_family(style: str) -> None:
    rim = ENEMY_LOOK.bullets.styles[style].halo[0]
    assert in_family(rim, READABILITY.families.enemyShot), style


def test_d231_the_bonuses_colours_are_in_the_pickups_violet_family() -> None:
    colours = [
        BONUS_LOOK.frame,
        BONUS_LOOK.chevrons,
        BONUS_LOOK.flash.color,
        *BONUS_LOOK.halo.colors[:3],
        BONUS_LOOK.life.rim,
        BONUS_LOOK.life.heart,
        *BONUS_LOOK.life.halo[:3],
        BONUS_LOOK.bomb.shell,
        BONUS_LOOK.bomb.highlight,
        *BONUS_LOOK.bomb.halo[:3],
    ]
    for colour in colours:
        # Pale ones (a highlight) belong to no family; the others to the pickups'.
        if _saturated(colour):
            assert in_family(colour, READABILITY.families.pickup), colour


def test_p14_r02_tones_are_fractions_and_the_background_is_dark() -> None:
    assert all(0 < tone <= 1 for tone in READABILITY.tones.values())
    assert 0 < READABILITY.backgroundMaxLuminance < 0.5


def test_p14_r02_contrast_thresholds_are_positive() -> None:
    assert READABILITY.minObjectContrast > 0
    assert READABILITY.minBulletContrast >= READABILITY.minObjectContrast
    assert 0 < READABILITY.effectMaxScreenShare <= 1
    assert 0 < READABILITY.effectMaxDuration < 1
