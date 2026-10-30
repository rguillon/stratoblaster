"""Unit tests of `src/input/game_controls.py`."""

import math

import pytest
from helpers.gamepads import FakeGamepad

from config.game_controls import GAME_CONTROLS_CONFIG
from input.game_controls import GameControls

MAX_SPEED = 100.0
DT = 0.1  # reach = 10 logical pixels per step


def make_controls(pads: list | None = None) -> GameControls:
    source = (lambda: pads) if pads is not None else None
    return GameControls(GAME_CONTROLS_CONFIG, source)


def test_p06_r02_space_shoots_while_held() -> None:
    controls = make_controls()
    assert controls.key("Space", True) is True
    assert controls.read(DT, MAX_SPEED).fire is True
    controls.key("Space", False)
    assert controls.read(DT, MAX_SPEED).fire is False


def test_p06_r02_arrow_keys_move_the_ship() -> None:
    controls = make_controls()
    controls.key("ArrowLeft", True)
    move = controls.read(DT, MAX_SPEED).move
    assert move.x == -1
    assert move.y == 0


def test_p06_r02_keys_outside_the_controls_are_not_claimed() -> None:
    controls = make_controls()
    assert controls.key("KeyZ", True) is False


def test_p06_r02_switch_weapon_counts_one_press_however_long_it_is_held() -> None:
    controls = make_controls()
    controls.key("KeyE", True)
    controls.key("KeyE", True)  # browser auto-repeat
    assert controls.read(DT, MAX_SPEED).switch_weapon is True
    assert controls.read(DT, MAX_SPEED).switch_weapon is False
    controls.key("KeyE", False)
    controls.key("KeyE", True)
    assert controls.read(DT, MAX_SPEED).switch_weapon is True


def test_p11_r06_bomb_keys_r_and_left_shift_set_a_bomb_off_once_per_press() -> None:
    controls = make_controls()
    controls.key("ShiftLeft", True)
    assert controls.read(DT, MAX_SPEED).bomb is True
    assert controls.read(DT, MAX_SPEED).bomb is False
    controls.key("ShiftLeft", False)
    controls.key("KeyR", True)
    assert controls.read(DT, MAX_SPEED).bomb is True


def test_p11_r06_the_on_screen_bomb_button_is_one_bomb_per_tap() -> None:
    controls = make_controls()
    controls.bomb()
    controls.bomb()
    assert controls.read(DT, MAX_SPEED).bomb is True
    assert controls.read(DT, MAX_SPEED).bomb is True
    assert controls.read(DT, MAX_SPEED).bomb is False


def test_p06_r02_touch_fire_button_shoots_while_held() -> None:
    controls = make_controls()
    controls.set_touch_fire(True)
    assert controls.read(DT, MAX_SPEED).fire is True
    controls.set_touch_fire(False)
    assert controls.read(DT, MAX_SPEED).fire is False


def test_p06_r02_a_drag_is_followed_at_most_at_full_speed_and_the_rest_waits() -> None:
    controls = make_controls()
    controls.drag(30, 40)  # 50 px: the ship covers 10 px this step
    first = controls.read(DT, MAX_SPEED).move
    assert first.x == pytest.approx(0.6)
    assert first.y == pytest.approx(0.8)
    second = controls.read(DT, MAX_SPEED).move
    assert second.x == pytest.approx(0.6)
    assert second.y == pytest.approx(0.8)


def test_p06_r02_a_short_drag_is_used_up_in_one_step() -> None:
    controls = make_controls()
    controls.drag(3, 4)  # 5 px, less than the 10 px reach
    move = controls.read(DT, MAX_SPEED).move
    assert move.x == pytest.approx(0.3)
    assert move.y == pytest.approx(0.4)
    assert controls.read(DT, MAX_SPEED).move.x == 0


