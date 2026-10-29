"""Exhaust flame of a reactor, ported from `reactor-flame.ts` (GD-61): the blue light behind each
reactor is a living flame: an outer exhaust cone and a hotter inner cone that flicker in length,
width and brightness, and plasma puffs that flow from the nozzle down the exhaust.
"""

import math

from org.transcrypt.stubs.browser import __pragma__

from game.config.ship_look import REACTOR_FLAME as FLAME
from game.view.ship_materials import get_ship_materials

# create_cylinder and create_polyhedron: render/babylon.py.
from render.babylon import (
    babylon_class,
    create_cylinder,
    create_polyhedron,
    new_transform_node,
)
from render.model_animation import add_model_animation

__pragma__("jsmod")

__pragma__("skip")
from typing import Any  # noqa: E402

Scene = Any  # noqa: E402


__pragma__("noskip")

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


def _cylinder_options(height: float, diameter_bottom: float, tessellation: int) -> Any:
    """Options for `CreateCylinder`: a cone pointing up, with its tip at the top."""
    options: Any = None
    __pragma__(
        "js",
        "{}",
        "options = {height: height, diameterTop: 0, diameterBottom: diameter_bottom, "
        "tessellation: tessellation};",
    )
    return options


def _polyhedron_options(kind: int, size: float) -> Any:
    """Options for `CreatePolyhedron`: `{ type, size }`."""
    options: Any = None
    __pragma__("js", "{}", "options = {type: kind, size: size};")
    return options


def flicker(time_sec: float, phase: float, hz: list[float]) -> float:
    """Irregular flicker in [-1, 1]: the mean of sines at the given frequencies, phase-shifted."""
    total = 0.0
    for i, f in enumerate(hz):
        total += math.sin(TAU * f * time_sec + phase * (i + 1))
    return total / len(hz) if len(hz) > 0 else 0


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
    """Maps a flicker value in [-1, 1] to a factor in [1 - amount, 1 + amount]."""
    return 1 + amount * value


def _dimmed(value: float, amount: float) -> float:
    """Maps a flicker value in [-1, 1] to a visibility in [1 - amount, 1]."""
    return 1 - (amount * (1 - value)) / 2


class Cone:
    """A cone of the flame: `pivot` is at the nozzle (scaling it stretches the cone from there),
    `mesh` the cone itself."""

    def __init__(self, pivot: Any, mesh: Any) -> None:
        self.pivot = pivot
        self.mesh = mesh


def _cone(name: str, size: dict[str, Any], material: Any, parent: Any) -> Cone:
    """A cone of the flame, from the nozzle towards -Z."""
    scene = parent.getScene()
    pivot = new_transform_node(name + "-pivot", scene)
    pivot.parent = parent
    options = _cylinder_options(size["length"], size["diameter"], size["sides"])
    if not size["caps"]:
        options.cap = babylon_class("Mesh").NO_CAP
    mesh = create_cylinder(name, options, scene)
    # The cylinder grows along +Y; -90° around X points its tip towards -Z.
    mesh.rotation.x = -math.pi / 2
    mesh.position.z = -size["length"] / 2
    mesh.material = material
    mesh.isPickable = False
    mesh.parent = pivot
    return Cone(pivot, mesh)


def _build_puffs(
    name: str,
    diameter: float,
    material: Any,
    parent: Any,
    light: Any,
) -> list[Any]:
    """Plasma puffs of a flame; the animation places them along the exhaust."""
    scene = parent.getScene()
    count = light["puffs"] if light else FLAME.puffCount
    puffs: list[Any] = []
    for i in range(count):
        # An icosahedron (20 triangles): small, translucent and moving, it reads as a blob. Light
        # flames use a tetrahedron (4 triangles).
        puff = create_polyhedron(
            name + "-puff-" + str(i),
            _polyhedron_options(TETRAHEDRON if light else ICOSAHEDRON, diameter / 2),
            scene,
        )
        puff.material = material
        puff.isPickable = False
        puff.parent = parent
        puffs.append(puff)
    return puffs


def _player_flame(parent: Any) -> dict[str, Any]:
    """The player ships' blue flame materials (GD-61)."""
    mats = get_ship_materials(parent.getScene())
    return {
        "exhaust": mats.reactorExhaust,
        "flame": mats.reactorFlame,
        "plasma": mats.reactorPlasma,
    }


def build_reactor_flame(
    name: str,
    size: dict[str, Any],
    parent: Any,
    materials: dict[str, Any] | None = None,
) -> None:
    """Builds an animated reactor flame (GD-61) under `parent`, named after `name`, blue like the
    player ships' unless other `materials` are given (enemies, phase 5 review).

    `size` holds `nozzleZ`, `length`, `diameter` (exhaust cone at the nozzle), `puffDiameter`,
    `sides`, and optionally `light` (`{ "puffs": n }`): lighter flames (enemies) have no caps on
    the cones, that many puffs, and tetrahedra instead of icosahedra."""
    if materials is None:
        materials = _player_flame(parent)
    sides = size["sides"]
    light = size.get("light")
    caps = not light
    outer = _cone(
        name + "-exhaust",
        {"length": size["length"], "diameter": size["diameter"], "sides": sides, "caps": caps},
        materials["exhaust"],
        parent,
    )
    inner = _cone(
        name + "-flame",
        {
            "length": size["length"] * FLAME.coreLength,
            "diameter": size["diameter"] * FLAME.coreWidth,
            "sides": sides,
            "caps": caps,
        },
        materials["flame"],
        parent,
    )
    for cone in [outer, inner]:
        cone.pivot.position.z = size["nozzleZ"]

    puffs = _build_puffs(name, size["puffDiameter"], materials["plasma"], parent, light)

    phase = reactor_phase(name)
    hz = FLAME.flickerHz
    # The time since the flame was built, in seconds.
    clock = [0.0]

    def apply() -> None:
        time = clock[0]
        outer_length = flicker(time, phase, hz)
        inner_length = flicker(time, phase + 1 * 1.7, hz)
        width = flicker(time, phase + 2 * 1.7, hz)
        brightness = flicker(time, phase + 3 * 1.7, hz)
        w = _around(width, FLAME.widthFlicker)
        outer.pivot.scaling.set(w, w, _around(outer_length, FLAME.lengthFlicker))
        inner.pivot.scaling.set(w, w, _around(inner_length, FLAME.lengthFlicker))
        outer.mesh.visibility = _dimmed(brightness, FLAME.brightnessFlicker)
        inner.mesh.visibility = _dimmed(-brightness, FLAME.brightnessFlicker)
        for i, puff in enumerate(puffs):
            p = puff_progress(time, i, len(puffs), FLAME.puffSpeed)
            # Nudged off the nozzle plane so the puff always sits behind it.
            puff.position.z = size["nozzleZ"] - 0.01 - p * size["length"]
            s = 1 - (1 - PUFF_END_SCALE) * p
            puff.scaling.set(s, s, s * 1.6)
            puff.visibility = puff_opacity(p)

    apply()

    def on_frame(dt_seconds: float) -> None:
        clock[0] = clock[0] + dt_seconds
        apply()

    add_model_animation(parent, on_frame)
