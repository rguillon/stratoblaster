"""Unit tests of `src/ui/screens/pause_panel.py`."""

from helpers.dom import FakeDocument

from ui.menu_view import PauseQuestion, PauseView
from ui.screens.pause_panel import pause_panel
from ui.screens.screen_handlers import ScreenHandlers


def test_p12_r02_the_pause_menu_lists_its_entries_with_the_selection_and_hint() -> None:
    taps: list[int] = []
    view = PauseView("Paused", ["Resume", "Leave"], "P to resume")
    dim = pause_panel(FakeDocument(), view, 1, ScreenHandlers(taps.append, lambda: None))
    assert dim.className == "pause-dim"
    panel = dim.children[0]
    assert panel.querySelector(".pause-heading").textContent == "Paused"
    entries = panel.querySelectorAll(".pause-entry")
    assert [entry.textContent for entry in entries] == ["Resume", "Leave"]
    assert entries[1].classList.contains("selected")
    assert panel.querySelector(".pause-hint").textContent == "P to resume"
    entries[0].fire("click")
    assert taps == [0]


def test_p12_r02_the_leave_question_has_its_text_and_choices() -> None:
    taps: list[int] = []
    question = PauseQuestion("Leave the level?", ["No", "Yes"], 0)
    view = PauseView("Paused", ["Resume", "Leave"], "hint", question)
    dim = pause_panel(FakeDocument(), view, 0, ScreenHandlers(taps.append, lambda: None))
    box = dim.children[0].querySelector(".pause-question")
    assert box.querySelector(".pause-question-text").textContent == "Leave the level?"
    choices = box.querySelectorAll(".pause-choice")
    assert [choice.textContent for choice in choices] == ["No", "Yes"]
    assert choices[0].classList.contains("selected")
    assert dim.children[0].querySelector(".pause-entry") is None
    choices[1].fire("click")
    assert taps == [1]
