# Copyright (c) 2026 Renaud Guillon
"""Callbacks of the tappable parts of a menu screen.

A callback that does not apply to a screen is None.
"""

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from collections.abc import Callable

# __pragma__ ("noskip")


class ScreenHandlers:
    """The callbacks of a menu screen's tappable parts."""

    def __init__(
        self,
        on_tap: Callable[[int], None],
        on_back: Callable[[], None],
        on_fire: Callable[[bool], None] | None = None,
        on_drag: Callable[[float, float], None] | None = None,
        on_set: Callable[[int, float], None] | None = None,
        on_wheel: Callable[[float], None] | None = None,
        on_turn: Callable[[float, float], None] | None = None,
        on_hold: Callable[[bool], None] | None = None,
    ) -> None:
        # An entry of the screen was tapped or clicked.
        self.on_tap = on_tap
        # The on-screen Back button was tapped or clicked.
        self.on_back = on_back
        # Game screen: the touch fire button was pressed (`True`) or let go (GAME-CTRL-05).
        self.on_fire = on_fire
        # Game screen: a finger dragged over the playfield, by screen pixels (Y down).
        self.on_drag = on_drag
        # Settings screen: slider `index` was tapped or dragged to `value` (UI-SET-03).
        self.on_set = on_set
        # Dev viewer (D-199): the mouse wheel turned by this many pixels (down positive).
        self.on_wheel = on_wheel
        # Dev viewer (D-199): a mouse or finger drag by screen pixels (Y down), to turn the model.
        self.on_turn = on_turn
        # Dev audio viewer (DEV-MENU-19): a button is pressed and held (True), or let go (False).
        self.on_hold = on_hold
