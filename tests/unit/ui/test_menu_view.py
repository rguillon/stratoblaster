"""Unit tests of `src/ui/menu_view.py`."""

from ui.menu_view import (
    BackView,
    GameScreenView,
    LevelCompleteView,
    LevelOption,
    LevelSelectView,
    LoadingView,
    SettingsView,
    ShipSelectView,
    SliderView,
    TitleView,
)


def test_p01_r04_each_screen_view_names_its_screen_kind() -> None:
    assert LoadingView.kind == "loading"
    assert TitleView.kind == "title"
    assert ShipSelectView.kind == "ship-select"
    assert LevelSelectView.kind == "level-select"
    assert GameScreenView.kind == "game"
    assert SettingsView.kind == "settings"


def test_p01_r11_the_screens_with_a_back_button_share_its_fields() -> None:
    settings = SettingsView("Settings", "hint", "Back", 1, [SliderView("Music", 3, 10)], False)
    assert isinstance(settings, BackView)
    assert (settings.heading, settings.back, settings.selected) == ("Settings", "Back", 1)
    assert settings.sliders[0].max == 10
    assert settings.over_level is False


def test_p01_r07_the_level_select_view_keeps_its_grid_and_locks() -> None:
    levels = [LevelOption("1", False), LevelOption("2", True)]
    view = LevelSelectView("Levels", "hint", "Back", 0, 2, levels, "Locked")
    assert view.columns == 2
    assert [level.locked for level in view.levels] == [False, True]
    assert view.locked_text == "Locked"


def test_p01_r04_the_title_view_keeps_every_text_it_was_given() -> None:
    view = TitleView("STRATO", "HIGH", 1200, "Start", "Settings", 0, "hint", "1.0", "abc123")
    assert view.high_score == 1200
    assert view.commit == "abc123"


def test_p06_r03_a_level_complete_panel_has_no_choices_unless_given() -> None:
    panel = LevelCompleteView("Level complete", False, "Level 1", "3/3", "900", "Tap")
    assert panel.choices is None
    assert panel.new_high_score is None
    assert panel.over is False


def test_p01_r15_a_loading_view_keeps_its_text_and_progress() -> None:
    view = LoadingView("Loading", 0.4)
    assert (view.text, view.progress) == ("Loading", 0.4)
