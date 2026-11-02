# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/app/saved_supplies.py`."""
# (lives and bombs kept between levels: GAME-LIFE-12, GAME-LEVEL-14).

import pytest
from helpers.memory_storage import MemoryStorage

from app import saved_supplies
from app.saved_supplies import (
    load_saved_supplies,
    parse_supplies,
    save_supplies,
    saved_supplies_key,
)
from core.systems.level_run_types import Supplies

# The JavaScript-only JSON helpers as the module defines them: the app conftest replaces them with
# their Python twins for every test, after this module is imported.
_READ_SUPPLIES = saved_supplies._read_supplies
_TO_JSON = saved_supplies._to_json


def test_game_life_12_the_supplies_are_kept_under_the_game_id() -> None:
    assert saved_supplies_key("game") == "game_supplies"


def test_game_life_12_stored_lives_and_bombs_are_read_back() -> None:
    supplies = parse_supplies('{"lives":4,"bombs":6}')
    assert supplies is not None
    assert (supplies.lives, supplies.bombs) == (4, 6)


@pytest.mark.parametrize(
    "raw",
    [
        None,
        "not json",
        "[]",
        "null",
        '{"lives":0,"bombs":1}',
        '{"lives":2.5,"bombs":1}',
        '{"lives":2,"bombs":-1}',
        '{"lives":"2","bombs":1}',
        '{"lives":2}',
    ],
)
def test_game_life_12_anything_else_starts_with_the_game_s_own_supplies(raw: str | None) -> None:
    assert parse_supplies(raw) is None


def test_game_life_12_saving_then_loading_gives_the_same_supplies() -> None:
    storage = MemoryStorage()
    save_supplies(storage, "game", Supplies(3, 2))
    loaded = load_saved_supplies(storage, "game")
    assert loaded is not None
    assert (loaded.lives, loaded.bombs) == (3, 2)


def test_game_life_12_nothing_saved_loads_as_none() -> None:
    assert load_saved_supplies(MemoryStorage(), "game") is None


def test_game_life_12_the_json_helpers_are_javascript_only() -> None:
    """`JSON.parse` and `JSON.stringify` run in the browser.

    CPython runs only the placeholders: nothing read, an empty text written.
    """
    assert _READ_SUPPLIES('{"lives":4,"bombs":6}') is None
    assert _TO_JSON(Supplies(4, 6)) == ""
