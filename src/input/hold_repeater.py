# Copyright (c) 2026 Renaud Guillon
"""Turns held keys into repeated presses (UI-INPUT-06).

A press is emitted at once, then again after `delay_seconds`, then every `interval_seconds` while
the key stays held.

Keys are strings: a Transcrypt dict keeps insertion order for them, as a JavaScript `Map` does.
"""


class HoldRepeater:
    """Repeats the keys held down (see the module doc)."""

    def __init__(self, delay_seconds: float, interval_seconds: float) -> None:
        if not (interval_seconds > 0) or delay_seconds < 0:
            msg = "interval_seconds must be > 0 and delay_seconds >= 0"
            raise ValueError(msg)
        self._delay = delay_seconds
        self._interval = interval_seconds
        self._timers: dict[str, float] = {}

    def press(self, key: str) -> bool:
        """Start holding `key`. Returns true when this is a new press (to be emitted at once)."""
        if key in self._timers:
            return False
        self._timers[key] = self._delay
        return True

    def release(self, key: str) -> None:
        """Stop holding `key`."""
        if key in self._timers:
            del self._timers[key]

    def release_all(self) -> None:
        """Stop holding every key."""
        self._timers.clear()

    @property
    def held(self) -> list[str]:
        """Keys currently held."""
        return list(self._timers.keys())

    def update(self, dt_seconds: float) -> list[str]:
        """Advances time and returns the repeats due, in order."""
        repeats: list[str] = []
        for key in list(self._timers.keys()):
            left = self._timers[key] - dt_seconds
            while left <= 0:
                repeats.append(key)
                left += self._interval
            self._timers[key] = left
        return repeats
