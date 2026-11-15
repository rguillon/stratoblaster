# Copyright (c) 2026 Renaud Guillon
"""Exhaust flame of a reactor (GFX-SHIP-06, ENM-40): the blue light behind each reactor.

It is a living flame: an outer exhaust cone and a hotter inner cone that flicker in length, width
and brightness, and plasma puffs that flow from the nozzle down the exhaust. A flame has no mesh
of its own: the scene's flame layer draws them all together (`flame_layer.py`, D-428).
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.record import field
from game.config.ship_look import REACTOR_FLAME as FLAME
from game.config.ship_look import SHIP_LOOK
from game.view.flame_layer import PUFF_STRETCH, flame_layer
from render.model_animation import add_model_animation

# isort: split
# __pragma__ ("skip")
from typing import Any

Scene = Any
# __pragma__ ("noskip")

__pragma__("jsmod")


TAU = math.pi * 2
# Puffs fade in over this first fraction of their travel, then fade out.
PUFF_FADE_IN = 0.15
# `CreatePolyhedron` types.
TETRAHEDRON = 0
ICOSAHEDRON = 3
# Size of a puff at the end of its travel, relative to its size at the nozzle.
PUFF_END_SCALE = 0.3


def _imul(a: int, b: int) -> int:
    """`Math.imul(a, b)`: 32-bit integer multiplication."""
    __pragma__("js", "{}", "return Math.imul(a, b);")
    return 0


def _char_code(text: str, index: int) -> int:
    """`text.charCodeAt(index)`."""
    __pragma__("js", "{}", "return text.charCodeAt(index);")
    return 0


def flicker(time_sec: float, phase: float, hz: list[float]) -> float:
    """Irregular flicker in [-1, 1]: the mean of sines at the given frequencies, phase-shifted.

    See GFX-ART-11.
    """
    count = len(hz)
    if count == 0:
        return 0
    total = 0.0
    # A plain loop: this runs for every flame, every frame (ENG-157).
    for i in range(count):
        total += math.sin(TAU * hz[i] * time_sec + phase * (i + 1))
    return total / count


def reactor_phase(text: str) -> float:
    """Stable phase in [0, 2π) derived from a name, so that reactors do not flicker in sync."""
    hash_value = 2166136261  # FNV-1a
    for i in range(len(text)):
        hash_value = _imul(hash_value ^ _char_code(text, i), 16777619)
        if hash_value < 0:
            hash_value += 4294967296  # `>>> 0`: unsigned
    return (hash_value / 4294967296) * TAU


def puff_progress(time_sec: float, index: int, count: int, speed: float) -> float:
    """How far puff `index` (of `count`) has travelled down the exhaust, in [0, 1)."""
    p = (time_sec * speed + index / count) % 1
    return p + 1 if p < 0 else p


def puff_opacity(progress: float) -> float:
    """Opacity of a puff at `progress`: fades in near the nozzle, then out towards the tip."""
    return min(1, progress / PUFF_FADE_IN) * (1 - progress)


def _around(value: float, amount: float) -> float:
    """Map a flicker value in [-1, 1] to a factor in [1 - amount, 1 + amount]."""
    return 1 + amount * value


def _dimmed(value: float, amount: float) -> float:
    """Map a flicker value in [-1, 1] to a visibility in [1 - amount, 1]."""
    return 1 - (amount * (1 - value)) / 2


class FlameColors:
    """The colours of a flame: its exhaust cone, its inner flame and its puffs.

    Each is `[r, g, b, alpha]`.
    """

    def __init__(self, exhaust: list[float], flame: list[float], plasma: list[float]) -> None:
        self.exhaust = exhaust
        self.flame = flame
        self.plasma = plasma


def _tint(look: Any) -> list[float]:
    emissive = look.emissive
    return [emissive[0], emissive[1], emissive[2], look.alpha]


def player_flame_colors() -> FlameColors:
    """Return the player ships' blue flame (GFX-ART-04)."""
    return FlameColors(
        _tint(SHIP_LOOK.reactorExhaust),
        _tint(SHIP_LOOK.reactorFlame),
        _tint(SHIP_LOOK.reactorPlasma),
    )


