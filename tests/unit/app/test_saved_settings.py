"""Unit tests of `src/app/saved_settings.py`."""
# (P12-R04, D-010).

import pytest

from app.saved_settings import (
    load_volumes,
    parse_volume,
    save_volumes,
    saved_setting_keys,
)
from app.settings_menu import Volumes
from host.key_value_storage import MemoryStorage


def test_p12_r04_the_volume_keys_are_prefixed_with_the_game_id() -> None:
    keys = saved_setting_keys("game")
    assert (keys.music, keys.sfx) == ("game_music_volume", "game_sfx_volume")


@pytest.mark.parametrize(("raw", "expected"), [("0", 0), ("10", 10), (" 7 ", 7)])
def test_p12_r04_a_whole_step_from_zero_to_the_maximum_is_read(raw: str, expected: int) -> None:
    assert parse_volume(raw, 10, 5) == expected


@pytest.mark.parametrize("raw", [None, "", "11", "-1", "3.5", "loud", "100"])
def test_p12_r04_anything_else_reads_as_the_fallback(raw: str | None) -> None:
    assert parse_volume(raw, 10, 5) == 5


def test_p12_r04_saved_volumes_are_loaded_or_fall_back_per_volume() -> None:
    storage = MemoryStorage()
    storage.set("game_music_volume", "3")
    storage.set("game_sfx_volume", "nope")
    loaded = load_volumes(storage, "game", 10, Volumes(6, 8))
    assert (loaded.music, loaded.sfx) == (3, 8)


def test_p12_r04_both_volumes_are_saved_on_a_change() -> None:
    storage = MemoryStorage()
    save_volumes(storage, "game", Volumes(2, 9))
    assert storage.get("game_music_volume") == "2"
    assert storage.get("game_sfx_volume") == "9"
    loaded = load_volumes(storage, "game", 10, Volumes(0, 0))
    assert (loaded.music, loaded.sfx) == (2, 9)
