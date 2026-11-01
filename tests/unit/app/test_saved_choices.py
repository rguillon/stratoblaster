"""Unit tests of `src/app/saved_choices.py`."""
# (UI-TITLE-03, UI-SHIP-07, GAME-SCORE-05).

from app.saved_choices import (
    load_saved_choices,
    parse_high_score,
    save_high_score,
    save_last_ship,
    saved_choice_keys,
)
from host.key_value_storage import MemoryStorage


def test_ui_title_03_the_keys_are_prefixed_with_the_game_id() -> None:
    keys = saved_choice_keys("stratoblaster")
    assert keys.high_score == "stratoblaster_high_score"
    assert keys.last_ship == "stratoblaster_last_ship"


def test_ui_title_03_a_plain_stored_score_is_read_as_a_number() -> None:
    assert parse_high_score("1200") == 1200
    assert parse_high_score(" 42 ") == 42


def test_ui_title_03_anything_but_a_plain_score_reads_as_zero() -> None:
    assert parse_high_score(None) == 0
    assert parse_high_score("") == 0
    assert parse_high_score("12.5") == 0
    assert parse_high_score("-3") == 0
    assert parse_high_score("1234567890123456") == 0
    assert parse_high_score("abc") == 0


def test_game_score_05_a_saved_high_score_is_floored_and_never_negative() -> None:
    storage = MemoryStorage()
    save_high_score(storage, "game", 1234.9)
    assert storage.get("game_high_score") == "1234"
    save_high_score(storage, "game", -5)
    assert storage.get("game_high_score") == "0"


def test_ui_ship_07_the_last_ship_is_saved_under_its_key() -> None:
    storage = MemoryStorage()
    save_last_ship(storage, "game", "beta")
    assert storage.get("game_last_ship") == "beta"


def test_ui_title_03_the_saved_choices_are_loaded_at_start_up() -> None:
    """Also UI-SHIP-07 (the last ship)."""
    storage = MemoryStorage()
    storage.set("game_high_score", "900")
    storage.set("game_last_ship", "gamma")
    saved = load_saved_choices(storage, "game")
    assert saved.high_score == 900
    assert saved.last_ship_id == "gamma"


def test_ui_title_03_nothing_saved_loads_as_no_score_and_no_ship() -> None:
    saved = load_saved_choices(MemoryStorage(), "game")
    assert saved.high_score == 0
    assert saved.last_ship_id is None
