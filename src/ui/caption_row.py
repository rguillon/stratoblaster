# Copyright (c) 2026 Renaud Guillon
"""A row of titled text blocks."""

# isort: split
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


class Caption:
    """A titled block of text lines."""

    def __init__(self, title: str, lines: list[str]) -> None:
        self.title = title
        self.lines = lines


def render_caption_row(doc: Any, parent: Any, captions: list[Caption], width_percent: float) -> Any:
    """Render captions side by side in a row (styled by the page's `.caption-row` CSS).

    Appends it to `parent`. `width_percent` sets the row width, centred on the page.
    """
    row = doc.createElement("div")
    row.className = "caption-row"
    row.style.width = str(width_percent) + "%"
    for caption in captions:
        block = doc.createElement("div")
        block.className = "caption"
        title = doc.createElement("div")
        title.className = "caption-title"
        title.textContent = caption.title
        block.append(title)
        for line in caption.lines:
            el = doc.createElement("div")
            el.textContent = line
            block.append(el)
        row.append(block)
    parent.append(row)
    return row
