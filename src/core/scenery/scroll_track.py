"""How far a scrolling level has gone (P04-R06)

The ground scrolls at `speed` world units per second from distance 0 to `length`, then the level
has ended and the track stops.

Two distances are kept (P07-R03): `distance`, the ground flown over (what the scenery shows), and
`progress`, how far the level has got (what its waves and bosses are placed by). They move
together, except while the track is `held` (a boss fight): the ground goes on, the level does not.
The ground's speed is `speed` times a factor that eases from one value to another
(`set_speed_factor`).
"""


def _smooth(t: float) -> float:
    """Smooth 0..1 ease of `t` in 0..1 (zero slope at both ends)."""
    return t * t * (3 - 2 * t)


class _Ease:
    """A speed-factor ease in progress."""

    def __init__(self, from_: float, to: float, seconds: float) -> None:
        self.from_ = from_
        self.to = to
        self.seconds = seconds
        self.done = 0.0


class ScrollTrack:
    """The scroll position of a level."""

    def __init__(self, speed: float, length: float) -> None:
        if not (speed > 0):
            raise ValueError("The scroll speed must be positive")
        if not (length >= 0):
            raise ValueError("The level length cannot be negative")
        self.speed = speed
        self.length_ = length
        self._progress = 0.0
        self._distance = 0.0
        self._factor = 1.0
        self._ease: _Ease | None = None
        self.time_scale = 1.0
        """Simulated seconds per real second (e.g. 4 to fast-forward); 0 pauses."""
        self.held = False
        """While held, the ground scrolls but the level's progress stays where it is."""

    @property
    def duration(self) -> float:
        """Seconds the whole level takes at speed × 1."""
        return self.length_ / self.speed

    @property
    def time(self) -> float:
        """Seconds of the level flown at speed × 1 (its progress, in time)."""
        return self._progress / self.speed

    @property
    def progress(self) -> float:
        """How far the level has got, from 0 to `length`."""
        return self._progress

    @property
    def distance(self) -> float:
        """Ground flown over, i.e. Z of the bottom of the playfield."""
        return self._distance

    @property
    def speed_factor(self) -> float:
        """The factor on `speed` the ground scrolls at now."""
        return self._factor

    @property
    def ended(self) -> bool:
        return self._progress >= self.length_

    def set_speed_factor(self, factor: float, seconds: float) -> None:
        """Eases the ground's speed factor from where it is to `factor` over `seconds`."""
        if not (factor >= 0):
            raise ValueError("The speed factor cannot be negative")
        if seconds <= 0:
            self._factor = factor
            self._ease = None
            return
        self._ease = _Ease(self._factor, factor, seconds)

    def step(self, dt: float) -> None:
        """Advances by `dt` real seconds (times `time_scale`), stopping at the end unless held."""
        seconds = max(0, dt) * self.time_scale
        self._step_ease(seconds)
        run = self.speed * self._factor * seconds
        if not self.held:
            run = min(run, max(0, self.length_ - self._progress))
            self._progress += run
        self._distance += run

    def _step_ease(self, seconds: float) -> None:
        ease = self._ease
        if ease is None:
            return
        ease.done = min(ease.seconds, ease.done + seconds)
        t = _smooth(ease.done / ease.seconds)
        self._factor = ease.from_ + (ease.to - ease.from_) * t
        if ease.done >= ease.seconds:
            self._ease = None

    def seek(self, time: float) -> None:
        """Jumps to `time` seconds of the level, kept within it. The ground keeps the lead it took
        during held stretches, so the scenery does not jump back."""
        lead = self._distance - self._progress
        self._progress = min(self.length_, max(0, time * self.speed))
        self._distance = self._progress + lead

    def restart(self) -> None:
        self._progress = 0.0
        self._distance = 0.0
        self._factor = 1.0
        self._ease = None
        self.held = False
