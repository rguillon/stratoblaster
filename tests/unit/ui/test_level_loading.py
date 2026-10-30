"""Unit tests of `src/ui/level_loading.py`."""

from helpers.dom import FakeDocument

from ui.level_loading import LevelLoadingScreen


def test_p13_r03_the_loading_screen_is_added_to_the_page_with_its_text() -> None:
    doc = FakeDocument()
    parent = doc.createElement("div")
    screen = LevelLoadingScreen(doc, parent, "Loading level 2")
    screen.show(0.0)
    assert len(parent.children) == 1
    root = parent.children[0]
    assert root.classList.contains("level-loading")
    assert root.querySelector(".loading-text").textContent == "Loading level 2"


def test_p13_r03_later_progress_updates_the_same_screen_in_place() -> None:
    doc = FakeDocument()
    parent = doc.createElement("div")
    screen = LevelLoadingScreen(doc, parent, "Loading")
    screen.show(0.0)
    root = parent.children[0]
    screen.show(0.5)
    assert parent.children == [root]
    assert root.querySelector(".loading-percent").textContent == "50 %"
    screen.show(1.0)
    assert root.querySelector(".loading-percent").textContent == "100 %"


def test_p13_r03_disposing_removes_the_screen_and_a_new_one_can_be_shown() -> None:
    doc = FakeDocument()
    parent = doc.createElement("div")
    screen = LevelLoadingScreen(doc, parent, "Loading")
    screen.show(0.2)
    screen.dispose()
    assert parent.children == []
    screen.dispose()
    screen.show(0.3)
    assert len(parent.children) == 1
