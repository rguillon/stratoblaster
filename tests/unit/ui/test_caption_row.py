"""Unit tests of `src/ui/caption_row.py`."""

from helpers.dom import FakeDocument

from ui.caption_row import Caption, render_caption_row


def test_p03_captions_render_side_by_side_in_a_row_centred_at_the_width() -> None:
    doc = FakeDocument()
    parent = doc.createElement("div")
    captions = [Caption("Alpha", ["Speed x1", "HP 5"]), Caption("Beta", [])]
    row = render_caption_row(doc, parent, captions, 80)
    assert row.className == "caption-row"
    assert row.style.width == "80%"
    assert row.parentElement is parent
    blocks = row.children
    assert [block.className for block in blocks] == ["caption", "caption"]


def test_p03_each_caption_shows_its_title_then_its_lines() -> None:
    doc = FakeDocument()
    row = render_caption_row(doc, doc.createElement("div"), [Caption("Alpha", ["a", "b"])], 50)
    block = row.children[0]
    assert block.children[0].className == "caption-title"
    assert block.children[0].textContent == "Alpha"
    assert [line.textContent for line in block.children[1:]] == ["a", "b"]
