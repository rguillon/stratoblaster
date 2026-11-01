"""Unit tests of `src/ui/perf_overlay.py`."""

from helpers.dom import FakeDocument

from ui.perf_overlay import PerfNumbers, PerfOverlay


def numbers(last_load: float | None = None) -> PerfNumbers:
    return PerfNumbers(3, 42.4, 600, last_load, None, 150)


def test_dev_perf_03_the_overlay_is_hidden_until_toggled() -> None:
    doc = FakeDocument()
    overlay = PerfOverlay(doc, doc.createElement("div"), 0.25)
    assert overlay.root.hidden is True
    assert overlay.shown is False
    overlay.update(1.0, numbers())
    assert overlay.root.textContent == ""


def test_dev_perf_03_toggling_shows_the_overlay_and_its_numbers_at_once() -> None:
    doc = FakeDocument()
    overlay = PerfOverlay(doc, doc.createElement("div"), 0.25)
    overlay.toggle()
    assert overlay.shown is True
    overlay.update(0.0, numbers(last_load=812.2))
    assert overlay.root.textContent == (
        "Long frames: 3\nLongest frame: 42 ms\nDraw calls: 150\nLevel load: 812 ms"
    )


def test_dev_perf_03_a_missing_load_time_is_a_dash() -> None:
    doc = FakeDocument()
    overlay = PerfOverlay(doc, doc.createElement("div"), 0.25)
    overlay.toggle()
    overlay.update(0.0, numbers())
    assert overlay.root.textContent.endswith("Level load: –")


def test_dev_perf_03_the_text_changes_at_most_every_refresh_interval() -> None:
    doc = FakeDocument()
    overlay = PerfOverlay(doc, doc.createElement("div"), 0.25)
    overlay.toggle()
    overlay.update(0.0, numbers())
    first = overlay.root.textContent
    overlay.update(0.1, PerfNumbers(9, 99.0, 1, None, None, 150))
    assert overlay.root.textContent == first
    overlay.update(0.2, PerfNumbers(9, 99.0, 1, None, None, 150))
    assert "Long frames: 9" in overlay.root.textContent


def test_dev_perf_03_toggling_twice_hides_it_again() -> None:
    doc = FakeDocument()
    overlay = PerfOverlay(doc, doc.createElement("div"), 0.25)
    overlay.toggle()
    overlay.toggle()
    assert overlay.shown is False


def test_dev_perf_03_dispose_removes_the_overlay_from_the_page() -> None:
    doc = FakeDocument()
    parent = doc.createElement("div")
    overlay = PerfOverlay(doc, parent, 0.25)
    overlay.dispose()
    assert overlay.root.parentElement is None
    assert parent.children == []


def test_eng_106_the_overlay_shows_the_draw_calls_of_the_last_frame() -> None:
    doc = FakeDocument()
    overlay = PerfOverlay(doc, doc.createElement("div"), 0.25)
    overlay.toggle()
    overlay.update(0.0, PerfNumbers(0, 0.0, 0, None, None, 187.4))
    assert "Draw calls: 187" in overlay.root.textContent.split("\n")
