"""Materials, textures and shadows of a scenery scene (P04, P08, P09, P10): the kit's interfaces,
and the plain stand-in kit that needs no WebGL.

The interfaces are classes here. The materials are plain Python objects with a `material` attribute
and a `set`
method, so the kit's callers use them.
"""

from org.transcrypt.stubs.browser import __pragma__

from render.babylon import color3, color3_black, is_instance_of, new_standard_material

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
__pragma__("skip")
from collections.abc import Callable  # noqa: E402
from typing import Any, Protocol  # noqa: E402

Rgb = tuple[float, float, float]
__pragma__("noskip")


class FogState:
    """A fog of a frame: its colour and the distances it starts and ends at."""

    def __init__(self, color: Rgb, start: float, end: float) -> None:
        self.color = color
        self.start = start
        self.end = end


class CloudState:
    """What a cloud layer shows on one frame."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        coverage: float,
        opacity: float,
        color: Rgb,
        shade: Rgb,
        fog: FogState,
        offset_x: float,
        offset_z: float,
    ) -> None:
        """`color` follows the time of day (P08-R04) and `fog` is the haze it fades into. The
        offsets are the drift of the pattern, in world units along X and Z."""
        self.coverage = coverage
        self.opacity = opacity
        self.color = color
        self.shade = shade
        self.fog = fog
        self.offset_x = offset_x
        self.offset_z = offset_z


class GroundTransform:
    """How the ground is drawn (`PlayfieldCameraLook.groundScale`): a world point is `scale`
    times its ground point, moved `offset_z` along Z."""

    def __init__(self, scale: float, offset_z: float) -> None:
        self.scale = scale
        self.offset_z = offset_z


class SceneryKitFrame:
    """What the materials need to know on each frame."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        time: float,
        camera_position: Any,
        sea_enabled: bool,
        atmosphere: Any,
        ground: GroundTransform | None = None,
    ) -> None:
        """`time`: seconds since the scene started (animations, not the level time).
        `atmosphere`: the level's look here (P08-R04): shadows' darkness, ground lights. `ground`:
        see {@link GroundTransform}; None when drawn as it is."""
        self.time = time
        self.camera_position = camera_position
        self.sea_enabled = sea_enabled
        self.atmosphere = atmosphere
        self.ground = ground


class PropMaterials:
    """Vertex-coloured materials of the props: the lit structure, the self-lit accents and the
    windows (D-210, set by the real kit: see `window_material_visual.py`; None: not drawn)."""

    def __init__(self, structure: Any, lights: Any, windows: Any = None) -> None:
        self.structure = structure
        self.lights = lights
        self.windows = windows


class SeaSize:
    """Size of the sea plane, to repeat its waves at the right scale."""

    def __init__(self, width: float, length: float) -> None:
        self.width = width
        self.length_ = length


class SceneryKitContext:
    """What a kit is built from."""

    def __init__(self, look: Any, sun: Any, sea_level: float, sea_size: SeaSize, seed: int) -> None:
        """`sea_level`: height of the sea (0 when the level has none). `seed`: seed of the
        generated textures."""
        self.look = look
        self.sun = sun
        self.sea_level = sea_level
        self.sea_size = sea_size
        self.seed = seed


__pragma__("skip")


class CloudMaterial(Protocol):
    """The material of one cloud layer, driven frame by frame."""

    material: Any

    def set(self, state: CloudState) -> None: ...


class SceneryKit(Protocol):
    """Materials, textures and shadows of a scenery scene. The real kit needs a WebGL engine; the
    plain kit works anywhere, including the NullEngine of the unit tests."""

    terrain: Any
    sea: Any
    props: PropMaterials
    roads: Any
    weather: Callable[[Any, Any], Any]
    rings: Callable[[Any, Any], Any]
    plume: Callable[[Any, Any], Any]

    def cloud(self, look: Any) -> CloudMaterial: ...

    def aurora(self) -> Any: ...

    def add_shadow_caster(self, mesh: Any) -> None: ...

    def update(self, frame: SceneryKitFrame) -> None: ...


SceneryKitFactory = Callable[[Any, SceneryKitContext], SceneryKit]
__pragma__("noskip")


def _or_default(value: Any, fallback: Any) -> Any:
    """`value ?? fallback`: the fallback when `value` is missing (None)."""
    return fallback if value is None else value


def set_ground_lights(materials: PropMaterials, glow: float) -> None:
    """Sets how bright the props' self-lit accents (windows, neon, street and car lights) are
    (P08-R04: off by day, on at dusk and night)."""
    if is_instance_of(materials.lights, "StandardMaterial"):
        materials.lights.emissiveColor.set(glow, glow, glow)
    if is_instance_of(materials.windows, "StandardMaterial"):
        materials.windows.emissiveColor.set(glow, glow, glow)


