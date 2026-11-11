# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/app/menu_view_builder.py`."""
# (the views of the screens of specs/ui/, and of the dev menu: specs/dev/dev-menu.md).

from types import SimpleNamespace

import pytest
from helpers.menu_game import make_game

from app.menu_state import MenuState
from app.menu_view_builder import MenuViewContext, build_menu_view
from app.settings_menu import Volumes
from core.systems.level_run_types import LevelCheckpoint, LevelResult
from core.systems.run_arsenal import WeaponLevels
from ui.menu_view import (
    DevAudioView,
    DevMenuView,
    DevViewerView,
    GameScreenView,
    LevelSelectView,
    LoadingView,
    PauseView,
    SettingsView,
    TitleView,
)


def ctx(game: SimpleNamespace | None = None, progress: float = 0.0) -> MenuViewContext:
    return MenuViewContext(game or make_game(), 1200, "1.0", "abc", progress, 10)


def state(screen: str, **overrides: object) -> MenuState:
    values: dict[str, object] = {
        "screen": screen,
        "selection": 0,
        "selected_id": None,
        "ship_id": "alpha",
        "chosen_level_id": None,
        "transitioning": False,
        "level_result": None,
        "choice": 0,
        "attempt": 1,
        "resume": None,
        "paused": False,
        "leaving": False,
        "volumes": Volumes(5, 6),
    }
    values.update(overrides)
    return MenuState(*values.values())  # type: ignore[arg-type]


def test_ui_load_03_the_loading_screen_shows_the_loading_text_and_progress() -> None:
    view = build_menu_view(state("loading"), ctx(progress=0.4))
    assert isinstance(view, LoadingView)
    assert (view.text, view.progress) == ("Loading", 0.4)


def test_ui_title_01_the_title_screen_shows_the_high_score_and_the_version() -> None:
    """Also UI-TITLE-03, UI-TITLE-04 and UI-LOOK-10 (the game's texts)."""
    view = build_menu_view(state("title", selection=1), ctx())
    assert isinstance(view, TitleView)
    assert (view.title, view.high_score, view.selected) == ("STRATOBLASTER", 1200, 1)
    assert (view.version, view.commit) == ("1.0", "abc")
    assert view.start == "Start"


def test_ui_level_04_the_level_select_marks_the_locked_levels() -> None:
    view = build_menu_view(state("level-select"), ctx())
    assert isinstance(view, LevelSelectView)
    assert [option.label for option in view.levels] == ["1-1", "1-2", "1-3"]
    assert [option.locked for option in view.levels] == [False, True, True]
    assert view.columns == 2
    assert view.locked_text == "Locked"


def test_ui_pause_07_the_pause_menu_is_the_game_screen_with_a_pause_view() -> None:
    view = build_menu_view(state("pause", selection=2, paused=True), ctx())
    assert isinstance(view, GameScreenView)
    assert view.level == "Level ?"  # no level chosen yet
    assert isinstance(view.paused, PauseView)
    assert view.paused.entries == ["Resume", "Settings", "Main menu"]
    assert view.paused.question is None
    assert view.selected == 2


def test_ui_pause_10_the_leave_question_is_shown_with_its_choices() -> None:
    view = build_menu_view(state("pause", leaving=True, choice=1, paused=True), ctx())
    question = view.paused.question
    assert question.text == "Leave the level?"
    assert question.choices == ["No", "Yes"]
    assert question.selected == 1
    assert view.selected == 1


def test_ui_hud_06_the_game_screen_names_the_chosen_level() -> None:
    view = build_menu_view(state("game", chosen_level_id="1-1"), ctx())
    assert isinstance(view, GameScreenView)
    assert view.level == "Level 1-1"
    assert view.fire == "FIRE"
    assert view.paused is None
    assert view.complete is None


def test_ui_hud_06_an_unknown_level_is_labelled_with_a_question_mark() -> None:
    view = build_menu_view(state("game", chosen_level_id="9-9"), ctx())
    assert view.level == "Level ?"


def test_ui_over_01_a_completed_level_shows_its_score_and_the_new_high_score() -> None:
    """Also UI-OVER-02 and UI-OVER-08 (no checkpoint, no choice)."""
    result = LevelResult("1-1", 10, 12, "complete", 1500.0, new_high_score=True, checkpoint=None)
    view = build_menu_view(state("game", level_result=result, chosen_level_id="1-1"), ctx())
    complete = view.complete
    assert complete.heading == "Level complete"
    assert complete.over is False
    assert complete.enemies == "10/12"
    assert complete.score == "Score 1500"
    assert complete.new_high_score == "New high score"
    assert complete.choices is None


