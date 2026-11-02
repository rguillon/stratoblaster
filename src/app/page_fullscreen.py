# Copyright (c) 2026 Renaud Guillon
"""The page's full screen (UI-TITLE-11): the title's Full screen entry toggles it.

A thin wrapper of the Fullscreen API on a document: whether the browser allows it, whether the
page is full screen now, toggling it, and hearing it change (the browser leaves full screen by
itself on Escape). The request may be refused (no user gesture, a browser's policy): the refusal
is swallowed, and the page simply stays as it is.
"""

from org.transcrypt.stubs.browser import __pragma__

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


def _swallow(promise: Any) -> None:
    """Ignore the refusal of a fullscreen request (`promise?.catch(() => {})`)."""
    __pragma__("js", "{}", "if (promise && promise.catch) promise.catch(() => {});")


class PageFullscreen:
    """The full screen of `doc` (the document)."""

    def __init__(self, doc: Any) -> None:
        self._doc = doc

    def supported(self) -> bool:
        """Whether the browser lets the page go full screen (`document.fullscreenEnabled`)."""
        doc = self._doc
        enabled: bool = doc.fullscreenEnabled
        root = doc.documentElement
        return bool(enabled) and root is not None and root.requestFullscreen is not None

    def active(self) -> bool:
        """Whether the page is full screen now."""
        element: Any = self._doc.fullscreenElement
        return element is not None

    def toggle(self) -> None:
        """Leave full screen when in it, else ask for it."""
        doc = self._doc
        if self.active():
            _swallow(doc.exitFullscreen())
        else:
            _swallow(doc.documentElement.requestFullscreen())

    def listen(self, on_change: Any) -> None:
        """Call `on_change` whenever the page enters or leaves full screen."""
        self._doc.addEventListener("fullscreenchange", lambda _event: on_change())
