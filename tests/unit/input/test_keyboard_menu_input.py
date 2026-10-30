"""Unit tests of `src/input/keyboard_menu_input.py`."""

import pytest

from config.menu_input import MENU_INPUT_CONFIG
from input.keyboard_menu_input import KeyboardMenuInput


class FakeKeyEvent:
    def __init__(self, code: str, repeat: bool = False) -> None:
        self.code = code
        self.repeat = repeat
        self.prevented = 0

    def preventDefault(self) -> None:  # noqa: N802 (DOM name)
        self.prevented += 1


class FakeTarget:
    """Records the listeners added to it, like an `EventTarget`."""

    def __init__(self) -> None:
        self.listeners: dict[str, list] = {}

    def addEventListener(self, kind: str, listener) -> None:  # noqa: N802
        self.listeners.setdefault(kind, []).append(listener)

    def removeEventListener(self, kind: str, listener) -> None:  # noqa: N802
        self.listeners[kind].remove(listener)


def make_input() -> KeyboardMenuInput:
    return KeyboardMenuInput(MENU_INPUT_CONFIG.keyboard, MENU_INPUT_CONFIG)


def test_p01_r09_wasd_positions_map_to_the_same_actions_as_arrows() -> None:
    keys = MENU_INPUT_CONFIG.keyboard
    assert keys["KeyW"] == keys["ArrowUp"] == "up"
    assert keys["KeyS"] == keys["ArrowDown"] == "down"
    assert keys["KeyA"] == keys["ArrowLeft"] == "left"
    assert keys["KeyD"] == keys["ArrowRight"] == "right"


def test_p01_r09_a_bound_key_is_prevented_from_scrolling_the_page() -> None:
    menu = make_input()
    event = FakeKeyEvent("Enter")
    menu.key_down(event)
    assert event.prevented == 1
    assert menu.update(0) == ["confirm"]


def test_p01_r09_unbound_keys_are_ignored() -> None:
    menu = make_input()
    event = FakeKeyEvent("KeyZ")
    menu.key_down(event)
    assert event.prevented == 0
    assert menu.update(1.0) == []


def test_p01_r09_escape_is_cancel_and_p_is_pause() -> None:
    menu = make_input()
    menu.key_down(FakeKeyEvent("Escape"))
    menu.key_down(FakeKeyEvent("KeyP"))
    assert menu.update(0) == ["cancel", "pause"]


def test_p01_r09_a_held_direction_repeats_with_our_own_timing() -> None:
    menu = make_input()
    menu.key_down(FakeKeyEvent("ArrowDown"))
    assert menu.update(0) == ["down"]
    assert menu.update(0.2) == []
    assert menu.update(0.2) == ["down"]


def test_p01_r09_browser_auto_repeat_events_are_ignored() -> None:
    menu = make_input()
    menu.key_down(FakeKeyEvent("ArrowDown"))
    menu.key_down(FakeKeyEvent("ArrowDown", repeat=True))
    assert menu.update(0) == ["down"]


def test_p01_r09_key_up_stops_the_repeats() -> None:
    menu = make_input()
    menu.key_down(FakeKeyEvent("ArrowUp"))
    menu.update(0)
    menu.key_up(FakeKeyEvent("ArrowUp"))
    assert menu.update(5.0) == []


def test_p01_r09_a_confirm_key_is_not_a_hold_so_key_up_is_harmless() -> None:
    menu = make_input()
    menu.key_down(FakeKeyEvent("Space"))
    menu.key_up(FakeKeyEvent("Space"))
    assert menu.update(5.0) == ["confirm"]


def test_p01_r09_release_all_forgets_held_keys() -> None:
    menu = make_input()
    menu.key_down(FakeKeyEvent("KeyD"))
    menu.update(0)
    menu.release_all()
    assert menu.update(5.0) == []


def test_p01_r09_listen_wires_keydown_keyup_and_blur_and_stop_removes_them() -> None:
    menu = make_input()
    target = FakeTarget()
    stop = menu.listen(target)
    down = target.listeners["keydown"][0]
    down(FakeKeyEvent("ArrowLeft"))
    assert menu.update(0) == ["left"]
    target.listeners["blur"][0]()
    assert menu.update(5.0) == []
    stop()
    assert target.listeners == {"keydown": [], "keyup": [], "blur": []}


@pytest.mark.xfail(
    strict=True,
    reason="BUG: KeyboardMenuInput.key_up releases the action, not the key, so releasing one of "
    "two keys bound to the same direction (ArrowUp and KeyW) stops the repeat while the other is "
    "still held (src/input/keyboard_menu_input.py)",
)
def test_p01_r09_releasing_one_of_two_keys_for_a_direction_keeps_repeating_for_the_other() -> None:
    menu = make_input()
    menu.key_down(FakeKeyEvent("ArrowUp"))
    menu.key_down(FakeKeyEvent("KeyW"))
    menu.update(0)
    menu.key_up(FakeKeyEvent("ArrowUp"))
    # KeyW is still down: the direction keeps repeating after the 0.35 s delay.
    assert menu.update(1.0) != []
