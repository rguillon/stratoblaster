"""Lowers an element's font size until it fits its parent, ported from `ui/shrink-to-fit.ts`."""

from org.transcrypt.stubs.browser import __pragma__, window

__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


def shrink_to_fit(el: Any, min_px: float = 12) -> None:
    """Lowers `el`'s font size, 1 px at a time, until it fits the width of its parent (or
    `min_px` is reached). The CSS sizes are tuned for condensed fonts; this keeps whole letters
    when the system falls back to a wider one. Does nothing while the element is not laid out.
    """
    parent = el.parentElement
    room = parent.clientWidth if parent else 0
    view = el.ownerDocument.defaultView
    style = view.getComputedStyle(el) if view else None
    if room == 0 or not style:
        return
    size = float(window.Number.parseFloat(style.fontSize))
    while el.scrollWidth > room and size > min_px:
        size -= 1
        el.style.fontSize = str(size) + "px"
