# Copyright (c) 2026 Renaud Guillon
"""The smoke trail of the enemies' missiles (GFX-SHOT-15).

Small puffs left behind each missile's tail as it flies, at its height (a missile climbing out of an
upward silo leaves its trail in the air, WPN-09): each grows and fades out. The game's own seeded
particles, drawn as thin instances like the explosions' smoke (ENG-103), not Babylon particle
systems.
"""

import math

from core.math.rng import create_rng, random_in
from game.config.enemy_look import ENEMY_LOOK

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from typing import Any

# __pragma__ ("noskip")


LOOK = ENEMY_LOOK.missile


class SmokePuff:
    """A puff of a missile's trail: where it is (`z` towards the camera is negative), its age."""

    def __init__(self, x: float, y: float, z: float, life: float, drift: list[float]) -> None:
        self.x = x
        self.y = y
        self.z = z
        self.age = 0.0
        self.life = life
        self.drift = drift


class TrailSpot:
    """A puff to draw: its centre (with its own depth `z`), radius and grey, and its opacity."""

    def __init__(self, puff: SmokePuff, radius: float, grey: float, a: float) -> None:
        self.x = puff.x
        self.y = puff.y
        self.z = puff.z
        self.radius = radius
        self.r = grey
        self.g = grey
        self.b = grey
        self.a = a


def tail_of(m: Any) -> list[float]:
    """Return where a missile's tail is, in playfield space (`z` towards the camera negative)."""
    size = m.radius / LOOK.baseRadius
    back = LOOK.length / 2 * size
    pitch = m.pitch if hasattr(m, "pitch") else 0
    flat = math.cos(pitch)
    return [
        m.x - math.sin(m.heading) * flat * back,
        m.y - math.cos(m.heading) * flat * back,
        -0.5 - m.height + math.sin(pitch) * back,
    ]


class MissileSmoke:
    """The puffs of every missile's trail: emitted, aged, and handed out as spots to draw."""

    def __init__(self) -> None:
        self.puffs: list[SmokePuff] = []
        self._random = create_rng(LOOK.smoke.seed)
        self._since = 0.0

    def step(self, missiles: list[Any], dt: float) -> list[TrailSpot]:
        """Age the puffs by `dt`, leave new ones behind `missiles`, and return what to draw."""
        smoke = LOOK.smoke
        kept: list[SmokePuff] = []
        for puff in self.puffs:
            puff.age += dt
            if puff.age < puff.life:
                puff.x += puff.drift[0] * dt
                puff.y += puff.drift[1] * dt
                kept.append(puff)
        self.puffs = kept
        self._since += dt
        while self._since >= smoke.every:
            self._since -= smoke.every
            for m in missiles:
                self._emit(m)
        return [self._spot(puff) for puff in self.puffs]

    def _emit(self, m: Any) -> None:
        smoke = LOOK.smoke
        if len(self.puffs) >= smoke.most:
            return
        tail = tail_of(m)
        life = random_in(self._random, smoke.life[0], smoke.life[1])
        a = random_in(self._random, 0, math.pi * 2)
        speed = random_in(self._random, 0, smoke.drift)
        drift = [math.cos(a) * speed, math.sin(a) * speed]
        self.puffs.append(SmokePuff(tail[0], tail[1], tail[2], life, drift))

    def _spot(self, puff: SmokePuff) -> TrailSpot:
        smoke = LOOK.smoke
        t = puff.age / puff.life
        radius = smoke.size[0] + (smoke.size[1] - smoke.size[0]) * math.sqrt(t)
        alpha = smoke.alpha * min(1, t / 0.15) * (1 - t)
        return TrailSpot(puff, radius, smoke.grey, alpha)
