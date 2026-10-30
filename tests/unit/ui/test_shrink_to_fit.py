"""Unit tests of `src/ui/shrink_to_fit.py`."""

from helpers.dom import FakeDocument, FakeElement

from ui.shrink_to_fit import shrink_to_fit


class Text(FakeElement):
    """A line of text whose width is its length times the font size (0.6 em a letter)."""

    @property
    def scrollWidth(self) -> float:  # noqa: N802
        size = float(self.style.fontSize.rstrip("px")) if self.style.fontSize else 16.0
        return len(self.textContent) * size * 0.6

    @scrollWidth.setter
    def scrollWidth(self, value: float) -> None:  # noqa: N802
        """The base class sets it; the text computes its own."""


def make_title(doc: FakeDocument, text: str, room: float) -> Text:
    parent = doc.createElement("div")
    parent.clientWidth = room
    el = Text(doc, "h1")
    el.textContent = text
    parent.append(el)
    return el


def test_p01_r13_a_title_wider_than_its_parent_is_shrunk_one_pixel_at_a_time() -> None:
    doc = FakeDocument()
    el = make_title(doc, "STRATOBLASTER", 200)
    shrink_to_fit(el)
    # 13 letters at 0.6 em are about 125 px at 16 px: they fit already.
    assert el.style.fontSize == ""
    el.textContent = "STRATOBLASTER" * 2
    shrink_to_fit(el)
    fitted = float(el.style.fontSize.rstrip("px"))
    assert el.scrollWidth <= 200
    assert fitted < 16


def test_p01_r13_the_font_never_goes_below_its_minimum() -> None:
    doc = FakeDocument()
    el = make_title(doc, "X" * 500, 100)
    shrink_to_fit(el, min_px=12)
    assert float(el.style.fontSize.rstrip("px")) == 12


def test_p01_r13_an_element_not_laid_out_is_left_alone() -> None:
    doc = FakeDocument()
    el = make_title(doc, "STRATOBLASTER", 0)
    shrink_to_fit(el)
    assert el.style.fontSize == ""


def test_p01_r13_an_element_without_a_parent_is_left_alone() -> None:
    doc = FakeDocument()
    el = Text(doc, "h1")
    el.textContent = "X" * 100
    shrink_to_fit(el)
    assert el.style.fontSize == ""
