# Copyright (c) 2026 Renaud Guillon
"""Keyboard listeners of the level: keys go to the level's debug keys first (when on, DEV-OPT-08).

Then to the in-game controls. Losing the focus lets every key go (GAME-CTRL-07).
"""

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from collections.abc import Callable
from typing import Any

# __pragma__ ("noskip")


def listen_controls(
    target: Any,
    controls: Any,
    game: Callable[[], Any],
) -> Callable[[], None]:
    """Listen for keys and focus loss on `target` (an event target, or None: nothing listens).

    Feeding `controls`. `game()` returns the level being played, or None. Returns the function that
    stops listening.
    """
    if target is None:
        return _stop_nothing

    def on_key(event: Any) -> None:
        code = event.code
        down = event["type"] == "keydown"
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
