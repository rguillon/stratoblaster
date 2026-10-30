"""Unit tests of `src/app/saved_supplies.py`."""
# (lives and bombs kept between levels).

import pytest

from app.saved_supplies import (
    load_saved_supplies,
    parse_supplies,
    save_supplies,
    saved_supplies_key,
)
from core.systems.level_run_types import Supplies
from host.key_value_storage import MemoryStorage


def test_p11_r05_the_supplies_are_kept_under_the_game_id() -> None:
    assert saved_supplies_key("game") == "game_supplies"


def test_p11_r05_stored_lives_and_bombs_are_read_back() -> None:
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
def test_p11_r05_anything_else_starts_with_the_game_s_own_supplies(raw: str | None) -> None:
    assert parse_supplies(raw) is None


def test_p11_r05_saving_then_loading_gives_the_same_supplies() -> None:
    storage = MemoryStorage()
    save_supplies(storage, "game", Supplies(3, 2))
    loaded = load_saved_supplies(storage, "game")
    assert loaded is not None
    assert (loaded.lives, loaded.bombs) == (3, 2)


def test_p11_r05_nothing_saved_loads_as_none() -> None:
    assert load_saved_supplies(MemoryStorage(), "game") is None
