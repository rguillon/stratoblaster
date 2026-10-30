"""Unit tests of `src/app/menu_controller.py`."""
# (P01-R14, P11-R03, P12-R03, P12-R04).

import pytest
from helpers.menu_game import make_game

from app.menu_controller import MenuController, MenuControllerDeps
from app.saved_choices import saved_choice_keys
from app.saved_settings import saved_setting_keys
from core.systems.level_run_types import LevelResult
from host.key_value_storage import MemoryStorage
from input.menu_action import MenuSet
from ui.menu_view import GameScreenView, LoadingView, SettingsView, ShipSelectView, TitleView


class FakeDisplay:
    def __init__(self) -> None:
        self.views: list = []
        self.shaken: list[str] = []

    def show(self, view: object) -> None:
        self.views.append(view)

    def shake_selected(self, text: str) -> None:
        self.shaken.append(text)

    @property
    def last(self) -> object:
        return self.views[-1]


class FakeInput:
    def __init__(self) -> None:
        self.frames: list[list] = []
        self.dts: list[float] = []

    def update(self, dt_seconds: float) -> list:
        self.dts.append(dt_seconds)
        return self.frames.pop(0) if self.frames else []


def make(
    storage: MemoryStorage | None = None,
    *,
    on_change: object = None,
    on_feedback: object = None,
) -> tuple[MenuController, FakeDisplay, FakeInput, MemoryStorage]:
    display = FakeDisplay()
    inputs = FakeInput()
    store = storage if storage is not None else MemoryStorage()
    deps = MenuControllerDeps(
        display,
        inputs,
        store,
        0.25,
        None,
        80,
        "1.0",
        "abc",
        on_change,
        on_feedback,
    )
    return MenuController(make_game(), deps), display, inputs, store


def finish(controller: MenuController) -> None:
    """Finishes loading and lets the transition end, so commands are heard."""
    controller.finish_loading()
    controller.tick(1.0)


def go(controller: MenuController, *commands: object) -> None:
    """Sends each command, letting the screen transition of each one end."""
    for command in commands:
        controller.command(command)
        controller.tick(1.0)


def level_result(score: float, outcome: str = "complete") -> LevelResult:
    return LevelResult("1-1", 4, 5, outcome, score, False, None)


def test_p01_r02_the_menu_starts_on_the_loading_screen_and_shows_its_progress() -> None:
    controller, display, _, _ = make()
    assert isinstance(display.last, LoadingView)
    controller.set_progress(0.6)
    assert isinstance(display.last, LoadingView)
    assert display.last.progress == pytest.approx(0.6)


def test_p01_r04_finishing_the_loading_shows_the_title_with_the_saved_high_score() -> None:
    storage = MemoryStorage()
    storage.set(saved_choice_keys("stratoblaster").high_score, "700")
    controller, display, _, _ = make(storage)
    assert controller.high_score == 700
    finish(controller)
    assert isinstance(display.last, TitleView)
    assert display.last.high_score == 700


def test_p11_r03_a_score_above_the_high_score_is_saved_and_a_lower_one_is_not() -> None:
    controller, _, _, storage = make()
    assert controller.record_score(300) is True
    assert controller.high_score == 300
    assert storage.get(saved_choice_keys("stratoblaster").high_score) == "300"
    assert controller.record_score(200) is False
    assert controller.high_score == 300
    assert controller.record_score(300) is False


def test_p11_r03_a_completed_level_that_beats_the_score_says_so_on_its_panel() -> None:
    controller, display, _, _ = make()
    finish(controller)
    go(controller, "confirm", "confirm", "confirm")
    controller.complete_level(level_result(1200))
    assert controller.high_score == 1200
    game_view = display.last
    assert isinstance(game_view, GameScreenView)
    assert game_view.complete.new_high_score == "New high score!"


def test_p06_r09_a_direct_start_refreshes_the_display() -> None:
    controller, display, _, _ = make()
    finish(controller)
    assert controller.play_direct("alpha", "1-1") is True
    assert isinstance(display.last, GameScreenView)
    assert controller.play_direct("nope", "1-1") is False


def test_p01_r14_the_chosen_ship_is_remembered_for_next_time() -> None:
    controller, _, _, storage = make()
    finish(controller)
    go(controller, "confirm", "right", "confirm")
    assert storage.get(saved_choice_keys("stratoblaster").last_ship) == "beta"


