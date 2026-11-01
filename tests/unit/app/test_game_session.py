# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/app/game_session.py`."""
# /app/game_session.py` (DEV-OPT-04 to DEV-OPT-06, PERF-12): the debug choices on the look, the
# level and ship a menu state names. The session itself (the level loading in steps, the Babylon
# scene) runs in the browser.

from types import SimpleNamespace

from app.game_session import (
    GameDebugOptions,
    GameSession,
    atmosphere_of,
    highlighted_level,
    ship_of,
)
from app.saved_supplies import load_saved_supplies, save_supplies, saved_supplies_key
from app.saved_weapons import load_saved_weapons, save_weapons
from core.systems.level_run_types import Supplies
from core.systems.run_arsenal import WeaponLevels
from host.key_value_storage import MemoryStorage


def state(**overrides: object) -> SimpleNamespace:
    values: dict[str, object] = {
        "screen": "game",
        "selected_id": None,
        "chosen_ship_id": None,
        "highlighted_ship_id": "alpha",
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def test_perf_12_the_highlighted_level_is_prefetched_only_on_the_level_select_screen() -> None:
    assert highlighted_level(state(screen="level-select", selected_id="1-2")) == "1-2"
    assert highlighted_level(state(screen="title", selected_id="start")) is None


def test_perf_13_the_ship_of_the_levels_is_the_chosen_one_or_else_the_highlighted() -> None:
    """The level built ahead is flown with the highlighted ship."""
    assert ship_of(state(chosen_ship_id="beta")) == "beta"
    assert ship_of(state(chosen_ship_id=None, highlighted_ship_id="gamma")) == "gamma"


def test_dev_opt_04_without_debug_options_the_look_is_the_levels_own() -> None:
    """Also DEV-OPT-05 and DEV-OPT-06."""
    options = atmosphere_of(None)
    assert (options.time_of_day, options.weather, options.tile_grid) == (None, None, None)


def test_dev_opt_05_debug_options_force_the_time_of_day_and_weather_off_and_the_tiles() -> None:
    """Also DEV-OPT-04 and DEV-OPT-06."""
    debug = GameDebugOptions("1-1", 0, None, None, weather=False, time_of_day="night", tiles=True)
    options = atmosphere_of(debug)
    assert options.time_of_day == "night"
    assert options.weather is False
    assert options.tile_grid is True


def test_dev_opt_06_the_tile_grid_is_left_to_the_level_when_not_asked() -> None:
    debug = GameDebugOptions("1-1", 0, None, None, None, None, tiles=False)
    options = atmosphere_of(debug)
    assert options.weather is None
    assert options.tile_grid is None


def _session(storage: MemoryStorage | None, completed: list[object]) -> GameSession:
    """Return a game session with only what its carry-over reads: the storage and the game's id."""
    session = GameSession.__new__(GameSession)
    session.options = SimpleNamespace(storage=storage)
    session.game = SimpleNamespace(id="game")
    session._on_complete = completed.append
    return session


def _played(phase: str, weapons: WeaponLevels, supplies: Supplies) -> SimpleNamespace:
    """Return a level as its run ends: its phase, its weapons (arsenal), lives and bombs."""
    run = SimpleNamespace(
        phase=phase,
        arsenal=SimpleNamespace(snapshot=lambda: weapons),
        supplies=supplies,
    )
    return SimpleNamespace(run=run)


def test_game_level_14_a_completed_level_keeps_its_weapons_lives_and_bombs() -> None:
    storage = MemoryStorage()
    completed: list[object] = []
    weapons = WeaponLevels("laser", {"guns": 2.0, "laser": 3.0})
    play = _played("complete", weapons, Supplies(5, 7))
    _session(storage, completed)._completed(play)
    kept_weapons = load_saved_weapons(storage, "game")
    kept_supplies = load_saved_supplies(storage, "game")
    assert kept_weapons is not None
    assert kept_weapons.weapon == "laser"
    assert kept_weapons.levels == {"guns": 2.0, "laser": 3.0}
    assert kept_supplies is not None
    assert (kept_supplies.lives, kept_supplies.bombs) == (5, 7)
    assert completed == [play]


def test_game_level_14_a_game_over_keeps_nothing_new() -> None:
    """What was kept before stays: the level lost keeps neither its weapons nor its supplies."""
    storage = MemoryStorage()
    save_weapons(storage, "game", WeaponLevels("guns", {"guns": 1.0}))
    save_supplies(storage, "game", Supplies(3, 3))
    completed: list[object] = []
    play = _played("over", WeaponLevels("laser", {"guns": 4.0, "laser": 4.0}), Supplies(9, 9))
    _session(storage, completed)._completed(play)
    kept_weapons = load_saved_weapons(storage, "game")
    kept_supplies = load_saved_supplies(storage, "game")
    assert kept_weapons is not None
    assert kept_weapons.weapon == "guns"
    assert kept_weapons.levels == {"guns": 1.0}
    assert kept_supplies is not None
    assert (kept_supplies.lives, kept_supplies.bombs) == (3, 3)
    assert completed == [play]


def test_game_life_12_a_continue_keeps_the_weapons_but_not_the_supplies() -> None:
    """A Continue starts again with the starting lives and bombs (GAME-LIFE-11): none are read."""
    storage = MemoryStorage()
    save_weapons(storage, "game", WeaponLevels("guns", {"guns": 2.0}))
    save_supplies(storage, "game", Supplies(5, 7))
    session = _session(storage, [])
    weapons, supplies = session._kept(SimpleNamespace(resume=True))
    assert weapons is not None
    assert weapons.levels == {"guns": 2.0}
    assert supplies is None
    weapons, supplies = session._kept(SimpleNamespace(resume=None))
    assert supplies is not None
    assert (supplies.lives, supplies.bombs) == (5, 7)


def test_game_life_12_an_unreadable_saved_supply_is_kept_as_none() -> None:
    storage = MemoryStorage()
    storage.set(saved_supplies_key("game"), "not json")
    _weapons, supplies = _session(storage, [])._kept(SimpleNamespace(resume=None))
    assert supplies is None


def test_game_level_14_without_storage_nothing_is_kept_or_saved() -> None:
    session = _session(None, [])
    assert session._kept(SimpleNamespace(resume=None)) == (None, None)
    session._completed(_played("complete", WeaponLevels("guns", {}), Supplies(5, 7)))
