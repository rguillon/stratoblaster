"""Unit tests of `src/game/config/readability.py`."""

from game.config.readability import READABILITY


def test_p14_r02_each_gameplay_family_has_a_hue_window_and_a_saturation_floor() -> None:
    families = READABILITY.families
    assert set(families.keys()) == {"player", "enemy", "enemyShot", "pickup"}
    for name, family in families.items():
        assert 0 <= family["from"] < 360, name
        assert 0 <= family["to"] < 360, name
        assert 0 < family.minSaturation <= 1, name


def test_p14_r02_the_enemy_family_wraps_round_red() -> None:
    enemy = READABILITY.families.enemy
    assert enemy["from"] > enemy["to"]


def test_p14_r02_families_do_not_share_their_hues() -> None:
    windows = {
        name: (family["from"], family["to"]) for name, family in READABILITY.families.items()
    }
    assert windows["player"] != windows["enemy"] != windows["pickup"]


def test_p14_r02_tones_are_fractions_and_the_background_is_dark() -> None:
    assert all(0 < tone <= 1 for tone in READABILITY.tones.values())
    assert 0 < READABILITY.backgroundMaxLuminance < 0.5


def test_p14_r02_contrast_thresholds_are_positive() -> None:
    assert READABILITY.minObjectContrast > 0
    assert READABILITY.minBulletContrast >= READABILITY.minObjectContrast
    assert 0 < READABILITY.effectMaxScreenShare <= 1
    assert 0 < READABILITY.effectMaxDuration < 1
