# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/input/keyboard_menu_input.py`."""

from typing import Any

from config.menu_input import MENU_INPUT_CONFIG
from input.keyboard_menu_input import KeyboardMenuInput


class FakeKeyEvent:
    def __init__(self, code: str, repeat: bool = False) -> None:
        self.code = code
        self.repeat = repeat
        self.prevented = 0

    def preventDefault(self) -> None:
        self.prevented += 1


class FakeTarget:
    """Records the listeners added to it, like an `EventTarget`."""

    def __init__(self) -> None:
        self.listeners: dict[str, list] = {}

    def addEventListener(self, kind: str, listener: Any) -> None:
        self.listeners.setdefault(kind, []).append(listener)

    def removeEventListener(self, kind: str, listener: Any) -> None:
        self.listeners[kind].remove(listener)


def make_input() -> KeyboardMenuInput:
    return KeyboardMenuInput(MENU_INPUT_CONFIG.keyboard, MENU_INPUT_CONFIG)


def test_ui_input_05_a_bound_key_is_prevented_from_scrolling_the_page() -> None:
    menu = make_input()
    event = FakeKeyEvent("Enter")
    menu.key_down(event)
    assert event.prevented == 1
    assert menu.update(0) == ["confirm"]


def test_ui_input_01_unbound_keys_are_ignored() -> None:
    menu = make_input()
    event = FakeKeyEvent("KeyZ")
    menu.key_down(event)
    assert event.prevented == 0
    assert menu.update(1.0) == []


def test_ui_input_04_escape_is_cancel_and_p_is_pause() -> None:
    """Also UI-PAUSE-01 (the pause keys)."""
    menu = make_input()
    menu.key_down(FakeKeyEvent("Escape"))
    menu.key_down(FakeKeyEvent("KeyP"))
    assert menu.update(0) == ["cancel", "pause"]


def test_ui_input_06_a_held_direction_repeats_with_our_own_timing() -> None:
    menu = make_input()
    menu.key_down(FakeKeyEvent("ArrowDown"))
    assert menu.update(0) == ["down"]
    assert menu.update(0.2) == []
    assert menu.update(0.2) == ["down"]


def test_ui_input_05_browser_auto_repeat_events_are_ignored() -> None:
    menu = make_input()
    menu.key_down(FakeKeyEvent("ArrowDown"))
    menu.key_down(FakeKeyEvent("ArrowDown", repeat=True))
    assert menu.update(0) == ["down"]


def test_ui_input_06_key_up_stops_the_repeats() -> None:
    menu = make_input()
    menu.key_down(FakeKeyEvent("ArrowUp"))
    menu.update(0)
    menu.key_up(FakeKeyEvent("ArrowUp"))
    assert menu.update(5.0) == []


def test_ui_input_06_a_confirm_key_is_not_a_hold_so_key_up_is_harmless() -> None:
    menu = make_input()
    menu.key_down(FakeKeyEvent("Space"))
    menu.key_up(FakeKeyEvent("Space"))
    assert menu.update(5.0) == ["confirm"]


def test_ui_input_05_release_all_forgets_held_keys() -> None:
    menu = make_input()
    menu.key_down(FakeKeyEvent("KeyD"))
    menu.update(0)
    menu.release_all()
    assert menu.update(5.0) == []


def test_ui_input_05_listen_wires_keydown_keyup_and_blur_and_stop_removes_them() -> None:
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


def test_ui_input_06_one_of_two_keys_still_held_keeps_the_direction_repeating() -> None:
    menu = make_input()
    menu.key_down(FakeKeyEvent("ArrowUp"))
    menu.key_down(FakeKeyEvent("KeyW"))
    menu.update(0)
    menu.key_up(FakeKeyEvent("ArrowUp"))
    # KeyW is still down: the direction keeps repeating after the 0.35 s delay.
    assert menu.update(1.0) != []


def test_ui_input_05_listen_wires_keyup_to_stop_the_repeats() -> None:
    menu = make_input()
    target = FakeTarget()
    menu.listen(target)
    target.listeners["keydown"][0](FakeKeyEvent("ArrowDown"))
    assert menu.update(0) == ["down"]
    target.listeners["keyup"][0](FakeKeyEvent("ArrowDown"))
    assert menu.update(5.0) == []


def test_ui_input_05_a_direction_key_up_after_a_focus_loss_is_harmless() -> None:
    """Its key-down was forgotten (`release_all`): its key-up releases nothing more."""
    menu = make_input()
    menu.key_down(FakeKeyEvent("ArrowUp"))
    menu.update(0)
    menu.release_all()
    menu.key_up(FakeKeyEvent("ArrowUp"))
    assert menu.update(5.0) == []
    menu.key_down(FakeKeyEvent("ArrowUp"))
    assert menu.update(0) == ["up"]
