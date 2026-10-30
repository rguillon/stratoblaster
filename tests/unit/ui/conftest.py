"""Shared set-up of the UI tests: the browser's `window.Math` and `window.Number`, and the two
JavaScript-only helpers of the DOM (`replaceChildren`, `Array.from`), whose Python twins work on
the fake DOM of `helpers.dom`."""

import importlib

import pytest
from helpers import js_window

DOM_MODULES = ["ui.boss_bar", "ui.level_loading", "ui.screens.elements"]


@pytest.fixture(autouse=True)
def js_globals(monkeypatch: pytest.MonkeyPatch) -> None:
    js_window.install(monkeypatch)
    for name in DOM_MODULES:
        module = importlib.import_module(name)
        if hasattr(module, "replace_children"):
            monkeypatch.setattr(
                module, "replace_children", lambda el, nodes: el.replaceChildren(*nodes)
            )
        if hasattr(module, "array_from"):
            monkeypatch.setattr(module, "array_from", list)
