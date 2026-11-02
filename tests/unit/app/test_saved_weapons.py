# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/app/saved_weapons.py`."""
# (the weapons kept between levels: GAME-WPN-15, GAME-LEVEL-14).

import pytest
from helpers.memory_storage import MemoryStorage

from app import saved_weapons
from app.saved_weapons import (
    load_saved_weapons,
    parse_weapon_levels,
    save_weapons,
    saved_weapons_key,
)
from core.systems.run_arsenal import WeaponLevels

# The JavaScript-only JSON helpers as the module defines them: the app conftest replaces them with
# their Python twins for every test, after this module is imported.
_READ_WEAPON_LEVELS = saved_weapons._read_weapon_levels
_TO_JSON = saved_weapons._to_json


def test_game_wpn_15_the_weapons_are_kept_under_the_game_id() -> None:
    assert saved_weapons_key("game") == "game_weapons"


def test_game_wpn_15_stored_weapons_and_their_levels_are_read_back() -> None:
    weapons = parse_weapon_levels('{"weapon":"guns","levels":{"guns":3,"spread":1}}')
    assert weapons is not None
    assert weapons.weapon == "guns"
    assert weapons.levels == {"guns": 3, "spread": 1}


@pytest.mark.parametrize(
    "raw",
    [
        None,
        "{",
        "3",
        '{"weapon":3,"levels":{}}',
        '{"weapon":"guns","levels":3}',
        '{"weapon":"guns","levels":{"guns":0}}',
        '{"weapon":"guns","levels":{"guns":1.5}}',
        '{"weapon":"guns"}',
    ],
)
def test_game_wpn_15_anything_else_starts_with_the_first_level_of_each_weapon(
    raw: str | None,
) -> None:
    assert parse_weapon_levels(raw) is None


def test_game_wpn_15_saving_then_loading_keeps_the_weapon_levels() -> None:
    storage = MemoryStorage()
    save_weapons(storage, "game", WeaponLevels("spread", {"guns": 2.0, "spread": 4.0}))
    loaded = load_saved_weapons(storage, "game")
    assert loaded is not None
    assert loaded.weapon == "spread"
    assert loaded.levels == {"guns": 2, "spread": 4}


def test_game_wpn_15_nothing_saved_loads_as_none() -> None:
    assert load_saved_weapons(MemoryStorage(), "game") is None


def test_game_wpn_15_the_json_helpers_are_javascript_only() -> None:
    """`JSON.parse` and `JSON.stringify` run in the browser.

    CPython runs only the placeholders: nothing read, an empty text written.
    """
    assert _READ_WEAPON_LEVELS('{"weapon":"guns","levels":{"guns":3}}') is None
    assert _TO_JSON(WeaponLevels("guns", {"guns": 3})) == ""