class Flame:
    """One reactor's flame: where it hangs (`node`), its sizes and colours, and its own time.

    `write(world)` adds its cones and puffs, as they are at its time, to the layer's batches;
    `world` holds the 16 numbers of its node's matrix.
    """

    def __init__(
        self, node: Any, size: dict[str, Any], colors: FlameColors, phase: float, layer: Any
    ) -> None:
        light = field(size, "light", None)
        self.node = node
        self.time = 0.0
        self._phase = phase
        self._colors = colors
        self._nozzle_z = size["nozzleZ"]
        self._length = size["length"]
        self._diameter = size["diameter"]
        self._puff_radius = size["puffDiameter"] / 2
        self._puff_count = light["puffs"] if light else FLAME.puffCount
        self._cones = layer.cones(size["sides"])
        # An icosahedron (20 triangles): small, translucent and moving, it reads as a blob. Light
        # flames (enemies) use a tetrahedron (4 triangles).
        self._puffs = layer.puffs(TETRAHEDRON if light else ICOSAHEDRON)
        # Reused for every instance written: nothing is allocated per frame.
        self._scale = [1.0, 1.0, 1.0]

    def write(self, world: Any) -> None:
        """Add the flame's cones and puffs to their batches, placed by `world`."""
        time = self.time
        phase = self._phase
        hz = FLAME.flickerHz
        outer_length = flicker(time, phase, hz)
        inner_length = flicker(time, phase + 1 * 1.7, hz)
        width = flicker(time, phase + 2 * 1.7, hz)
        brightness = flicker(time, phase + 3 * 1.7, hz)
        colors = self._colors
        scale = self._scale
        length = self._length
        w = _around(width, FLAME.widthFlicker) * self._diameter
        scale[0] = w
        scale[1] = w
        scale[2] = _around(outer_length, FLAME.lengthFlicker) * length
        exhaust = colors.exhaust
        dim = _dimmed(brightness, FLAME.brightnessFlicker)
        self._cones.add(world, scale, self._nozzle_z, exhaust, exhaust[3] * dim)
        scale[0] = w * FLAME.coreWidth
        scale[1] = w * FLAME.coreWidth
        scale[2] = _around(inner_length, FLAME.lengthFlicker) * length * FLAME.coreLength
        flame = colors.flame
        dim = _dimmed(-brightness, FLAME.brightnessFlicker)
        self._cones.add(world, scale, self._nozzle_z, flame, flame[3] * dim)
        plasma = colors.plasma
        count = self._puff_count
        for i in range(count):
            p = puff_progress(time, i, count, FLAME.puffSpeed)
            s = (1 - (1 - PUFF_END_SCALE) * p) * self._puff_radius
            scale[0] = s
            scale[1] = s
            scale[2] = s * PUFF_STRETCH
            # Nudged off the nozzle plane so the puff always sits behind it.
            along = self._nozzle_z - 0.01 - p * length
            self._puffs.add(world, scale, along, plasma, plasma[3] * puff_opacity(p))


def build_reactor_flame(
    name: str,
    size: dict[str, Any],
    parent: Any,
    colors: FlameColors | None = None,
) -> Flame:
    """Add an animated reactor flame (GFX-SHIP-06) at `parent`, named after `name`.

    It is blue like the player ships' unless other `colors` are given (enemies, ENM-40).

    `size` holds `nozzleZ`, `length`, `diameter` (exhaust cone at the nozzle), `puffDiameter`,
    `sides`, and optionally `light` (`{ "puffs": n }`): lighter flames (enemies) have that many
    puffs, tetrahedra instead of icosahedra. The flame points to `parent`'s -Z, and shows
    whenever `parent` does.
    """
    if colors is None:
        colors = player_flame_colors()
    layer = flame_layer(parent.getScene())
    flame = Flame(parent, size, colors, reactor_phase(name), layer)
    layer.add(flame)

    def on_frame(dt_seconds: float) -> None:
        flame.time = flame.time + dt_seconds

    add_model_animation(parent, on_frame)
    return flame