# Depth offset of the props' self-lit accents (see `create_prop_materials`).
LIGHTS_Z_OFFSET = -2


def create_prop_materials(scene: Any, look: Any) -> PropMaterials:
    """Vertex-coloured materials of the props: lit structure, and self-lit accents."""
    structure = new_standard_material("prop-structure", scene)
    tone = _or_default(look.tone, 1)
    structure.diffuseColor = color3(tone, tone, tone)
    specular = look.props.specular
    structure.specularColor = color3(specular, specular, specular)
    lights = new_standard_material("prop-lights", scene)
    glow = look.props.lightIntensity
    lights.emissiveColor = color3(glow, glow, glow)
    lights.diffuseColor = color3_black()
    lights.specularColor = color3_black()
    lights.disableLighting = True
    # Pulled towards the camera in depth: the lights lie flat on walls and roads, and would
    # flicker against them, in the glow layer most of all (reviewer, 2026-10-28).
    lights.zOffset = LIGHTS_Z_OFFSET
    return PropMaterials(structure, lights)


def create_road_material(scene: Any) -> Any:
    """Vertex-coloured, lit, see-through material of the road ribbons (their vertex alpha fades
    the edges), pulled towards the camera in depth so they never flicker against the terrain."""
    roads = new_standard_material("roads", scene)
    roads.diffuseColor = color3(1, 1, 1)
    roads.specularColor = color3_black()
    roads.backFaceCulling = False
    roads.zOffset = -2
    # Blended over the ground: overlapping ribbons (crossings) must not hide each other.
    roads.disableDepthWrite = True
    return roads


def _plain_material(label: str, color: Rgb, scene: Any) -> Any:
    material = new_standard_material(label, scene)
    material.diffuseColor = color3(color[0], color[1], color[2])
    material.specularColor = color3_black()
    return material


def _plain_sea(scene: Any, sea: Any) -> Any:
    """A flat sea; phase 10: lava glows by itself, opaque."""
    material = _plain_material("sea", sea.color, scene)
    material.alpha = sea.alpha
    if sea.lava:
        material.alpha = 1
        material.emissiveColor = color3(sea.lava.glow[0], sea.lava.glow[1], sea.lava.glow[2])
        material.disableLighting = True
    return material


class PlainMaterial:
    """A flat material that ignores the frames (the plain kit's stand-in)."""

    def __init__(self, material: Any) -> None:
        self.material = material

    def set(self, frame: Any) -> None:
        """Nothing to drive."""
        return None


class PlainCloudMaterial:
    """A flat cloud layer: opaque while it covers the sky, its colour as set."""

    def __init__(self, material: Any) -> None:
        self.material = material

    def set(self, state: CloudState) -> None:
        self.material.alpha = state.opacity if state.coverage > 0 else 0
        self.material.diffuseColor.set(state.color[0], state.color[1], state.color[2])


def _plain_weather(scene: Any, kind: Any) -> PlainMaterial:
    material = _plain_material("weather", kind.color, scene)
    material.alpha = kind.alpha
    return PlainMaterial(material)


def _plain_rings(scene: Any, rings: Any) -> PlainMaterial:
    material = _plain_material("rain-rings", rings.color, scene)
    material.alpha = rings.alpha
    return PlainMaterial(material)


def _plain_plume(scene: Any, kind: Any) -> PlainMaterial:
    material = _plain_material("plume", kind.color, scene)
    material.alpha = kind.alpha
    return PlainMaterial(material)


class PlainSceneryKit:
    """Flat-coloured stand-ins for every material, with no texture and no shadow
    (`create_plain_scenery_kit`)."""

    def __init__(self, scene: Any, look: Any) -> None:
        self._scene = scene
        self.sea = _plain_sea(scene, look.sea)
        self.props = create_prop_materials(scene, look)
        self.terrain = _plain_material("terrain", look.terrain.ground.colors[1], scene)
        self.roads = create_road_material(scene)
        self.weather = _plain_weather
        self.rings = _plain_rings
        self.plume = _plain_plume

    def cloud(self, look: Any) -> PlainCloudMaterial:
        return PlainCloudMaterial(
            _plain_material("cloud-" + str(look.altitude), look.color, self._scene)
        )

    def aurora(self) -> PlainMaterial:
        material = _plain_material("aurora", (0.2, 1, 0.5), self._scene)
        material.alpha = 0.3
        return PlainMaterial(material)

    def add_shadow_caster(self, mesh: Any) -> None:
        return None

    def update(self, frame: SceneryKitFrame) -> None:
        set_ground_lights(self.props, frame.atmosphere.ground_lights)


def create_plain_scenery_kit(scene: Any, context: SceneryKitContext) -> PlainSceneryKit:
    """A flat-coloured scenery kit (the `SceneryKitFactory` that needs no WebGL)."""
    return PlainSceneryKit(scene, context.look)
