# Copyright (c) 2026 Renaud Guillon
"""WebGL2 support check (ENG-06)."""

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from collections.abc import Callable
from typing import Protocol


class CanvasLike(Protocol):
    """Minimal canvas shape needed to probe WebGL2, so the check is testable without a DOM."""

    # The DOM method keeps its JavaScript name: it is called on a real canvas element.
    def getContext(self, context_id: str) -> object:
        """Return the context `context_id`, or None when unsupported."""


# __pragma__ ("noskip")


def has_webgl2(create_canvas: Callable[[], CanvasLike]) -> bool:
    """Return true when the browser can create a WebGL2 context (ENG-06)."""
    try:
        # `!= None` is JavaScript's `!= null`: a context of `undefined` counts as missing too
        # (ENG-161).
        return create_canvas().getContext("webgl2") != None
    except:
        return False