def test_p06_r02_no_time_or_speed_means_the_drag_is_not_spent() -> None:
    controls = make_controls()
    controls.drag(3, 4)
    assert controls.read(0, MAX_SPEED).move.x == 0
    assert controls.read(DT, MAX_SPEED).move.x == pytest.approx(0.3)


def test_p06_r02_clear_lets_go_of_everything() -> None:
    controls = make_controls()
    controls.key("ArrowUp", True)
    controls.key("Space", True)
    controls.key("KeyE", True)
    controls.bomb()
    controls.set_touch_fire(True)
    controls.drag(10, 10)
    controls.clear()
    state = controls.read(DT, MAX_SPEED)
    assert state.move.x == 0
    assert state.move.y == 0
    assert state.fire is False
    assert state.switch_weapon is False
    assert state.bomb is False


def test_p06_r02_left_stick_moves_and_is_ignored_inside_its_dead_zone() -> None:
    pad = FakeGamepad().tilt(0.1, 0.1)  # 0.14 < dead zone 0.2
    controls = make_controls([pad])
    assert controls.read(DT, MAX_SPEED).move.x == 0
    pad.tilt(0.6, 0.0)
    move = controls.read(DT, MAX_SPEED).move
    assert move.x == pytest.approx(0.6)
    assert move.y == 0


def test_p06_r02_stick_up_is_positive_y() -> None:
    pad = FakeGamepad().tilt(0, -1)  # the stick's Y axis is down-positive
    controls = make_controls([pad])
    assert controls.read(DT, MAX_SPEED).move.y == pytest.approx(1)


def test_p06_r02_dpad_directions_fly_the_ship_and_diagonals_are_capped() -> None:
    pad = FakeGamepad().press(12, 15)  # up and right
    controls = make_controls([pad])
    move = controls.read(DT, MAX_SPEED).move
    assert math.hypot(move.x, move.y) == pytest.approx(1)
    assert move.x > 0
    assert move.y > 0


def test_p06_r02_the_fire_and_bomb_buttons_of_the_pad() -> None:
    pad = FakeGamepad().press(0)
    controls = make_controls([pad])
    assert controls.read(DT, MAX_SPEED).fire is True
    pad.release(0).press(2)
    state = controls.read(DT, MAX_SPEED)
    assert state.fire is False
    assert state.bomb is True
    assert controls.read(DT, MAX_SPEED).bomb is False  # held, not a new press
    pad.release(2)
    assert controls.read(DT, MAX_SPEED).bomb is False


def test_p12_r03_the_gamepad_in_use_being_unplugged_is_reported_once() -> None:
    pads: list = [FakeGamepad().tilt(1, 0)]
    controls = GameControls(GAME_CONTROLS_CONFIG, lambda: pads)
    controls.read(DT, MAX_SPEED)
    assert controls.take_disconnect() is False
    pads[0] = None
    controls.read(DT, MAX_SPEED)
    assert controls.take_disconnect() is True
    assert controls.take_disconnect() is False


def test_p12_r03_a_pad_never_used_is_not_a_disconnect() -> None:
    pads: list = [FakeGamepad()]
    controls = GameControls(GAME_CONTROLS_CONFIG, lambda: pads)
    controls.read(DT, MAX_SPEED)
    pads[0] = None
    controls.read(DT, MAX_SPEED)
    assert controls.take_disconnect() is False


def test_p06_r02_the_strongest_gamepad_steers_and_all_of_them_fire() -> None:
    weak = FakeGamepad().tilt(0.5, 0)
    strong = FakeGamepad().tilt(1, 0).press(7)
    controls = make_controls([weak, strong])
    state = controls.read(DT, MAX_SPEED)
    assert state.move.x == pytest.approx(1)
    assert state.fire is True


def test_p06_r02_the_keys_win_over_a_weaker_gamepad() -> None:
    pad = FakeGamepad().tilt(0.3, 0)
    controls = make_controls([pad])
    controls.key("ArrowRight", True)
    assert controls.read(DT, MAX_SPEED).move.x == 1
