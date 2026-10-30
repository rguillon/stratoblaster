"""Stand-ins for Babylon.js in the view tests: Babylon runs only in the browser, so the view modules
that build meshes are tested with `MagicMock` objects in place of the `render.babylon` helpers.

`stub_babylon` replaces, in one module, every helper it imported from `render.babylon` (each call
then gives a fresh `MagicMock`) and the few JavaScript-only twins the module calls (a plain object
or a JavaScript value). CPython runs those twins' Python fallback bodies, which return None, so
they are given working replacements here.
"""

import sys
from types import ModuleType, SimpleNamespace
from typing import Any
from unittest.mock import MagicMock

import pytest

from render import babylon

# JavaScript-only helpers the view modules call, with a Python equivalent: a plain object holding
# the arguments they are given (`{sync, dispose}` of a renderer, the look of a flash...).
JS_TWINS = {
    "_shot_renderer": lambda sync, dispose: {"sync": sync, "dispose": dispose},
    "_bomb_renderer": lambda sync, dispose: {"sync": sync, "dispose": dispose},
    "_exhaust": lambda sync, dispose: {"sync": sync, "dispose": dispose},
    "_bonus_renderer": lambda sync, dispose: {"sync": sync, "dispose": dispose},
    "flash_look": lambda colors, segments: SimpleNamespace(colors=colors, segments=segments),
    "_badge_colors": lambda frame, face, chevrons, inset: SimpleNamespace(
        frame=frame, face=face, chevrons=chevrons, inset=inset
    ),
}


def _fake(*_args: Any, **_kwargs: Any) -> MagicMock:
    return MagicMock()


def stub_babylon(monkeypatch: pytest.MonkeyPatch, *modules: ModuleType) -> None:
    """Replaces the `render.babylon` helpers the modules imported, and their JavaScript-only twins.

    The modules given are patched, and so is every module of `render/` and `game/view/` loaded so
    far: a helper that one of them calls through another's import is stubbed as well.
    """
    loaded = [
        module
        for name, module in list(sys.modules.items())
        if module is not None
        and (name.startswith(("render.", "game.view.")) or name == "render.babylon")
    ]
    for module in [*modules, *loaded]:
        for name, value in list(vars(module).items()):
            if callable(value) and getattr(value, "__module__", None) == babylon.__name__:
                monkeypatch.setattr(module, name, _fake)
        for name, twin in JS_TWINS.items():
            if hasattr(module, name):
                monkeypatch.setattr(module, name, twin)
