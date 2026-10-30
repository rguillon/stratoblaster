"""Targets for the shots viewer (P03-R10), ported from `app/dummy-targets.ts`: they sway left and
right together around their anchors and come back with full health some time after being
destroyed. When disabled, they are all dead and stay dead.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


class DummyTargetOptions:
    """Settings of the dummy targets: their anchors (objects with `x` and `y`), sway and respawn."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        radius: float,
        max_health: float,
        anchors: list[Any],
        sway_amplitude: float,
        sway_hz: float,
        respawn_seconds: float,
    ) -> None:
        self.radius = radius
        self.max_health = max_health
        self.anchors = anchors
        self.sway_amplitude = sway_amplitude
        self.sway_hz = sway_hz
        self.respawn_seconds = respawn_seconds


class DummyTarget:
    """A target shots can hit: a circle with health (it has the fields of `ShotTarget`)."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self, id: int, x: float, y: float, radius: float, max_health: float
    ) -> None:
        self.id = id
        self.x = x
        self.y = y
        self.radius = radius
        self.health = max_health
        self.max_health = max_health


class DummyTargets:
    """Targets for the shots viewer (P03-R10)."""

    def __init__(self, options: DummyTargetOptions) -> None:
        self._options = options
        self.targets: list[DummyTarget] = [
            DummyTarget(index, anchor.x, anchor.y, options.radius, options.max_health)
            for index, anchor in enumerate(options.anchors)
        ]
        # Destroyed targets since creation.
        self.kills = 0
        self._time = 0.0
        self._enabled = True
        # Seconds each target has been destroyed for, 0 while alive.
        self._dead_for: list[float] = [0.0 for _ in self.targets]

    @property
    def enabled(self) -> bool:
        return self._enabled

    def set_enabled(self, enabled: bool) -> None:
        """Shows (full health) or removes all targets."""
        self._enabled = enabled
        for target in self.targets:
            target.health = target.max_health if enabled else 0
        self._dead_for = [0.0 for _ in self.targets]

    def update(self, dt: float) -> None:
        """Moves the targets, counts the newly destroyed ones and brings back the old ones."""
        self._time += dt
        options = self._options
        sway = options.sway_amplitude * math.sin(2 * math.pi * options.sway_hz * self._time)
        for i, target in enumerate(self.targets):
            anchor = options.anchors[i] if i < len(options.anchors) else None
            target.x = (anchor.x if anchor is not None else target.x) + sway
            if not self._enabled or target.health > 0:
                continue
            dead_for = self._dead_for[i]
            if dead_for == 0:
                self.kills += 1
            self._dead_for[i] = dead_for + dt
            if dead_for + dt >= options.respawn_seconds:
                target.health = target.max_health
                self._dead_for[i] = 0.0
