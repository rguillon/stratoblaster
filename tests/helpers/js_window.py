# Copyright (c) 2026 Renaud Guillon
"""The parts of the browser's `window` the UI reads (`window.Math`, `window.Number`).

They follow the JavaScript rules that matter here: `Math.round` rounds halves up, and numbers print
as JavaScript does. Installed on the stub's `window` by `install(monkeypatch)`.
"""

import math
from typing import Any

import pytest
from org.transcrypt.stubs.browser import window as browser_window


class JsNumber(float):
    """A JavaScript number: `toFixed` and `toLocaleString` as the browser has them."""

    def __str__(self) -> str:
        if self.is_integer():
            return str(int(self))
        return repr(float(self))

    def toFixed(self, digits: int = 0) -> str:
        return f"{float(self):.{digits}f}"

    def toLocaleString(self, _locale: str = "en-US") -> str:
        return f"{int(self):,}"


class FakeMath:
    @staticmethod
    def min(*values: float) -> JsNumber:
        return JsNumber(min(values))

    @staticmethod
    def max(*values: float) -> JsNumber:
        return JsNumber(max(values))

    @staticmethod
    def floor(value: float) -> JsNumber:
        return JsNumber(math.floor(value))

    @staticmethod
    def ceil(value: float) -> JsNumber:
        return JsNumber(math.ceil(value))

    @staticmethod
    def round(value: float) -> JsNumber:
        return JsNumber(math.floor(value + 0.5))


class FakeNumber:
    def __new__(cls, value: Any) -> JsNumber:  # type: ignore[misc]
        return JsNumber(value)

    @staticmethod
    def parseFloat(text: str) -> JsNumber:
        return JsNumber(float(text.strip().rstrip("px")))


def install(monkeypatch: pytest.MonkeyPatch) -> None:
    """Give the stub's `window` the `Math` and `Number` objects for the test."""
    monkeypatch.setattr(browser_window, "Math", FakeMath, raising=False)
    monkeypatch.setattr(browser_window, "Number", FakeNumber, raising=False)
