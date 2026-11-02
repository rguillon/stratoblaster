# Copyright (c) 2026 Renaud Guillon
"""Pieces of a `SceneryStage` that need nothing else of it (phase 4): the lowest ground.

The order of the opaque meshes, the stage camera, the sea plane and the terrain-chunk watchers.
"""

from render.babylon import (
    create_ground,
    new_free_camera,
    new_viewport,
    render_painter_sort_compare,
    vector3_zero,
)
from render.scenery.rain_rings import RainRings

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
# __pragma__ ("skip")
from collections.abc import Callable, Sequence
from typing import Any

from core.scenery.scenery_level import SceneryLevel

# __pragma__ ("noskip")


def _min_of(values: Sequence[float]) -> float:
    """`Math.min(...values)`: Infinity for no value."""
    low = float("Infinity")
    for v in values:
        low = min(low, v)
    return low


def lowest_ground(level: SceneryLevel) -> float:
    """Lowest ground of a level: its sea, or the lowest relief (GFX-CAM-05, GFX-WATER-02)."""
    lows = [s.relief.base - s.relief.amplitude for s in level.sections]
    if level.sea is not None:
        return level.sea.level
    return _min_of(lows)


def terrain_last(terrain: Any) -> Callable[[Any, Any], float]:
    """Return the order of the opaque meshes (reviewer, 2026-10-28, PERF-28): the terrain last.

    So its costly shading is skipped where the props and cars in front of it were drawn first; the
    others by material, as Babylon does.
    """

    def last(s: Any) -> float:
        return 1 if s.getMaterial() is terrain else 0

    def compare(a: Any, b: Any) -> float:
        difference = last(a) - last(b)
        if difference != 0:
            return difference
        return render_painter_sort_compare(a, b)

    return compare


def stage_camera(
    scene: Any,
    half_fov: float,
    clips: tuple[float, float],
    viewport: tuple[float, float, float, float] | None = None,
) -> Any:
    """Return the camera (GFX-CAM-02), made the active one.

    It sees `half_fov` up and down, from `clips[0]` to `clips[1]` (D-216, GFX-CAM-06: the near plane
    far out, so the depth buffer keeps its precision at the ground). With a `viewport` (x, y,
    width, height as shares of the canvas, D-252) it draws only there, the rest of the canvas
    left to the clear colour; its aspect ratio follows the viewport.
    """
    near_clip, far_clip = clips
    camera = new_free_camera("scenery-camera", vector3_zero(), scene)
    camera.fov = half_fov * 2
    camera.minZ = near_clip
    camera.maxZ = far_clip
    if viewport is not None:
        camera.viewport = new_viewport(viewport[0], viewport[1], viewport[2], viewport[3])
    scene.activeCamera = camera
    return camera


class SeaParts:
    """The sea plane and the rain rings on it (GFX-WEATHER-09)."""

    def __init__(self, sea: Any, rings: RainRings) -> None:
        self.sea = sea
        self.rings = rings


def sea_parts(scene: Any, level: SceneryLevel, size: Sequence[float], kit: Any) -> SeaParts | None:
    """Return the sea plane of `level` (GFX-WATER-01; phase 10: or lava, GFX-TERRAIN-16).

    The rain rings on it (GFX-WEATHER-09), `width` x `length` (`size`), if it has a sea.
    """
    if level.sea is None:
        return None
    width = size[0]
    length = size[1]
    height = level.sea.level
    return SeaParts(
        sea_plane(scene, [width, length, height], kit.sea),
        RainRings(scene, kit.rings, (height, width, length)),
    )


def sea_plane(scene: Any, size: Sequence[float], material: Any) -> Any:
    """Return the sea plane (GFX-WATER-03; phase 10: or lava).

    It is `width` x `length` (`size[0]`, `size[1]`), at `size[2]`, the level.
    """
    sea = create_ground("sea", size[0], size[1], 1, scene)
    sea.position.y = size[2]
    sea.material = material
    sea.isPickable = False
    sea.receiveShadows = True
    sea.alphaIndex = 0
    return sea


class TerrainWatch:
    """The terrain chunk meshes made so far, and who wants.

    Know about each new one (phase 10: a glow layer hiding the lava under the hills).
    """

    def __init__(self) -> None:
        self._meshes: list[Any] = []
        self._watchers: list[Callable[[Any], None]] = []

    def add(self, mesh: Any) -> None:
        """Add a new terrain chunk mesh."""
        self._meshes.append(mesh)
        for watch in self._watchers:
            watch(mesh)

    def watch(self, watch: Callable[[Any], None]) -> None:
        """Call `watch` with every mesh, now and as new ones are made."""
        for mesh in self._meshes:
            watch(mesh)
        self._watchers.append(watch)
