"""How a scenery level looks: sky, light, terrain, sea, clouds and props (P04)

The interfaces are classes here (Transcrypt has no interfaces). Each takes its fields
positionally, in the order of the interface, with the optional fields last (default None).
"""

from org.transcrypt.stubs.browser import __pragma__

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module). The
# imports here are used in annotations only, so they stay out of the browser build.
__pragma__("skip")
from collections.abc import Callable, Sequence  # noqa: E402
from typing import Any  # noqa: E402

from core.scenery.sky_look import SkyScript  # noqa: E402
from render.geometry.gradient_shapes import ColoredGeometry  # noqa: E402
from render.geometry.textured import TexturedGeometry  # noqa: E402
from render.scenery.road_geometry import RoadLook  # noqa: E402

Rgb = tuple[float, float, float]
__pragma__("noskip")


class TextureLook:
    """A tiling texture generated in code: fractal noise between three colours, plus speckles."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        colors: tuple[Rgb, Rgb, Rgb],
        frequency: float,
        octaves: float,
        speckle: float,
        speckle_color: Rgb,
        strata: float,
        cracks: float | None = None,
    ) -> None:
        """`colors`: dark, base and light, at the low, middle and high noise values. `frequency`:
        noise cycles across the texture (first octave). `speckle`: share (0..1) of pixels turned
        into speckles of `speckleColor`. `strata`: horizontal bands, like rock strata. `cracks`:
        thin dark crack lines, as in lake ice (phase 8)."""
        self.colors = colors
        self.frequency = frequency
        self.octaves = octaves
        self.speckle = speckle
        self.speckleColor = speckle_color
        self.strata = strata
        self.cracks = cracks


class Jitter:
    """Noise added to the height (world units) and the slope before blending."""

    def __init__(self, height: float, slope: float) -> None:
        self.height = height
        self.slope = slope


class TerrainLook:
    """Generated ground textures blended by altitude and slope (P04-R01): `low` under
    `lowHeight` (shores, sea bed), `ground` in between, `high` above `highHeight` (snow),
    `steep` on slopes. `lush`, `paved` and `sand` are the covers of the terrain sections."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        texture_size: float,
        tile_size: float,
        low: TextureLook,
        ground: TextureLook,
        steep: TextureLook,
        high: TextureLook,
        lush: TextureLook,
        paved: TextureLook,
        sand: TextureLook,
        low_height: float,
        high_height: float,
        height_blend: float,
        steep_slope: tuple[float, float],
        jitter: Jitter,
        noise_tile_size: float,
        tints: tuple[Rgb, Rgb],
        tint_tile_size: float,
        shore: "ShoreLook",
        specular: float,
        casts_shadows: bool | None = None,
    ) -> None:
        """`castsShadows`: whether the terrain casts the sun's shadows (default: yes)."""
        self.textureSize = texture_size
        self.tileSize = tile_size
        self.low = low
        self.ground = ground
        self.steep = steep
        self.high = high
        self.lush = lush
        self.paved = paved
        self.sand = sand
        self.lowHeight = low_height
        self.highHeight = high_height
        self.heightBlend = height_blend
        self.steepSlope = steep_slope
        self.jitter = jitter
        self.noiseTileSize = noise_tile_size
        self.tints = tints
        self.tintTileSize = tint_tile_size
        self.shore = shore
        self.specular = specular
        self.castsShadows = casts_shadows


class ShoreFoam:
    """The foam at the water's edge: its colour, half-height, band spacing, speed and reach."""

    def __init__(
        self, color: Rgb, width: float, spacing: float, speed: float, reach: float
    ) -> None:
        self.color = color
        self.width = width
        self.spacing = spacing
        self.speed = speed
        self.reach = reach


class ShoreLook:
    """The shore, painted on the terrain around the sea level (phase 5 review): a sand beach up to
    `beach` above the water, ground under the water tinted from `shallow` to `deep` over `depth`,
    and surf: a broken foam line at the water's edge and bands of foam rolling in."""

    def __init__(
        self, sand: Rgb, beach: float, shallow: Rgb, deep: Rgb, depth: float, foam: ShoreFoam
    ) -> None:
        self.sand = sand
        self.beach = beach
        self.shallow = shallow
        self.deep = deep
        self.depth = depth
        self.foam = foam