def test_p01_r14_the_saved_ship_is_highlighted_when_the_menu_starts() -> None:
    storage = MemoryStorage()
    storage.set(saved_choice_keys("stratoblaster").last_ship, "beta")
    controller, display, _, _ = make(storage)
    finish(controller)
    controller.command("confirm")
    assert isinstance(display.last, ShipSelectView)
    assert display.last.selected == 1


def test_p12_r04_the_volumes_are_saved_on_every_change() -> None:
    controller, _, _, storage = make()
    finish(controller)
    go(controller, "confirm", "down", "down", "confirm")
    controller.command(MenuSet(0, 2))
    keys = saved_setting_keys("stratoblaster")
    assert storage.get(keys.music) == "2"
    assert storage.get(keys.sfx) == "8"


def test_p12_r04_saved_volumes_are_restored_when_the_menu_starts() -> None:
    storage = MemoryStorage()
    keys = saved_setting_keys("stratoblaster")
    storage.set(keys.music, "3")
    storage.set(keys.sfx, "4")
    controller, _, _, _ = make(storage)
    assert controller._saved_volumes.music == 3
    assert controller._saved_volumes.sfx == 4


def test_p12_r04_an_invalid_saved_volume_falls_back_to_the_default() -> None:
    storage = MemoryStorage()
    storage.set(saved_setting_keys("stratoblaster").music, "loud")
    controller, _, _, _ = make(storage)
    assert controller._saved_volumes.music == 6


def test_p01_r07_a_locked_pick_shakes_the_entry_with_the_locked_text() -> None:
    controller, display, _, _ = make()
    finish(controller)
    go(controller, "confirm", "confirm", "down", "confirm")
    assert display.shaken == ["Locked"]


def test_p12_r09_every_command_is_reported_with_its_feedback() -> None:
    feedback: list = []
    controller, _, _, _ = make(
        on_feedback=lambda command, result: feedback.append((command, result))
    )
    finish(controller)
    controller.command("down")
    assert feedback == [("down", "moved")]


def test_p12_r03_pausing_reports_the_pause_and_refreshes() -> None:
    feedback: list = []
    controller, display, _, _ = make(on_feedback=lambda c, r: feedback.append((c, r)))
    finish(controller)
    go(controller, "confirm", "confirm", "confirm")
    assert controller.pause() is True
    assert feedback[-1] == ("pause", "paused")
    assert isinstance(display.last, GameScreenView)
    assert controller.pause() is False


def test_p01_r13_the_input_of_each_frame_is_applied_after_the_transition_timer() -> None:
    controller, display, inputs, _ = make()
    finish(controller)
    inputs.frames.append(["down"])
    controller.tick(0.1)
    assert inputs.dts[-1] == 0.1
    assert isinstance(display.last, TitleView)
    assert display.last.selected == 1


def test_p01_r13_the_view_is_redrawn_only_when_something_changed() -> None:
    controller, display, _, _ = make()
    finish(controller)
    count = len(display.views)
    controller.refresh()
    assert len(display.views) == count
    controller.set_progress(0.0)
    assert len(display.views) == count


def test_p01_r13_the_scene_callback_runs_after_each_redraw() -> None:
    seen: list = []
    controller, _, _, _ = make(on_change=seen.append)
    finish(controller)
    assert seen
    assert seen[-1].screen == "title"


def test_p01_r13_the_settings_screen_is_shown_when_chosen() -> None:
    controller, display, _, _ = make()
    finish(controller)
    go(controller, "down", "confirm")
    assert isinstance(display.last, SettingsView)


def test_d199_the_dev_labels_give_the_flow_its_counts_and_the_views_their_items() -> None:
    labels = {"ships": ["A", "B"], "enemies": [], "bosses": [], "props": [], "levels": ["1-1"]}
    display = FakeDisplay()
    deps = MenuControllerDeps(
        display, FakeInput(), MemoryStorage(), 0.25, None, 80, "1.0", "abc", None, None, labels
    )
    controller = MenuController(make_game(), deps)
    finish(controller)
    assert display.last.dev == "Dev"
    for command in ["down", "down", "confirm"]:
        controller.command(command)
    controller.tick(1.0)
    controller.command("confirm")
    controller.tick(1.0)
    controller.command("left")
    assert (display.last.item, display.last.position) == ("B", "2 / 2")
