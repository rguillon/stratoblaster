"""Callbacks of the tappable parts of a menu screen
A callback that does not apply to a screen is None."""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402

__pragma__("noskip")


class ScreenHandlers:
    """The callbacks of a menu screen's tappable parts."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        on_tap: Callable[[int], None],
        on_back: Callable[[], None],
        on_fire: Callable[[bool], None] | None = None,
        on_drag: Callable[[float, float], None] | None = None,
        on_pause: Callable[[], None] | None = None,
        on_set: Callable[[int, float], None] | None = None,
        on_wheel: Callable[[float], None] | None = None,
        on_turn: Callable[[float, float], None] | None = None,
    ) -> None:
        # An entry of the screen was tapped or clicked.
        self.on_tap = on_tap
        # The on-screen Back button was tapped or clicked.
        self.on_back = on_back
        # Game screen: the touch fire button was pressed (`True`) or let go (P06-R02).
        self.on_fire = on_fire
        # Game screen: a finger dragged over the playfield, by screen pixels (Y down).
        self.on_drag = on_drag
        # Game screen: the on-screen pause button was tapped (P12-R01).
        self.on_pause = on_pause
        # Settings screen: slider `index` was tapped or dragged to `value` (P12-R04).
        self.on_set = on_set
        # Dev viewer (D-199): the mouse wheel turned by this many pixels (down positive).
        self.on_wheel = on_wheel
        # Dev viewer (D-199): a mouse or finger drag by screen pixels (Y down), to turn the model.
        self.on_turn = on_turn