class SeaNormalMap:
    """The generated normal map of the water: size, noise frequency and octaves, wave slope."""

    def __init__(self, size: float, frequency: float, octaves: float, strength: float) -> None:
        self.size = size
        self.frequency = frequency
        self.octaves = octaves
        self.strength = strength


class LavaEdge:
    """The rock where it meets the lava: a glowing edge `width` high, and glowing cracks up to
    `cracks` above it."""

    def __init__(self, color: Rgb, width: float, cracks: float) -> None:
        self.color = color
        self.width = width
        self.cracks = cracks


class LavaLook:
    """Lava (P10-R05): a self-lit liquid at the sea level, dark crust plates drifting and breaking
    over a glowing melt. Only a look."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        crust: Rgb,
        plate: Rgb,
        glow: Rgb,
        hot: Rgb,
        cell: float,
        crack: float,
        churn: float,
        intensity: float,
        edge: LavaEdge,
    ) -> None:
        """`crust`: the dark crust; `plate`: the lit side of its plates; `glow` and `hot`: the glow
        in the cracks and their white-hot heart. `cell`: world units across a plate. `crack`: width
        of the cracks (0..1 of a plate). `churn`: cycles a second. `intensity`: brightness of the
        self-lit colours."""
        self.crust = crust
        self.plate = plate
        self.glow = glow
        self.hot = hot
        self.cell = cell
        self.crack = crack
        self.churn = churn
        self.intensity = intensity
        self.edge = edge


class SeaLook:
    """Water with a generated, drifting normal map that catches the sun (P04-R02)."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        color: Rgb,
        alpha: float,
        roughness: float,
        sun_glint: float,
        normal_map: SeaNormalMap,
        tile_size: float,
        drift: tuple[float, float],
        lava: LavaLook | None = None,
    ) -> None:
        """`sunGlint`: strength of the sun's direct light on the water (above 1, brighter glint).
        `drift`: world units per second the waves drift along X and Z. `lava` (phase 10): the
        liquid is lava (P10-R05), not water."""
        self.color = color
        self.alpha = alpha
        self.roughness = roughness
        self.sunGlint = sun_glint
        self.normalMap = normal_map
        self.tileSize = tile_size
        self.drift = drift
        self.lava = lava


