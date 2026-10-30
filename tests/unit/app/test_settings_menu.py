"""Unit tests of `src/app/settings_menu.py`."""
# (P12-R04).

import math

from app.settings_menu import (
    SETTINGS_SLIDERS,
    SettingsMenu,
    Volumes,
    volume_of,
    with_volume,
)


def make(music: int = 5, sfx: int = 7, max_step: int = 10) -> SettingsMenu:
    return SettingsMenu(Volumes(music, sfx), max_step)


def test_p12_r04_there_is_a_music_and_a_sound_effects_slider() -> None:
    assert SETTINGS_SLIDERS == ["music", "sfx"]


def test_p12_r04_volume_of_and_with_volume_read_and_copy_the_sliders() -> None:
    volumes = Volumes(3, 4)
    assert volume_of(volumes, "music") == 3
    assert volume_of(volumes, "sfx") == 4
    louder = with_volume(volumes, "sfx", 9)
    assert (louder.music, louder.sfx) == (3, 9)
    assert (volumes.music, volumes.sfx) == (3, 4)
    quieter = with_volume(volumes, "music", 1)
    assert (quieter.music, quieter.sfx) == (1, 4)


def test_p12_r04_the_saved_volumes_are_clamped_to_the_slider() -> None:
    menu = make(music=20, sfx=-3, max_step=10)
    assert (menu.volumes.music, menu.volumes.sfx) == (10, 0)


def test_p12_r04_the_screen_opens_on_the_music_slider() -> None:
    menu = make()
    menu.select(1)
    menu.open()
    assert menu.selection == 0
    assert menu.selected_id == "music"


def test_p12_r04_up_and_down_pick_a_slider_and_stop_at_the_ends() -> None:
    menu = make()
    assert menu.move("up") == "none"
    assert menu.move("down") == "moved"
    assert menu.selected_id == "sfx"
    assert menu.move("down") == "none"
    assert menu.move("up") == "moved"
    assert menu.selected_id == "music"


def test_p12_r04_left_and_right_change_the_selected_slider_by_one_step() -> None:
    menu = make(music=5, sfx=7)
    assert menu.move("right") == "adjusted"
    assert menu.volumes.music == 6
    assert menu.move("left") == "adjusted"
    assert menu.move("left") == "adjusted"
    assert menu.volumes.music == 4
    menu.move("down")
    assert menu.move("right") == "adjusted"
    assert menu.volumes.sfx == 8


def test_p12_r04_a_slider_stops_at_its_ends() -> None:
    menu = make(music=10, sfx=0, max_step=10)
    assert menu.move("right") == "none"
    menu.move("down")
    assert menu.move("left") == "none"
    assert menu.volumes.sfx == 0


def test_p12_r04_a_tap_or_drag_sets_a_slider_to_the_nearest_step() -> None:
    menu = make(music=5, sfx=7)
    assert menu.set(1, 3.4) == "adjusted"
    assert menu.volumes.sfx == 3
    assert menu.selection == 1
    assert menu.set(0, 9.6) == "adjusted"
    assert menu.volumes.music == 10


def test_p12_r04_setting_a_slider_clamps_to_the_range() -> None:
    menu = make(music=5, sfx=7, max_step=10)
    menu.set(0, 99)
    assert menu.volumes.music == 10
    menu.set(0, -4)
    assert menu.volumes.music == 0


def test_p12_r04_setting_the_same_value_reports_none_or_a_move() -> None:
    menu = make(music=5, sfx=7)
    assert menu.set(0, 5) == "none"
    assert menu.set(1, 7) == "moved"
    assert menu.selection == 1
    assert menu.set(1, 7) == "none"
    assert menu.set(1, 6) == "adjusted"


def test_p12_r04_a_slider_that_does_not_exist_or_a_nan_value_is_refused() -> None:
    menu = make()
    assert menu.set(2, 3) == "none"
    assert menu.set(-1, 3) == "none"
    assert menu.set(0, math.nan) == "none"
    assert menu.set(0, float("inf")) == "none"
    assert menu.set(0.5, 3) == "none"


def test_p12_r04_a_direct_pick_moves_the_selection_or_is_refused() -> None:
    menu = make()
    assert menu.select(1) == "moved"
    assert menu.select(1) == "none"
    assert menu.select(2) == "none"
    assert menu.select(0.5) == "none"


def test_p12_r04_the_selected_id_falls_back_to_music_for_a_bad_selection() -> None:
    menu = make()
    menu._selection = 5  # noqa: SLF001 (the guard of an out-of-range selection)
    assert menu.selected_id == "music"
