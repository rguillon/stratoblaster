"""Unit tests of `src/game/config/readability.py`."""

from core.math.color import in_family
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


def test_p14_r02_tones_are_fractions_and_the_background_is_dark() -> None:
    assert all(0 < tone <= 1 for tone in READABILITY.tones.values())
    assert 0 < READABILITY.backgroundMaxLuminance < 0.5


def test_p14_r02_contrast_thresholds_are_positive() -> None:
    assert READABILITY.minObjectContrast > 0
    assert READABILITY.minBulletContrast >= READABILITY.minObjectContrast
    assert 0 < READABILITY.effectMaxScreenShare <= 1
    assert 0 < READABILITY.effectMaxDuration < 1
