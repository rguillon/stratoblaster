# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/app/debug_options.py`."""
# (DEV-OPT-01 to DEV-OPT-06, DEV-MENU-01).

from app import debug_options
from app.debug_options import ai_mode, dev_mode, parse_debug_options

# The JavaScript-only query helpers as the module defines them: the app conftest replaces them with
# their Python twins for every test, after this module is imported.
_QUERY_TEXT = debug_options._query_text
_HAS_KEY = debug_options._has_key
_TIME_TEXT = debug_options._time_text


def test_dev_opt_01_the_level_in_the_query_turns_debug_on() -> None:
    options = parse_debug_options("?level=1-3")
    assert options is not None
    assert options.level_id == "1-3"
    assert options.time == 0
    assert options.boss is None
    assert options.weather is True
    assert options.time_of_day is None
    assert options.tiles is False


def test_dev_opt_01_without_a_level_there_are_no_debug_options() -> None:
    assert parse_debug_options("") is None
    assert parse_debug_options("?t=120") is None
    assert parse_debug_options("?level=") is None


def test_dev_opt_02_the_start_time_and_boss_are_read() -> None:
    """Also DEV-OPT-03 (the boss)."""
    options = parse_debug_options("?level=2-1&t=120&boss=final")
    assert options is not None
    assert options.time == 120
    assert options.boss == "final"


def test_dev_opt_02_a_negative_or_unreadable_time_starts_at_zero() -> None:
    assert parse_debug_options("?level=1-1&t=-5").time == 0
    assert parse_debug_options("?level=1-1&t=soon").time == 0


def test_dev_opt_03_only_the_mini_and_final_bosses_are_accepted() -> None:
    assert parse_debug_options("?level=1-1&boss=mini").boss == "mini"
    assert parse_debug_options("?level=1-1&boss=huge").boss is None


def test_dev_opt_04_weather_is_off_only_when_asked_with_zero() -> None:
    assert parse_debug_options("?level=1-1&weather=0").weather is False
    assert parse_debug_options("?level=1-1&weather=1").weather is True


def test_dev_opt_05_the_time_of_day_is_forced_only_for_a_known_one() -> None:
    options = parse_debug_options("?level=1-1&look=night")
    assert options.time_of_day == "night"
    assert parse_debug_options("?level=1-1&look=sometimes").time_of_day is None


def test_dev_opt_06_the_tile_grid_is_drawn_only_when_asked_with_one() -> None:
    assert parse_debug_options("?level=1-1&tiles=1").tiles is True
    assert parse_debug_options("?level=1-1&tiles=yes").tiles is False


def test_d199_dev_in_the_query_asks_for_the_dev_menu() -> None:
    """DEV-MENU-01."""
    assert dev_mode("?dev")
    assert dev_mode("?level=1-1&dev=1")
    assert not dev_mode("")
    assert not dev_mode("?level=1-1")


def test_d_266_ai_in_the_query_asks_for_the_ai_player() -> None:
    assert ai_mode("?ai")
    assert ai_mode("?ai&level=2-3")
    assert not ai_mode("")
    assert not ai_mode("?level=2-3")


def test_dev_opt_01_the_query_helpers_are_javascript_only() -> None:
    """`URLSearchParams` reads the query in the browser; CPython runs only the placeholders.

    No value, no key and a start time of 0, whatever the query (DEV-OPT-02 for the time, DEV-MENU-01
    for the key).
    """
    assert _QUERY_TEXT("?level=1-3", "level") is None
    assert _HAS_KEY("?dev", "dev") is False
    assert _TIME_TEXT("?t=120") == 0
