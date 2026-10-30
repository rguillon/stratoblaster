"""Unit tests of `src/config/game_controls.py`."""

from config.game_controls import GAME_CONTROLS_CONFIG


def test_p06_r02_fire_keys_are_bound_and_do_not_switch_or_bomb() -> None:
    config = GAME_CONTROLS_CONFIG
    assert "Space" in config.fire_keys
    assert not set(config.fire_keys) & set(config.switch_keys)
    assert not set(config.fire_keys) & set(config.bomb_keys)


def test_p11_r06_bomb_keys_and_buttons_are_bound() -> None:
    config = GAME_CONTROLS_CONFIG
    assert "KeyR" in config.bomb_keys
    assert "ShiftLeft" in config.bomb_keys
    assert config.bomb_buttons
    assert not set(config.bomb_buttons) & set(config.fire_buttons)


def test_p06_r02_the_dpad_buttons_are_four_distinct_indices() -> None:
    dpad = GAME_CONTROLS_CONFIG.dpad
    assert len({dpad.up, dpad.down, dpad.left, dpad.right}) == 4


def test_p06_r02_the_stick_dead_zone_is_a_fraction_of_its_range() -> None:
    stick = GAME_CONTROLS_CONFIG.stick
    assert 0 < stick.dead_zone < 1
    assert {stick.x_axis, stick.y_axis} == {0, 1}


def test_gd10_acceleration_is_a_short_positive_time() -> None:
    assert 0 < GAME_CONTROLS_CONFIG.acceleration_seconds < 1
