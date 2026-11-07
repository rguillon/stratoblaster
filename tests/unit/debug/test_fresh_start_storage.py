# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/debug/fresh_start_storage.py` (D-269)."""

from app.saved_supplies import load_saved_supplies, save_supplies, saved_supplies_key
from app.saved_weapons import load_saved_weapons, save_weapons, saved_weapons_key
from core.systems.level_run_types import Supplies
from core.systems.run_arsenal import WeaponLevels
from debug.fresh_start_storage import FreshStartStorage


def test_d_269_no_weapons_or_supplies_are_kept_from_a_level_to_the_next() -> None:
    storage = FreshStartStorage("game")
    save_weapons(storage, "game", WeaponLevels("missile", {"missile": 5}))
    save_supplies(storage, "game", Supplies(5, 60))
    assert load_saved_weapons(storage, "game") is None
    assert load_saved_supplies(storage, "game") is None
    assert storage.get(saved_weapons_key("game")) is None
    assert storage.get(saved_supplies_key("game")) is None


def test_d_269_anything_else_is_kept_in_memory() -> None:
    storage = FreshStartStorage("game")
    assert storage.get("game_volumes") is None
    storage.set("game_volumes", "6,8")
    assert storage.get("game_volumes") == "6,8"
    assert FreshStartStorage("game").get("game_volumes") is None  # a new page starts empty
