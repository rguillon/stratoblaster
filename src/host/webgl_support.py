"""WebGL2 support check (ENG-06)"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Protocol  # noqa: E402


class CanvasLike(Protocol):
    """Minimal canvas shape needed to probe WebGL2, so the check is testable without a DOM."""

    # The DOM method keeps its JavaScript name: it is called on a real canvas element.
    def getContext(self, context_id: str) -> object: ...  # noqa: N802


__pragma__("noskip")


def has_webgl2(create_canvas: Callable[[], CanvasLike]) -> bool:
    """Returns true when the browser can create a WebGL2 context (ENG-06)."""
    try:
        # `!= None` is JavaScript's `!= null`: a context of `undefined` counts as missing too.
        return create_canvas().getContext("webgl2") != None  # noqa: E711
    except:  # noqa: E722 (a failure while creating the canvas means no WebGL2)
        return False
