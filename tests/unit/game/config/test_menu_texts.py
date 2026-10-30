"""Unit tests of `src/game/config/menu_texts.py`."""

from game.config.menu_texts import MENU_TEXTS, SCORE_DIGITS, padded


def test_p11_r02_padded_scores_are_zero_filled_to_the_score_width() -> None:
    assert SCORE_DIGITS == 7
    assert padded(42) == "0000042"
    assert padded(0) == "0" * SCORE_DIGITS


def test_p11_r02_a_score_wider_than_the_display_is_not_truncated() -> None:
    assert padded(12345678) == "12345678"


def test_p11_r02_every_menu_text_is_a_non_empty_string_or_a_text_builder() -> None:
    for key, text in MENU_TEXTS.items():
        if callable(text):
            assert text(*(["x"] * text.__code__.co_argcount)), key
        else:
            assert isinstance(text, str) and text, key