class CloudLayerLook:
    """A layer of clouds under the flight altitude (P04-R03)."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        altitude: float,
        coverage: float,
        opacity: float,
        tile_size: float,
        drift: tuple[float, float],
        softness: float,
        color: Rgb,
        shade: Rgb,
    ) -> None:
        """`coverage`: share (0..1) of the sky covered by this layer. `opacity`: 0 = invisible,
        1 = opaque. `drift`: world units per second, on top of the scrolling. `softness`: fade
        width (0..1) of the cloud edges. `shade`: colour of the thin edges."""
        self.altitude = altitude
        self.coverage = coverage
        self.opacity = opacity
        self.tileSize = tile_size
        self.drift = drift
        self.softness = softness
        self.color = color
        self.shade = shade


class SceneryLookSky:
    """The sky of a look: its haze (clear and fog colour) and the gradient used for reflections."""

    def __init__(self, haze: Rgb, stops: Sequence[Any], environment_intensity: float) -> None:
        self.haze = haze
        self.stops = stops
        self.environmentIntensity = environment_intensity


class SceneryFog:
    """Linear fog, in world units from the camera."""

    def __init__(self, start: float, end: float) -> None:
        self.start = start
        self.end = end


class ShadowLook:
    """The sun's shadow map: its size, the square of ground it covers (fixed, moved by whole
    texels so shadows do not shimmer), bias, normal bias and darkness (0 = black, 1 = none)."""

    def __init__(
        self, map_size: float, frustum: float, bias: float, normal_bias: float, darkness: float
    ) -> None:
        self.mapSize = map_size
        self.frustum = frustum
        self.bias = bias
        self.normalBias = normal_bias
        self.darkness = darkness


class SunLook:
    """The sun: its elevation (degrees above the horizon), azimuth (0 = straight ahead, +Z,
    positive towards +X), colour, intensity and shadow."""

    def __init__(
        self,
        elevation_deg: float,
        azimuth_deg: float,
        color: Rgb,
        intensity: float,
        shadow: ShadowLook,
    ) -> None:
        self.elevationDeg = elevation_deg
        self.azimuthDeg = azimuth_deg
        self.color = color
        self.intensity = intensity
        self.shadow = shadow


class AmbientLook:
    """The ambient light: from the sky and from the ground, and its intensity."""

    def __init__(self, sky: Rgb, ground: Rgb, intensity: float) -> None:
        self.sky = sky
        self.ground = ground
        self.intensity = intensity


class PropsLook:
    """The props: their specular and the brightness of their self-lit accents. The looks of the
    windows' atlas (D-210, see `window_atlas.py`) and of the cars' and the trees' imposters (D-211,
    D-212, see `imposters.py`) are read from the config record as it is (`look.props.windows`,
    `look.props.imposters`, `look.props.treeImposters`); these are None (drawn as they are) here,
    which is the case for the looks built by hand."""

    def __init__(self, specular: float, light_intensity: float) -> None:
        self.specular = specular
        self.lightIntensity = light_intensity
        self.windows: Any = None  # noqa: ANN401 (a config record)
        self.imposters: Any = None  # noqa: ANN401 (a config record)
        self.treeImposters: Any = None  # noqa: ANN401 (a config record)


class GlowLook:
    """The glow layer: its intensity and blur kernel size."""

    def __init__(self, intensity: float, blur_kernel_size: float) -> None:
        self.intensity = intensity
        self.blurKernelSize = blur_kernel_size


class SceneryLook:
    """How a scenery level looks: sky, light, terrain, sea, clouds and props. The optional fields
    are last: `atmosphere` (phase 8, its sky script, replaces the fixed sky, fog, sun, ambient,
    clouds and ground lights), `shotStyle` (phase 10, the enemy shot style of this level),
    `tone` (phase 14, 0..1, how bright the background is kept under the playfield; 1 when None)."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        sky: SceneryLookSky,
        fog: SceneryFog,
        sun: SunLook,
        ambient: AmbientLook,
        terrain: TerrainLook,
        sea: SeaLook,
        clouds: Sequence[CloudLayerLook],
        roads: RoadLook,
        props: PropsLook,
        glow: GlowLook,
        atmosphere: SkyScript | None = None,
        shot_style: str | None = None,
        tone: float | None = None,
    ) -> None:
        self.sky = sky
        self.fog = fog
        self.sun = sun
        self.ambient = ambient
        self.terrain = terrain
        self.sea = sea
        self.clouds = clouds
        self.roads = roads
        self.props = props
        self.glow = glow
        self.atmosphere = atmosphere
        self.shotStyle = shot_style
        self.tone = tone


class PropPlume:
    """A column of smoke or steam rising from a prop (phase 10, P10-R08): from `at` (model space,
    at scale 1), of a kind of the engine's `PLUME_KINDS`, `scale` times as big as the kind's."""

    def __init__(
        self, at: tuple[float, float, float], kind: str, scale: float | None = None
    ) -> None:
        self.at = at
        self.kind = kind
        self.scale = scale


class PropGeometry:
    """Raw geometry of a prop: its lit structure (casts shadows), its self-lit accents, the
    smoke or steam it sends up, its windows (D-210: quads on the walls, mapped on the windows'
    atlas) and a stand-in that only casts its shadow (D-212: a prop drawn as an imposter, whose
    quad would cast a wrong one; a few low-poly solids round where it stands)."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        structure: ColoredGeometry,
        lights: ColoredGeometry | None = None,
        plumes: Sequence[PropPlume] | None = None,
        windows: TexturedGeometry | None = None,
        shadow: ColoredGeometry | None = None,
    ) -> None:
        self.structure = structure
        self.lights = lights
        self.plumes = plumes
        self.windows = windows
        self.shadow = shadow


# Builds the geometry of one kind of prop, standing on Y = 0, centred on the origin.
__pragma__("skip")
PropModelFactory = Callable[[], PropGeometry]
__pragma__("noskip")


class PlayfieldCameraLook:
    """The camera above the playfield (P04-R05): its tilt from straight down, vertical field of
    view, the height of the playfield plane, and `groundScale` (how much bigger the ground is
    drawn, as if flying lower; 1 when None)."""

    def __init__(
        self,
        tilt_deg: float,
        fov_deg: float,
        flight_altitude: float,
        ground_scale: float | None = None,
    ) -> None:
        self.tiltDeg = tilt_deg
        self.fovDeg = fov_deg
        self.flightAltitude = flight_altitude
        self.groundScale = ground_scale
