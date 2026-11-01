"""Unit tests of `src/game/config/menu_texts.py`."""

from game.config.menu_texts import MENU_TEXTS, SCORE_DIGITS, padded


def test_ui_hud_05_padded_scores_are_zero_filled_to_the_score_width() -> None:
    assert SCORE_DIGITS == 7
    assert padded(42) == "0000042"
    assert padded(0) == "0" * SCORE_DIGITS


def test_ui_hud_05_a_score_wider_than_the_display_is_not_truncated() -> None:
    assert padded(12345678) == "12345678"


def test_ui_look_10_every_menu_text_is_a_non_empty_string_or_a_text_builder() -> None:
    for key, text in MENU_TEXTS.items():
        if callable(text):
            assert text(*(["x"] * text.__code__.co_argcount)), key
        else:
            assert isinstance(text, str) and text, key


def test_ui_load_07_the_context_lost_message_asks_for_a_reload_and_has_a_reload_button() -> None:
    """The message over the page (main.py `show_context_lost`) and the button's text."""
    assert MENU_TEXTS["contextLost"] == "The graphics context was lost. Please reload the page."
    assert MENU_TEXTS["reload"] == "Reload"