def test_ui_over_06_a_game_over_with_a_checkpoint_offers_its_two_choices() -> None:
    """Also UI-OVER-05 and GAME-LIFE-11."""
    checkpoint = LevelCheckpoint(0.4, 1, WeaponLevels("guns", {"guns": 1.0}), 800.0)
    result = LevelResult("1-1", 3, 9, "over", 800.0, new_high_score=False, checkpoint=checkpoint)
    view = build_menu_view(state("game", level_result=result, choice=1), ctx())
    complete = view.complete
    assert complete.heading == "Game over"
    assert complete.over is True
    assert complete.new_high_score is None
    assert complete.choices.labels == ["Continue", "Level select"]
    assert complete.choices.selected == 1
    assert view.selected == 1


def test_ui_set_02_the_settings_screen_shows_one_slider_per_volume() -> None:
    view = build_menu_view(state("settings", selection=1), ctx())
    assert isinstance(view, SettingsView)
    assert [slider.label for slider in view.sliders] == ["Music", "Effects"]
    assert [slider.value for slider in view.sliders] == [5, 6]
    assert all(slider.max == 10 for slider in view.sliders)
    assert view.selected == 1
    assert view.over_level is False


def test_ui_set_07_settings_opened_in_a_level_are_marked_over_the_level() -> None:
    view = build_menu_view(state("settings", paused=True), ctx())
    assert view.over_level is True


@pytest.mark.parametrize("screen", ["title", "game"])
def test_ui_flow_01_each_screen_name_gets_its_own_view(screen: str) -> None:
    view = build_menu_view(state(screen), ctx())
    assert view.kind == ("title" if screen == "title" else "game")


# D-199: the dev menu and its viewers.


def dev_ctx() -> MenuViewContext:
    labels = {
        "ships": ["Alpha", "Beta"],
        "enemies": ["Gnat"],
        "bosses": [],
        "props": ["hut"],
        "levels": ["1-1", "1-2"],
    }
    return MenuViewContext(make_game(), 0, "1.0", "abc", 0, 10, labels)


def test_ui_title_11_the_full_screen_entry_reads_what_confirming_it_does() -> None:
    assert build_menu_view(state("title"), ctx()).fullscreen is None
    windowed = MenuViewContext(make_game(), 0, "1.0", "abc", 0, 10, None, None, False)
    assert build_menu_view(state("title"), windowed).fullscreen == "Full screen"
    full = MenuViewContext(make_game(), 0, "1.0", "abc", 0, 10, None, None, True)
    assert build_menu_view(state("title"), full).fullscreen == "Exit full screen"


def test_d199_the_title_shows_the_dev_entry_only_with_the_dev_labels() -> None:
    """DEV-MENU-01."""
    assert build_menu_view(state("title"), ctx()).dev is None
    assert build_menu_view(state("title"), dev_ctx()).dev == "Dev"


def test_d199_the_dev_menu_lists_the_viewers() -> None:
    """DEV-MENU-03."""
    view = build_menu_view(state("dev", selection=2), dev_ctx())
    assert isinstance(view, DevMenuView)
    assert view.entries == [
        "Player ships",
        "Enemies",
        "Bosses",
        "Props",
        "Levels",
        "Sounds",
        "Music",
    ]
    assert (view.selected, view.back) == (2, "Back")


def test_d199_a_model_viewer_shows_its_item_and_place_in_the_list() -> None:
    """DEV-MENU-05."""
    view = build_menu_view(
        state("dev-viewer", selection=1, dev_viewer="ships", dev_close_up=True), dev_ctx()
    )
    assert isinstance(view, DevViewerView)
    assert (view.heading, view.item, view.position) == ("Player ships", "Beta", "2 / 2")
    assert view.scrub is False


def test_d202_a_grouped_viewer_shows_the_items_group_and_place_in_it() -> None:
    context = dev_ctx()
    context.dev_labels["props"] = ["hut", "barn", "tower"]
    context.dev_groups = {"props": ["Farm", "Farm", "City"]}
    view = build_menu_view(state("dev-viewer", selection=1, dev_viewer="props"), context)
    assert isinstance(view, DevViewerView)
    assert (view.item, view.position) == ("barn", "Farm · 2 / 2")
    assert "group" in view.hint
    view = build_menu_view(state("dev-viewer", selection=2, dev_viewer="props"), context)
    assert view.position == "City · 1 / 1"


