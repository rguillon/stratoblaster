"""Unit tests of `src/app/game_session.py`."""
# /app/game_session.py` (P06-R09, P13-R03, P08-R12): the debug choices on the look, the level and
# ship a menu state names. The session itself (the level loading in steps, the Babylon scene) runs
# in the browser.

from types import SimpleNamespace

from app.game_session import GameDebugOptions, atmosphere_of, highlighted_level, ship_of


def state(**overrides: object) -> SimpleNamespace:
    values: dict[str, object] = {
        "screen": "game",
        "selected_id": None,
        "chosen_ship_id": None,
        "highlighted_ship_id": "alpha",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_p13_r03_the_highlighted_level_is_prefetched_only_on_the_level_select_screen() -> None:
    assert highlighted_level(state(screen="level-select", selected_id="1-2")) == "1-2"
    assert highlighted_level(state(screen="title", selected_id="start")) is None


def test_p01_r14_the_ship_of_the_levels_is_the_chosen_one_or_else_the_highlighted() -> None:
    assert ship_of(state(chosen_ship_id="beta")) == "beta"
    assert ship_of(state(chosen_ship_id=None, highlighted_ship_id="gamma")) == "gamma"


def test_p08_r12_without_debug_options_the_look_is_the_levels_own() -> None:
    options = atmosphere_of(None)
    assert (options.time_of_day, options.weather, options.tile_grid) == (None, None, None)


def test_p08_r12_debug_options_force_the_time_of_day_and_weather_off_and_the_tiles() -> None:
    debug = GameDebugOptions("1-1", 0, None, None, False, "night", True)
    options = atmosphere_of(debug)
    assert options.time_of_day == "night"
    assert options.weather is False
    assert options.tile_grid is True


def test_p15_r10_the_tile_grid_is_left_to_the_level_when_not_asked() -> None:
    debug = GameDebugOptions("1-1", 0, None, None, None, None, False)
    options = atmosphere_of(debug)
    assert options.weather is None
    assert options.tile_grid is None
