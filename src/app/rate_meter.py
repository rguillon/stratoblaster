"""Measures how fast a running total grows, over a sliding time window ()."""


class RateMeter:
    """Measures how fast a running total grows, over a sliding time window."""

    def __init__(self, window_seconds: float) -> None:
        self._window_seconds = window_seconds
        # The samples, oldest first: their times and their running totals, in parallel lists.
        self._times: list[float] = []
        self._totals: list[float] = []
        self._time = 0.0

    def add(self, dt: float, total: float) -> None:
        """Records the running `total` after `dt` more seconds."""
        self._time += dt
        self._times.append(self._time)
        self._totals.append(total)
        # Drop the samples that fell out of the window, keeping the last one before it.
        while len(self._times) > 1 and self._times[1] <= self._time - self._window_seconds:
            self._times.pop(0)
            self._totals.pop(0)

    @property
    def rate(self) -> float:
        """Growth per second over the window (over less time until a full window has passed)."""
        count = len(self._times)
        if count == 0:
            return 0
        first_time = self._times[0]
        last_time = self._times[count - 1]
        if last_time <= first_time:
            return 0
        return (self._totals[count - 1] - self._totals[0]) / (last_time - first_time)
