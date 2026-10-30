"""Rain rings on the water (P09-R05): faint rings spreading where raindrops land, drawn on a plane
at the water level. Ported from `render/scenery/rain-rings.ts`.
"""

from org.transcrypt.stubs.browser import __pragma__

from config.weather import WEATHER_KINDS
from render.babylon import create_ground_sized, set_enabled
from render.scenery.scenery_kit import FogState

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Any, Protocol  # noqa: E402

__pragma__("noskip")

# Draw order among the see-through meshes: right after the water.
RINGS_ALPHA_INDEX = 1
# The rings lie this far above the water, so they never flicker against it.
LIFT = 0.05


class RingsFrame:
    """What the rain rings show on one frame (P09-R05)."""

    def __init__(self, time: float, strength: float, fog: FogState) -> None:
        """`strength` (0..1): how many rings there are and how strong they show."""
        self.time = time
        self.strength = strength
        self.fog = fog


__pragma__("skip")


class RingsMaterial(Protocol):
    """The material of the rings of a weather kind, driven frame by frame."""

    material: Any

    def set(self, frame: RingsFrame) -> None: ...


RingsMaterialFactory = Callable[[Any, Any], RingsMaterial]
__pragma__("noskip")


class RainRings:
    """Faint rings spreading on the water where raindrops land (P09-R05): a plane at the water
    level that follows the view, the rings drawn by its material in cells of the ground. The
    terrain above the water hides it, so the rings only show on the sea, the rivers, the swamps
    and the lakes. It shows the rings of the weather kind of the atmosphere, if it has any."""

    def __init__(
        self,
        scene: Any,
        materials: RingsMaterialFactory,
        placement: tuple[float, float, float],
        kinds: Any = WEATHER_KINDS,
    ) -> None:
        """`placement` is `(level, width, length)`."""
        level, width, length = placement
        self._scene = scene
        self._factory = materials
        self._kinds = kinds
        self._materials: dict[str, Any] = {}
        self._shown = 0
        self._plane = create_ground_sized("rain-rings", width, length, scene)
        self._plane.position.y = level + LIFT
        self._plane.isPickable = False
        self._plane.alphaIndex = RINGS_ALPHA_INDEX
        set_enabled(self._plane, False)

    @property
    def shown(self) -> float:
        """Strength of the rings drawn on the last frame (0 when none)."""
        return self._shown

    def update(self, atmosphere: Any, frame: tuple[float, float, bool]) -> None:
        """Shows the rings of `atmosphere`'s weather. `frame` is `(time, z, water)`: the plane is
        centred at `z`; none while the water is hidden (`water` false)."""
        time, z, water = frame
        weather = atmosphere.weather
        kind = self._kinds.get(weather.kind)
        rings = kind.rings if kind else None
        strength = min(1, max(0, weather.strength))
        self._shown = strength if (rings and water and strength > 0) else 0
        set_enabled(self._plane, self._shown > 0)
        if not rings or self._shown == 0:
            return
        material = self._material(weather.kind, rings)
        self._plane.material = material.material
        self._plane.position.z = z
        fog = FogState(atmosphere.sky.haze, atmosphere.fog.start, atmosphere.fog.end)
        material.set(RingsFrame(time, strength, fog))

    def _material(self, kind_id: str, rings: Any) -> RingsMaterial:
        material = self._materials.get(kind_id)
        if not material:
            material = self._factory(self._scene, rings)
            self._materials[kind_id] = material
        return material
