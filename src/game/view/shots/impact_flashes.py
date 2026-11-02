# Copyright (c) 2026 Renaud Guillon
"""Short glowing discs where shots hit (GFX-FX-03)."""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.view.shot_geometry import build_glow_disc
from game.view.shots.shot_meshes import additive_template
from render.node_pool import NodePool

# isort: split
# __pragma__ ("skip")
from typing import Any

from core.systems.shot_world import ShotImpact

# __pragma__ ("noskip")


class Flash:
    """A flash in progress."""

    def __init__(self, x: float, y: float, radius: float, age: float) -> None:
        self.x = x
        self.y = y
        self.radius = radius
        self.age = age


def flash_look(colors: list[list[float]], segments: int) -> Any:
    """Return a `{ colors, segments }` look as the flashes take it (a JavaScript object)."""
    __pragma__("js", "{}", "return {colors: colors, segments: segments};")
    return None


def flash_scale(age: float, duration: float) -> float:
    """Size of a flash at `age` over `duration`, relative to its radius: grows, then shrinks."""
    t = age / duration
    if t <= 0 or t >= 1:
        return 0
    return math.sin(math.pi * math.sqrt(t))


class ImpactFlashes:
    """Short glowing discs where shots hit (GFX-FX-03), kept in a pool."""

    def __init__(
        self,
        scene: Any,
        name: str,
        look: Any,
        duration: float,
        radius_of: Any,
    ) -> None:
        self.flashes: list[Flash] = []
        self.duration = duration
        self.radius_of = radius_of
        template = additive_template(name, build_glow_disc(look.segments, look.colors), scene)
        self._pool: NodePool = NodePool(lambda i: template.clone(name + "-" + str(i)))

    def sync(self, impacts: list[ShotImpact], dt: float) -> None:
        """Start a flash per impact, age the others by `dt`, and draw them."""
        for flash in self.flashes:
            flash.age += dt
        i = len(self.flashes) - 1
        while i >= 0:
            if self.flashes[i].age >= self.duration:
                self.flashes.pop(i)
            i -= 1
        for impact in impacts:
            self.flashes.append(Flash(impact.x, impact.y, self.radius_of(impact), 0))
        for i, mesh in enumerate(self._pool.show(len(self.flashes))):
            flash = self.flashes[i]
            # A new flash shows at a small size on its first frame.
            size = flash.radius * max(0.3, flash_scale(flash.age, self.duration))
            mesh.position.set(flash.x, flash.y, -1)
            mesh.scaling.set(size, size, 1)

    def dispose(self) -> None:
        """Disposes the pool of flashes."""
        self._pool.dispose()
