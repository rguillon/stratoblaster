"""Unit tests of `src/app/menu_view_builder.py`."""
# (P01-R04, R06, R07, P06-R02, R03, P12-R02, R04).

from types import SimpleNamespace

import pytest
from helpers.menu_game import make_game

from app.menu_state import MenuState
from app.menu_view_builder import MenuViewContext, build_menu_view
from app.settings_menu import Volumes
from core.systems.level_run_types import LevelCheckpoint, LevelResult
from core.systems.run_arsenal import WeaponLevels
from ui.menu_view import (
    DevMenuView,
    DevViewerView,
    GameScreenView,
    LevelSelectView,
    LoadingView,
    PauseView,
    SettingsView,
    ShipSelectView,
    TitleView,
)


def ctx(game: SimpleNamespace | None = None, progress: float = 0.0) -> MenuViewContext:
    return MenuViewContext(game or make_game(), 1200, "1.0", "abc", 80, progress, 10)


def state(screen: str, **overrides: object) -> MenuState:
    values: dict[str, object] = {
        "screen": screen,
        "selection": 0,
        "selected_id": None,
        "highlighted_ship_id": "alpha",
        "chosen_ship_id": None,
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


def test_p01_r02_the_loading_screen_shows_the_loading_text_and_progress() -> None:
    view = build_menu_view(state("loading"), ctx(progress=0.4))
    assert isinstance(view, LoadingView)
    assert (view.text, view.progress) == ("Loading", 0.4)


def test_p01_r04_the_title_screen_shows_the_high_score_and_the_version() -> None:
    view = build_menu_view(state("title", selection=1), ctx())
    assert isinstance(view, TitleView)
    assert (view.title, view.high_score, view.selected) == ("STRATOBLASTER", 1200, 1)
    assert (view.version, view.commit) == ("1.0", "abc")
    assert view.start == "Start"


def test_p01_r06_the_ship_select_has_a_card_per_ship() -> None:
    view = build_menu_view(state("ship-select", selection=1), ctx())
    assert isinstance(view, ShipSelectView)
    assert [card.title for card in view.ships] == ["Alpha", "Beta"]
    assert view.ships[1].lines[0] == "Speed ×2 (200 px/s)"
    assert view.cards_width_percent == 80


def test_p01_r07_the_level_select_marks_the_locked_levels() -> None:
    view = build_menu_view(state("level-select"), ctx())
    assert isinstance(view, LevelSelectView)
    assert [option.label for option in view.levels] == ["1-1", "1-2", "1-3"]
    assert [option.locked for option in view.levels] == [False, True, True]
    assert view.columns == 2
    assert view.locked_text == "Locked"


def test_p12_r02_the_pause_menu_is_the_game_screen_with_a_pause_view() -> None:
    view = build_menu_view(state("pause", selection=2, paused=True), ctx())
    assert isinstance(view, GameScreenView)
    assert view.level == "Level ?"  # no level chosen yet
    assert isinstance(view.paused, PauseView)
    assert view.paused.entries == ["Resume", "Settings", "Main menu"]
    assert view.paused.question is None
    assert view.selected == 2


def test_p12_r02_the_leave_question_is_shown_with_its_choices() -> None:
    view = build_menu_view(state("pause", leaving=True, choice=1, paused=True), ctx())
    question = view.paused.question
    assert question.text == "Leave the level?"
    assert question.choices == ["No", "Yes"]
    assert question.selected == 1
    assert view.selected == 1


def test_p06_r02_the_game_screen_names_the_chosen_level() -> None:
    view = build_menu_view(state("game", chosen_level_id="1-1"), ctx())
    assert isinstance(view, GameScreenView)
    assert view.level == "Level 1-1"
    assert view.fire == "FIRE"
    assert view.paused is None
    assert view.complete is None


def test_p06_r02_an_unknown_level_is_labelled_with_a_question_mark() -> None:
    view = build_menu_view(state("game", chosen_level_id="9-9"), ctx())
    assert view.level == "Level ?"


def test_p06_r03_a_completed_level_shows_its_score_and_the_new_high_score() -> None:
    result = LevelResult("1-1", 10, 12, "complete", 1500.0, True, None)
    view = build_menu_view(state("game", level_result=result, chosen_level_id="1-1"), ctx())
    complete = view.complete
    assert complete.heading == "Level complete"
    assert complete.over is False
    assert complete.enemies == "10/12"
    assert complete.score == "Score 1500"
    assert complete.new_high_score == "New high score!"
    assert complete.choices is None


def test_p07_r08_a_game_over_with_a_checkpoint_offers_its_two_choices() -> None:
    checkpoint = LevelCheckpoint(0.4, 1, WeaponLevels("guns", {"guns": 1.0}), 800.0)
    result = LevelResult("1-1", 3, 9, "over", 800.0, False, checkpoint)
    view = build_menu_view(state("game", level_result=result, choice=1), ctx())
    complete = view.complete
    assert complete.heading == "Game over"
    assert complete.over is True
    assert complete.new_high_score is None
    assert complete.choices.labels == ["Continue", "Level select"]
    assert complete.choices.selected == 1
    assert view.selected == 1


def test_p12_r04_the_settings_screen_shows_one_slider_per_volume() -> None:
    view = build_menu_view(state("settings", selection=1), ctx())
    assert isinstance(view, SettingsView)
    assert [slider.label for slider in view.sliders] == ["Music", "Effects"]
    assert [slider.value for slider in view.sliders] == [5, 6]
    assert all(slider.max == 10 for slider in view.sliders)
    assert view.selected == 1
    assert view.over_level is False


def test_p12_r04_settings_opened_in_a_level_are_marked_over_the_level() -> None:
    view = build_menu_view(state("settings", paused=True), ctx())
    assert view.over_level is True


@pytest.mark.parametrize("screen", ["title", "game"])
def test_p01_r01_each_screen_name_gets_its_own_view(screen: str) -> None:
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
    return MenuViewContext(make_game(), 0, "1.0", "abc", 80, 0, 10, labels)


def test_d199_the_title_shows_the_dev_entry_only_with_the_dev_labels() -> None:
    assert build_menu_view(state("title"), ctx()).dev is None
    assert build_menu_view(state("title"), dev_ctx()).dev == "Dev"


def test_d199_the_dev_menu_lists_the_viewers() -> None:
    view = build_menu_view(state("dev", selection=2), dev_ctx())
    assert isinstance(view, DevMenuView)
    assert view.entries == ["Player ships", "Enemies", "Bosses", "Props", "Levels"]
    assert (view.selected, view.back) == (2, "Back")


def test_d199_a_model_viewer_shows_its_item_and_place_in_the_list() -> None:
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