def test_d206_a_grouped_viewer_has_a_menu_of_its_groups_and_their_items() -> None:
    """DEV-MENU-07."""
    context = dev_ctx()
    context.dev_labels["props"] = ["hut", "barn", "tower"]
    context.dev_groups = {"props": ["Farm", "Farm", "City"]}
    view = build_menu_view(state("dev-viewer", selection=1, dev_viewer="props"), context)
    assert isinstance(view, DevViewerView)
    assert view.menu is not None
    assert [(c.label, c.index, c.selected, c.heading) for c in view.menu] == [
        ("Farm (2)", 0, True, True),
        ("hut", 0, False, False),
        ("barn", 1, True, False),
        ("City (1)", 2, False, True),
        ("tower", 2, False, False),
    ]


def test_d208_a_viewer_without_groups_has_a_menu_of_its_items() -> None:
    ships = build_menu_view(state("dev-viewer", selection=1, dev_viewer="ships"), dev_ctx())
    assert isinstance(ships, DevViewerView)
    assert ships.menu is not None
    assert [(c.label, c.index, c.selected, c.heading) for c in ships.menu] == [
        ("Alpha", 0, False, False),
        ("Beta", 1, True, False),
    ]
    assert "zoom" in ships.hint


def test_d199_the_levels_viewer_scrubs_with_the_wheel() -> None:
    view = build_menu_view(state("dev-viewer", dev_viewer="levels"), dev_ctx())
    assert isinstance(view, DevViewerView)
    assert view.scrub is True
    assert view.item == "1-1"
    assert "scrub" in view.hint.lower()


def test_d199_a_viewer_with_no_item_shows_an_empty_one() -> None:
    view = build_menu_view(state("dev-viewer", dev_viewer="bosses"), dev_ctx())
    assert (view.item, view.position) == ("", "1 / 0")


def test_dev_menu_19_the_sounds_viewer_is_a_grid_of_buttons_one_per_sound() -> None:
    context = dev_ctx()
    context.dev_labels["sounds"] = ["fire:guns", "hit"]
    view = build_menu_view(state("dev-viewer", selection=1, dev_viewer="sounds"), context)
    assert isinstance(view, DevAudioView)
    assert (view.kind, view.heading, view.selected, view.back) == ("dev-audio", "Sounds", 1, "Back")
    assert [(c.label, c.index, c.selected, c.heading) for c in view.entries] == [
        ("fire:guns", 0, False, False),
        ("hit", 1, True, False),
    ]
    assert "play" in view.hint


def test_dev_menu_20_the_music_viewer_lists_the_tracks_under_their_groups() -> None:
    context = dev_ctx()
    context.dev_labels["music"] = ["menu", "level-1-1", "boss-1"]
    context.dev_groups = {"music": ["Menu", "Levels", "Bosses"]}
    view = build_menu_view(state("dev-viewer", selection=2, dev_viewer="music"), context)
    assert isinstance(view, DevAudioView)
    assert [(c.label, c.index, c.selected, c.heading) for c in view.entries] == [
        ("Menu (1)", 0, False, True),
        ("menu", 0, False, False),
        ("Levels (1)", 1, False, True),
        ("level-1-1", 1, False, False),
        ("Bosses (1)", 2, True, True),
        ("boss-1", 2, True, False),
    ]
    assert "group" in view.hint


def test_dev_menu_21_the_enemies_and_bosses_viewers_have_three_view_buttons() -> None:
    for viewer in ("enemies", "bosses"):
        view = build_menu_view(
            state("dev-viewer", dev_viewer=viewer, dev_close_up=False, dev_mode=1), dev_ctx()
        )
        assert isinstance(view, DevViewerView)
        assert view.modes is not None
        assert [(c.label, c.index, c.selected) for c in view.modes] == [
            ("Model", 0, False),
            ("Wireframe", 1, True),
            ("Game view", 2, False),
        ]


def test_dev_menu_21_the_other_viewers_have_no_view_buttons() -> None:
    for viewer in ("ships", "props", "levels"):
        view = build_menu_view(state("dev-viewer", dev_viewer=viewer), dev_ctx())
        assert isinstance(view, DevViewerView)
        assert view.modes is None


def test_d333_a_model_viewer_with_a_single_model_has_no_menu() -> None:
    """D-333: the player ship alone: no menu, no place in a list, no "next" in the hint."""
    context = dev_ctx()
    context.dev_labels["ships"] = ["Balanced"]
    view = build_menu_view(state("dev-viewer", dev_viewer="ships"), context)
    assert isinstance(view, DevViewerView)
    assert view.menu is None
    assert (view.item, view.position) == ("Balanced", "")
    assert "next" not in view.hint
    assert "zoom" in view.hint
