"""The weather of a scenery stage (P08-R05): particles of its kind, falling through the air between
the ground and the flight altitude.
"""

from org.transcrypt.stubs.browser import __pragma__

from config.weather import WEATHER_KINDS
from core.math.rng import create_rng
from core.scenery.sky_look import weather_particles
from render.babylon import apply_vertex_data, babylon_class, new_mesh, set_enabled, vertex_data_of
from render.scenery.cloud_layers import BELOW_CLOUDS_GROUP
from render.scenery.scenery_kit import FogState

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Any, Protocol  # noqa: E402

__pragma__("noskip")

# Draw order among the see-through meshes above the ground: after both cloud layers.
WEATHER_ALPHA_INDEX = 4
# Indices of one particle's quad.
QUAD_INDICES = 6


class WeatherView:
    """Where the camera looks on one frame: what the particles need besides the weather."""

    def __init__(
        self, time: float, camera_position: Any, right: Any, up: Any, start: float
    ) -> None:
        """`right` and `up`: the camera's directions, to face the particles to it. `start`: Z where
        the box of air they fill starts (it follows the view, they stay put)."""
        self.time = time
        self.camera_position = camera_position
        self.right = right
        self.up = up
        self.start = start


class WeatherFrame:
    """What the particles of a weather show on one frame (P08-R05)."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        time: float,
        strength: float,
        camera_position: Any,
        right: Any,
        up: Any,
        start: float,
        fog: FogState,
    ) -> None:
        """`strength` (0..1) sets the wind and how much the particles streak."""
        self.time = time
        self.strength = strength
        self.camera_position = camera_position
        self.right = right
        self.up = up
        self.start = start
        self.fog = fog


__pragma__("skip")


class WeatherMaterial(Protocol):
    """The material of a weather's particles, driven frame by frame."""

    material: Any

    def set(self, frame: WeatherFrame) -> None: ...


WeatherMaterialFactory = Callable[[Any, Any], WeatherMaterial]
__pragma__("noskip")


def _draw_first(mesh: Any, count: int) -> None:
    """Draws only the first `count` particles of `mesh` (one sub-mesh over their quads)."""
    sub = mesh.subMeshes[0]
    if sub and sub.indexCount == count * QUAD_INDICES:
        return
    mesh.releaseSubMeshes()
    babylon_class("SubMesh").AddToMesh(0, 0, mesh.getTotalVertices(), 0, count * QUAD_INDICES, mesh)


def _build_particles(scene: Any, kind_id: str, kind: Any, material: Any) -> Any:
    """The particles of a weather kind (P08-R05): one mesh of `max_particles` small quads, each
    with its own random place in the box of air, depth, size and fall speed (the `flake`
    attribute); the material moves them on the GPU, so nothing is uploaded per frame. Only the
    first `weather_particles` of them are drawn."""
    count = kind.max_particles
    random = create_rng(len(kind_id) * 7919 + count)
    positions: list[float] = []
    flakes: list[float] = []
    indices: list[int] = []
    corners = [[-0.5, -0.5], [0.5, -0.5], [0.5, 0.5], [-0.5, 0.5]]
    for i in range(count):
        flake = [random(), random(), random(), random()]
        for corner in corners:
            positions.append(corner[0])
            positions.append(corner[1])
            positions.append(0)
            for value in flake:
                flakes.append(value)
        v = i * 4
        indices.extend([v, v + 1, v + 2, v, v + 2, v + 3])
    mesh = new_mesh("weather-" + kind_id, scene)
    apply_vertex_data(vertex_data_of(positions, indices), mesh)
    mesh.setVerticesData("flake", flakes, False, 4)
    mesh.material = material
    mesh.isPickable = False
    # The quads are placed by the material: the mesh's own bounds mean nothing.
    mesh.alwaysSelectAsActiveMesh = True
    mesh.renderingGroupId = BELOW_CLOUDS_GROUP + 1
    mesh.alphaIndex = WEATHER_ALPHA_INDEX
    set_enabled(mesh, False)
    return mesh


class _ParticleLayer:
    """A weather kind's mesh and its material."""

    def __init__(self, mesh: Any, material: Any) -> None:
        self.mesh = mesh
        self.material = material


class WeatherLayer:
    """The weather of a level (P08-R05): the particles of its kind (phase 10: of both its kinds),
    as many as its strength asks, falling through the air between the ground and the flight
    altitude, behind everything on the playfield. It is only a look: nothing in the simulation
    reads it."""

    def __init__(
        self, scene: Any, materials: WeatherMaterialFactory, kinds: Any = WEATHER_KINDS
    ) -> None:
        self._scene = scene
        self._factory = materials
        self._kinds = kinds
        self._layers: dict[str, _ParticleLayer] = {}
        self._drawn = 0

    @property
    def drawn(self) -> int:
        """Particles drawn on the last frame."""
        return self._drawn

    def update(self, atmosphere: Any, view: WeatherView) -> None:
        """Shows the weather of `atmosphere` for this frame (phase 10: its second weather too)."""
        weathers = []
        for weather in [atmosphere.weather, atmosphere.second_weather]:
            if weather and weather_particles(weather) > 0 and self._kinds.get(weather.kind):
                weathers.append(weather)
        for layer_id, layer in self._layers.items():
            shown = False
            for weather in weathers:
                if weather.kind == layer_id:
                    shown = True
            set_enabled(layer.mesh, shown)
        self._drawn = 0
        for weather in weathers:
            kind = self._kinds.get(weather.kind)
            if not kind:
                continue
            count = weather_particles(weather)
            layer = self._layer(weather.kind, kind)
            _draw_first(layer.mesh, count)
            fog = FogState(atmosphere.sky.haze, atmosphere.fog.start, atmosphere.fog.end)
            layer.material.set(
                WeatherFrame(
                    view.time,
                    weather.strength,
                    view.camera_position,
                    view.right,
                    view.up,
                    view.start,
                    fog,
                )
            )
            self._drawn += count

    def _layer(self, kind_id: str, kind: Any) -> _ParticleLayer:
        layer = self._layers.get(kind_id)
        if not layer:
            material = self._factory(self._scene, kind)
            layer = _ParticleLayer(
                _build_particles(self._scene, kind_id, kind, material.material), material
            )
            self._layers[kind_id] = layer
        set_enabled(layer.mesh, True)
        return layer
