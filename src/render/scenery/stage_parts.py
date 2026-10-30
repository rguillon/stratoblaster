"""Pieces of a `SceneryStage` that need nothing else of it (P04), ported from
`render/scenery/stage-parts.ts`: the lowest ground, the order of the opaque meshes, the stage
camera, the sea plane and the terrain-chunk watchers.
"""

from org.transcrypt.stubs.browser import __pragma__

from render.babylon import (
    create_ground,
    new_free_camera,
    render_painter_sort_compare,
    vector3_zero,
)
from render.scenery.rain_rings import RainRings

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable, Sequence  # noqa: E402
from typing import Any  # noqa: E402

from core.scenery.scenery_level import SceneryLevel  # noqa: E402

__pragma__("noskip")


def _min_of(values: Sequence[float]) -> float:
    """`Math.min(...values)`: Infinity for no value."""
    low = float("Infinity")
    for v in values:
        low = min(low, v)
    return low


def lowest_ground(level: SceneryLevel) -> float:
    """Lowest ground of a level: its sea, or the lowest relief."""
    lows = [s.relief.base - s.relief.amplitude for s in level.sections]
    if level.sea is not None:
        return level.sea.level
    return _min_of(lows)


def terrain_last(terrain: Any) -> Callable[[Any, Any], float]:
    """The order of the opaque meshes (reviewer, 2026-10-28): the terrain last, so its costly
    shading is skipped where the props and cars in front of it were drawn first; the others by
    material, as Babylon does."""

    def last(s: Any) -> float:
        return 1 if s.getMaterial() is terrain else 0

    def compare(a: Any, b: Any) -> float:
        difference = last(a) - last(b)
        if difference != 0:
            return difference
        return render_painter_sort_compare(a, b)

    return compare


def stage_camera(scene: Any, half_fov: float, far_clip: float) -> Any:
    """The stage's camera, `half_fov` up and down, seeing up to `far_clip`; made the active one."""
    camera = new_free_camera("scenery-camera", vector3_zero(), scene)
    camera.fov = half_fov * 2
    camera.minZ = 1
    camera.maxZ = far_clip
    scene.activeCamera = camera
    return camera


class SeaParts:
    """The sea plane and the rain rings on it (P09-R05)."""

    def __init__(self, sea: Any, rings: RainRings) -> None:
        self.sea = sea
        self.rings = rings


def sea_parts(scene: Any, level: SceneryLevel, size: Sequence[float], kit: Any) -> SeaParts | None:
    """The sea plane of `level` (P04-R02; phase 10: or lava) and the rain rings on it (P09-R05),
    `width` x `length` (`size`), if it has a sea."""
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
    """The sea plane (P04-R02; phase 10: or lava), `width` x `length` (`size[0]`, `size[1]`), at
    `size[2]`, the level."""
    sea = create_ground("sea", size[0], size[1], 1, scene)
    sea.position.y = size[2]
    sea.material = material
    sea.isPickable = False
    sea.receiveShadows = True
    sea.alphaIndex = 0
    return sea


class TerrainWatch:
    """The terrain chunk meshes made so far, and who wants to know about each new one (phase 10: a
    glow layer hiding the lava under the hills)."""

    def __init__(self) -> None:
        self._meshes: list[Any] = []
        self._watchers: list[Callable[[Any], None]] = []

    def add(self, mesh: Any) -> None:
        """A new terrain chunk mesh."""
        self._meshes.append(mesh)
        for watch in self._watchers:
            watch(mesh)

    def watch(self, watch: Callable[[Any], None]) -> None:
        """Calls `watch` with every mesh, now and as new ones are made."""
        for mesh in self._meshes:
            watch(mesh)
        self._watchers.append(watch)
