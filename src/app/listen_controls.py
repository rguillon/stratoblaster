"""Keyboard listeners of the level (ported from `app/listen-controls.ts`): keys go to the level's
debug keys first (when on), then to the in-game controls.
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Any  # noqa: E402

__pragma__("noskip")


def listen_controls(
    target: Any,
    controls: Any,
    game: Callable[[], Any],
) -> Callable[[], None]:
    """Listens for keys and focus loss on `target` (an event target, or None: nothing listens),
    feeding `controls`. `game()` returns the level being played, or None. Returns the function
    that stops listening.
    """
    if target is None:
        return _stop_nothing

    def on_key(event: Any) -> None:
        code = event.code
        down = event.type == "keydown"
        play = game()
        # The debug keys of the level take their keys first, when they are on.
        if not (play and play.debug_key(code, down)):
            controls.key(code, down)

    def on_blur() -> None:
        controls.clear()

    target.addEventListener("keydown", on_key)
    target.addEventListener("keyup", on_key)
    target.addEventListener("blur", on_blur)

    def stop() -> None:
        target.removeEventListener("keydown", on_key)
        target.removeEventListener("keyup", on_key)
        target.removeEventListener("blur", on_blur)

    return stop


def _stop_nothing() -> None:
    return None
