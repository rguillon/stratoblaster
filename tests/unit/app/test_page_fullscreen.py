# Copyright (c) 2026 Renaud Guillon
"""Unit tests of `src/app/page_fullscreen.py` (UI-TITLE-11)."""

from typing import Any

from app.page_fullscreen import PageFullscreen


class FakeRoot:
    def __init__(self, doc: "FakeDocument") -> None:
        self._doc = doc

    def requestFullscreen(self) -> str:
        self._doc.calls.append("request")
        self._doc.fullscreenElement = self
        return "promise"


class FakeDocument:
    def __init__(self, enabled: bool = True) -> None:
        self.fullscreenEnabled = enabled
        self.fullscreenElement: Any = None
        self.documentElement = FakeRoot(self)
        self.calls: list[str] = []
        self.listeners: dict[str, Any] = {}

    def exitFullscreen(self) -> str:
        self.calls.append("exit")
        self.fullscreenElement = None
        return "promise"

    def addEventListener(self, name: str, listener: Any) -> None:
        self.listeners[name] = listener


def test_ui_title_11_full_screen_is_supported_where_the_browser_allows_it() -> None:
    assert PageFullscreen(FakeDocument()).supported() is True
    assert PageFullscreen(FakeDocument(enabled=False)).supported() is False
    doc = FakeDocument()
    doc.documentElement = None
    assert PageFullscreen(doc).supported() is False


def test_ui_title_11_toggle_asks_for_full_screen_then_leaves_it() -> None:
    doc = FakeDocument()
    page = PageFullscreen(doc)
    assert page.active() is False
    page.toggle()
    assert page.active() is True
    page.toggle()
    assert page.active() is False
    assert doc.calls == ["request", "exit"]


def test_ui_title_11_a_change_of_full_screen_is_heard() -> None:
    doc = FakeDocument()
    heard: list[int] = []
    PageFullscreen(doc).listen(lambda: heard.append(1))
    doc.listeners["fullscreenchange"]("event")
    assert heard == [1]
