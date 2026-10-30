"""Unit tests of `src/ui/screens/screen_handlers.py`."""

from ui.screens.screen_handlers import ScreenHandlers


def test_p01_r11_a_menu_screen_needs_only_tap_and_back() -> None:
    handlers = ScreenHandlers(lambda index: None, lambda: None)
    assert handlers.on_fire is None
    assert handlers.on_drag is None
    assert handlers.on_pause is None
    assert handlers.on_set is None


def test_p06_r02_the_game_screen_handlers_are_kept() -> None:
    def fire(held: bool) -> None:
        return None

    handlers = ScreenHandlers(lambda index: None, lambda: None, fire)
    assert handlers.on_fire is fire
