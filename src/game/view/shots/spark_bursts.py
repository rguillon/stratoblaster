"""Bursts of metal sparks where bullets hit (P03-R01, phase 3 review), ported from
`shots/spark-bursts.ts`.

Each burst throws `count` sparks back from the hit, spread around straight down; they slow down
with drag, twinkle, and shrink to nothing over their life.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from typing import Any  # noqa: E402

from core.math.rng import Random  # noqa: E402

__pragma__("noskip")

from core.math.rng import random_in  # noqa: E402


class Spark:
    """A spark in flight (internal to `SparkBursts`)."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        x: float,
        y: float,
        vx: float,
        vy: float,
        life: float,
        length: float,
        twinkle_hz: float,
        phase: float,
    ) -> None:
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.age = 0.0
        self.life = life
        self.length_ = length
        self.twinkleHz = twinkle_hz
        self.phase = phase


class SparkSpot:
    """A spark to draw: a streak along its motion, `length` long, at `brightness` (0..1)."""

    def __init__(
        self, x: float, y: float, heading: float, length: float, brightness: float
    ) -> None:
        self.x = x
        self.y = y
        # Direction of motion, radians from +Y, positive to the right.
        self.heading = heading
        self.length_ = length
        self.brightness = brightness


class SparkBursts:
    """Bursts of metal sparks where bullets hit (P03-R01, phase 3 review)."""

    def __init__(self, options: Any, random: Random) -> None:
        self._options = options
        self._random = random
        self._sparks: list[Spark] = []

    @property
    def count(self) -> int:
        """Number of sparks alive."""
        return len(self._sparks)

    def emit(self, x: float, y: float) -> None:
        """Throws a burst of sparks from (x, y)."""
        o = self._options
        random = self._random
        spread = (o.spreadDeg * math.pi) / 180
        for _ in range(o.count):
            heading = math.pi + random_in(random, -spread, spread)
            speed = random_in(random, o.speed[0], o.speed[1])
            self._sparks.append(
                Spark(
                    x,
                    y,
                    math.sin(heading) * speed,
                    math.cos(heading) * speed,
                    random_in(random, o.life[0], o.life[1]),
                    random_in(random, o.length[0], o.length[1]),
                    random_in(random, o.twinkleHz[0], o.twinkleHz[1]),
                    random() * 2 * math.pi,
                )
            )

    def step(self, dt: float) -> list[SparkSpot]:
        """Moves and ages the sparks by `dt`, drops the dead ones, returns where to draw them."""
        slow = math.exp(-self._options.drag * dt)
        spots: list[SparkSpot] = []
        i = len(self._sparks) - 1
        while i >= 0:
            s: Any = self._sparks[i]
            i -= 1
            if not s:
                continue
            s.age += dt
            if s.age >= s.life:
                self._sparks.pop(i + 1)
                continue
            s.vx *= slow
            s.vy *= slow
            s.x += s.vx * dt
            s.y += s.vy * dt
            fade = 1 - s.age / s.life
            twinkle = 1 - self._options.twinkle * (
                0.5 + 0.5 * math.sin(s.phase + 2 * math.pi * s.twinkleHz * s.age)
            )
            spots.append(
                SparkSpot(
                    s.x,
                    s.y,
                    math.atan2(s.vx, s.vy),
                    s.length_ * fade,
                    fade * twinkle,
                )
            )
        return spots
