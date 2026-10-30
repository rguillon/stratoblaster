"""Unit tests of `src/app/saved_weapons.py`."""
# (the weapons kept between levels).

import pytest

from app.saved_weapons import (
    load_saved_weapons,
    parse_weapon_levels,
    save_weapons,
    saved_weapons_key,
)
from core.systems.run_arsenal import WeaponLevels
from host.key_value_storage import MemoryStorage


def test_p07_r08_the_weapons_are_kept_under_the_game_id() -> None:
    assert saved_weapons_key("game") == "game_weapons"


def test_p07_r08_stored_weapons_and_their_levels_are_read_back() -> None:
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
def test_p07_r08_anything_else_starts_with_the_first_level_of_each_weapon(raw: str | None) -> None:
    assert parse_weapon_levels(raw) is None


def test_p07_r08_saving_then_loading_keeps_the_weapon_levels() -> None:
    storage = MemoryStorage()
    save_weapons(storage, "game", WeaponLevels("spread", {"guns": 2.0, "spread": 4.0}))
    loaded = load_saved_weapons(storage, "game")
    assert loaded is not None
    assert loaded.weapon == "spread"
    assert loaded.levels == {"guns": 2, "spread": 4}


def test_p07_r08_nothing_saved_loads_as_none() -> None:
    assert load_saved_weapons(MemoryStorage(), "game") is None
