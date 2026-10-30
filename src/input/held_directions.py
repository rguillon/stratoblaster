"""Movement keys held down, as a direction to fly in (ported from `input/held-directions.ts`).
`DIRECTION_KEYS`: `KeyboardEvent.code` -> direction; arrows and WASD by key position (AZERTY works
too, GD §2)."""

import math

from org.transcrypt.stubs.browser import __pragma__

from core.systems.player_flight import FlightInput

__pragma__("skip")
from input.menu_action import MenuDirection  # noqa: E402

__pragma__("noskip")

DIRECTION_KEYS = {
    "ArrowUp": "up",
    "ArrowDown": "down",
    "ArrowLeft": "left",
    "ArrowRight": "right",
    "KeyW": "up",
    "KeyS": "down",
    "KeyA": "left",
    "KeyD": "right",
}


class HeldDirections:
    """The movement keys held down, as a direction to fly in: X right, Y up, at most length 1 (so
    diagonals are not faster)."""

    def __init__(self) -> None:
        self._held: list[str] = []

    def key(self, code: str, down: bool) -> bool:
        """Records a key going down or up; returns whether it is a movement key."""
        if code not in DIRECTION_KEYS:
            return False
        if down:
            if code not in self._held:
                self._held.append(code)
        elif code in self._held:
            self._held.remove(code)
        return True

    def clear(self) -> None:
        """Releases every key (e.g. when the window loses the focus)."""
        self._held.clear()

    @property
    def direction(self) -> FlightInput:
        held: list[MenuDirection] = [DIRECTION_KEYS[code] for code in self._held]
        x = (1 if "right" in held else 0) - (1 if "left" in held else 0)
        y = (1 if "up" in held else 0) - (1 if "down" in held else 0)
        length = math.hypot(x, y) or 1
        return FlightInput(x / length, y / length)
