"""Unit tests of `src/ui/screens/settings_screen.py`."""

from helpers.dom import FakeDocument, FakeEvent

from ui.menu_view import SettingsView, SliderView
from ui.screens.screen_handlers import ScreenHandlers
from ui.screens.settings_screen import render_settings_screen


def render(sets: list[tuple[int, float]], selected: int = 0, over: bool = False) -> object:
    sliders = [SliderView("Music", 3, 10), SliderView("Effects", 8, 10)]
    view = SettingsView("Sound", "Drag or tap", "Back", selected, sliders, over)
    handlers = ScreenHandlers(
        lambda index: None,
        lambda: None,
        on_set=lambda index, value: sets.append((index, value)),
    )
    return render_settings_screen(FakeDocument(), view, handlers)


def test_p12_r04_each_slider_is_a_row_with_its_label_value_and_range() -> None:
    root = render([])
    rows = root.querySelector(".settings-list").children
    assert len(rows) == 2
    music = rows[0]
    assert music.getAttribute("role") == "slider"
    assert music.getAttribute("aria-label") == "Music"
    assert music.getAttribute("aria-valuemax") == "10"
    assert music.getAttribute("aria-valuenow") == "3"
    assert music.querySelector(".slider-label").textContent == "Music"
    assert music.querySelector(".slider-value").textContent == "3"


def test_p12_r04_the_bar_lights_the_cells_up_to_the_value() -> None:
    root = render([])
    cells = root.querySelector(".settings-list").children[0].querySelectorAll(".slider-cell")
    assert len(cells) == 10
    assert [cell.classList.contains("on") for cell in cells] == [True] * 3 + [False] * 7


def test_p12_r04_tapping_the_bar_sets_the_slider_to_the_value_under_the_pointer() -> None:
    sets: list[tuple[int, float]] = []
    root = render(sets)
    bar = root.querySelector(".settings-list").children[1].querySelector(".slider-bar")
    bar.rect.left = 0
    bar.rect.width = 100
    bar.fire("pointerdown", FakeEvent(x=70))
    assert sets == [(1, 7)]


def test_p12_r04_dragging_the_bar_keeps_setting_it_while_the_pointer_is_down() -> None:
    sets: list[tuple[int, float]] = []
    root = render(sets)
    bar = root.querySelector(".settings-list").children[0].querySelector(".slider-bar")
    bar.rect.width = 100
    bar.fire("pointermove", FakeEvent(x=20))
    assert sets == []
    bar.fire("pointerdown", FakeEvent(x=20))
    bar.fire("pointermove", FakeEvent(x=60))
    bar.fire("pointerup")
    bar.fire("pointermove", FakeEvent(x=90))
    assert sets == [(0, 2), (0, 6)]


def test_p12_r04_the_bar_of_zero_width_sets_nothing_useful() -> None:
    sets: list[tuple[int, float]] = []
    root = render(sets)
    bar = root.querySelector(".settings-list").children[0].querySelector(".slider-bar")
    bar.fire("pointerdown", FakeEvent(x=50))
    assert sets == [(0, 0)]


def test_p12_r04_a_bar_click_does_not_also_select_its_row() -> None:
    root = render([])
    bar = root.querySelector(".settings-list").children[0].querySelector(".slider-bar")
    event = FakeEvent()
    bar.fire("click", event)
    assert event.stopped is True


def test_p12_r04_the_screen_marks_when_it_is_over_a_level() -> None:
    assert render([], over=True).className == "menu-screen settings-screen over-level"
    assert render([]).className == "menu-screen settings-screen"


def test_p12_r04_the_selected_row_is_highlighted_and_back_is_there() -> None:
    root = render([], selected=1)
    rows = root.querySelector(".settings-list").children
    assert rows[1].classList.contains("selected")
    assert root.querySelector(".menu-back") is not None
