# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/ui/screens/screen_handlers.py`."""

from ui.screens.screen_handlers import ScreenHandlers


def test_ui_input_09_a_menu_screen_needs_only_tap_and_back() -> None:
    handlers = ScreenHandlers(lambda _index: None, lambda: None)
    assert handlers.on_fire is None
    assert handlers.on_drag is None
    assert handlers.on_pause is None
    assert handlers.on_set is None


def test_game_ctrl_05_the_game_screen_handlers_are_kept() -> None:
    def fire(_held: bool) -> None:
        return None

    handlers = ScreenHandlers(lambda _index: None, lambda: None, fire)
    assert handlers.on_fire is fire
