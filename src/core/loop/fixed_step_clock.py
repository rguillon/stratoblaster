"""Fixed-timestep accumulator (ENG-100)

It converts variable frame times into a whole number of fixed simulation steps plus an
interpolation factor for rendering.
"""

import math


class ClockAdvance:
    """Result of advancing the clock by one rendered frame."""

    def __init__(self, steps: int, alpha: float) -> None:
        """`steps` is the number of fixed simulation steps to run this frame; `alpha` the
        interpolation factor in [0, 1) between the previous and current simulation states.
        """
        self.steps = steps
        self.alpha = alpha


class FixedStepClock:
    """Fixed-timestep accumulator (ENG-100)."""

    def __init__(self, hz: float, max_steps_per_frame: int) -> None:
        """Raises if `hz` is not positive or `max_steps_per_frame` is below 1."""
        if hz <= 0 or max_steps_per_frame < 1:
            raise ValueError("hz must be > 0 and max_steps_per_frame >= 1")
        # Duration of one simulation step, in seconds.
        self.step_seconds = 1 / hz
        self._max_steps_per_frame = max_steps_per_frame
        self._accumulator = 0.0

    def advance(self, frame_seconds: float) -> ClockAdvance:
        """Advances by `frame_seconds` of real time. Excess time beyond the step cap is dropped."""
        self._accumulator += max(0, frame_seconds)
        steps = math.floor(self._accumulator / self.step_seconds)
        if steps > self._max_steps_per_frame:
            self._accumulator = 0.0
            return ClockAdvance(self._max_steps_per_frame, 0.0)
        self._accumulator -= steps * self.step_seconds
        return ClockAdvance(steps, self._accumulator / self.step_seconds)
