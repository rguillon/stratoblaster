"""Unit tests of `src/app/debug_options.py`."""
# (P06-R09, P07-R09, P08-R12, P15-R10).

from app.debug_options import parse_debug_options


def test_p06_r09_the_level_in_the_query_turns_debug_on() -> None:
    options = parse_debug_options("?level=1-3")
    assert options is not None
    assert options.level_id == "1-3"
    assert options.time == 0
    assert options.ship_id is None
    assert options.boss is None
    assert options.weather is True
    assert options.time_of_day is None
    assert options.tiles is False


def test_p06_r09_without_a_level_there_are_no_debug_options() -> None:
    assert parse_debug_options("") is None
    assert parse_debug_options("?ship=heavy") is None
    assert parse_debug_options("?level=") is None


def test_p06_r09_the_start_time_ship_and_boss_are_read() -> None:
    options = parse_debug_options("?level=2-1&t=120&ship=heavy&boss=final")
    assert options is not None
    assert options.time == 120
    assert options.ship_id == "heavy"
    assert options.boss == "final"


def test_p06_r09_a_negative_or_unreadable_time_starts_at_zero() -> None:
    assert parse_debug_options("?level=1-1&t=-5").time == 0
    assert parse_debug_options("?level=1-1&t=soon").time == 0


def test_p07_r09_only_the_mini_and_final_bosses_are_accepted() -> None:
    assert parse_debug_options("?level=1-1&boss=mini").boss == "mini"
    assert parse_debug_options("?level=1-1&boss=huge").boss is None


def test_p08_r12_weather_is_off_only_when_asked_with_zero() -> None:
    assert parse_debug_options("?level=1-1&weather=0").weather is False
    assert parse_debug_options("?level=1-1&weather=1").weather is True


def test_p08_r12_the_time_of_day_is_forced_only_for_a_known_one() -> None:
    options = parse_debug_options("?level=1-1&look=night")
    assert options.time_of_day == "night"
    assert parse_debug_options("?level=1-1&look=sometimes").time_of_day is None


def test_p15_r10_the_tile_grid_is_drawn_only_when_asked_with_one() -> None:
    assert parse_debug_options("?level=1-1&tiles=1").tiles is True
    assert parse_debug_options("?level=1-1&tiles=yes").tiles is False
