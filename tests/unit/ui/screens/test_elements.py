"""Unit tests of `src/ui/screens/elements.py`."""

from helpers.dom import FakeDocument, FakeEvent

from ui.screens.elements import (
    SVG,
    back_button,
    element,
    entry,
    padlock,
    tap_listener,
)


def test_p01_r11_an_element_has_its_tag_class_and_text() -> None:
    doc = FakeDocument()
    el = element(doc, "h1", "title-name", "STRATO")
    assert el.tagName == "h1"
    assert el.className == "title-name"
    assert el.textContent == "STRATO"


def test_p01_r11_an_element_without_text_has_none() -> None:
    doc = FakeDocument()
    assert element(doc, "div", "x").textContent == ""


def test_p01_r11_a_tap_listener_reports_its_own_index() -> None:
    taps: list[int] = []
    first = tap_listener(taps.append, 1)
    second = tap_listener(taps.append, 4)
    first(FakeEvent())
    second(FakeEvent())
    assert taps == [1, 4]


def test_p01_r11_an_entry_is_a_button_div_that_reports_its_tap() -> None:
    doc = FakeDocument()
    taps: list[int] = []
    el = entry(doc, "level-cell", 3, False, taps.append)
    assert el.tagName == "div"
    assert el.className == "menu-entry level-cell"
    assert el.getAttribute("role") == "button"
    assert el.dataset.index == "3"
    assert not el.classList.contains("selected")
    assert el.getAttribute("aria-current") is None
    el.fire("click")
    assert taps == [3]


def test_p01_r11_a_selected_entry_is_marked_as_current() -> None:
    doc = FakeDocument()
    el = entry(doc, "title-start", 0, True, lambda index: None)
    assert el.classList.contains("selected")
    assert el.getAttribute("aria-current") == "true"


def test_p01_r11_the_back_button_has_the_label_and_runs_its_callback() -> None:
    doc = FakeDocument()
    calls: list[bool] = []
    el = back_button(doc, "Back", lambda: calls.append(True))
    assert el.textContent == "◀ Back"
    assert el.getAttribute("role") == "button"
    el.fire("click")
    assert calls == [True]


def test_p01_r13_the_padlock_is_an_svg_icon_with_an_accessible_name() -> None:
    doc = FakeDocument()
    lock = padlock(doc)
    assert lock.namespace == SVG
    assert lock.tagName == "svg"
    assert lock.getAttribute("aria-label") == "locked"
    assert lock.getAttribute("class") == "padlock"
    assert [child.tagName for child in lock.children] == ["path", "rect"]
