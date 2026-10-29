"""Particles flowing up along a beam (P03-R02), ported from `shots/laser-particles.ts`.

Each particle runs from the start of the beam to its end, then starts again from the start, so the
flow follows the beam as it gets shorter or longer.
"""

from org.transcrypt.stubs.browser import __pragma__

__pragma__("skip")
from typing import Any  # noqa: E402

from core.math.rng import Random  # noqa: E402

__pragma__("noskip")

from core.math.rng import random_in  # noqa: E402


class Particle:
    """One particle along the beam (internal to `LaserParticles`)."""

    def __init__(self, distance: float, speed: float, radius: float, lateral: float) -> None:
        # Distance travelled from the start of the beam.
        self.distance = distance
        self.speed = speed
        self.radius = radius
        # Sideways position in [-1, 1].
        self.lateral = lateral


class ParticleSpot:
    """A particle to draw, in logical pixels."""

    def __init__(self, x: float, y: float, radius: float) -> None:
        self.x = x
        self.y = y
        self.radius = radius


class LaserParticles:
    """Particles flowing up along a beam (P03-R02)."""

    def __init__(self, options: Any, random: Random, initial_length: float) -> None:
        self._options = options
        self._particles: list[Particle] = [
            Particle(
                random() * initial_length,
                random_in(random, options.speed[0], options.speed[1]),
                random_in(random, options.radius[0], options.radius[1]),
                random_in(random, -1, 1),
            )
            for _ in range(options.count)
        ]

    def step(self, segments: list[Any], dt: float) -> list[ParticleSpot]:
        """Moves the particles along `segments` (bottom first) and returns where to draw them."""
        if len(segments) == 0:
            return []
        first = segments[0]
        last = segments[len(segments) - 1]
        length = last.y1 - first.y0
        if not length > 0:
            return []
        spots: list[ParticleSpot] = []
        for p in self._particles:
            p.distance = (p.distance + p.speed * dt) % length
            y = first.y0 + p.distance
            segment = last
            for s in segments:
                if y <= s.y1:
                    segment = s
                    break
            x = segment.x + (p.lateral * segment.width * self._options.spread) / 2
            spots.append(ParticleSpot(x, y, p.radius))
        return spots
