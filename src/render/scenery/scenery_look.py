# Copyright (c) 2026 Renaud Guillon
"""How a scenery level looks: sky, light, terrain, sea, clouds and props (phase 4).

The interfaces are classes here (Transcrypt has no interfaces). Each takes its fields
positionally, in the order of the interface, with the optional fields last (default None).
"""

from org.transcrypt.stubs.browser import __pragma__

# isort: split
# Typing names are for mypy only: Transcrypt skips this block (it has no typing module). The
# imports here are used in annotations only, so they stay out of the browser build.
# __pragma__ ("skip")
from collections.abc import Callable, Sequence
from typing import Any

from core.scenery.sky_look import SkyScript
from render.geometry.gradient_shapes import ColoredGeometry
from render.geometry.textured import TexturedGeometry
from render.scenery.road_geometry import RoadLook

Rgb = tuple[float, float, float]
# __pragma__ ("noskip")


class TextureLook:
    """A tiling texture generated in code: fractal noise between three colours, plus speckles."""

    def __init__(
        self,
        colors: tuple[Rgb, Rgb, Rgb],
        frequency: float,
        octaves: float,
        speckle: float,
        speckle_color: Rgb,
        strata: float,
        cracks: float | None = None,
        stones: float | None = None,
    ) -> None:
        """`colors`: dark, base and light, at the low, middle and high noise values.

        `frequency`: noise cycles across the texture (first octave). `speckle`: share (0..1) of
        pixels turned into speckles of `speckleColor`. `strata`: horizontal bands, like rock strata.
        `cracks`: thin dark crack lines, as in lake ice (phase 8). `stones`: how much (0..1) the
        texture is stones, each a shade of its own with lit edges and dark joints, as a rock face.
        """
        self.colors = colors
        self.frequency = frequency
        self.octaves = octaves
        self.speckle = speckle
        self.speckleColor = speckle_color
        self.strata = strata
        self.cracks = cracks
        self.stones = stones


class LushDetail:
    """What keeps the grass from being one flat green (GFX-TERRAIN-09).

    `tints`: two tints mixed over the grass in patches by the coarse noise over `tileSize`. `fine`:
    the grass lightened and darkened by up to this much by the fine noise over `fineTileSize`, a
    grain finer than the texture's texels.
    """

    def __init__(
        self, tints: tuple[Rgb, Rgb], tile_size: float, fine_tile_size: float, fine: float
    ) -> None:
        self.tints = tints
        self.tileSize = tile_size
        self.fineTileSize = fine_tile_size
        self.fine = fine


class Jitter:
    """Noise added to the height (world units) and the slope before blending."""

    def __init__(self, height: float, slope: float) -> None:
        self.height = height
        self.slope = slope


class TerrainLook:
    """Generated ground textures blended by altitude and slope (GFX-TERRAIN-08).

    `low` under `lowHeight` (shores, sea bed), `ground` in between, `high` above `highHeight`
    (snow), `steep` on slopes. `lush`, `paved` and `sand` are the covers of the terrain sections
    (GFX-TERRAIN-09).
    """

    def __init__(
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
        lush_detail: LushDetail | None = None,
    ) -> None:
        """`castsShadows`: whether the terrain casts the sun's shadows.

        Default: yes (GFX-TERRAIN-13, PERF-28). `lushDetail`: the grass's patches and grain; none
        by default (one flat green).
        """
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
        self.lushDetail = lush_detail


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
    """The shore, painted on the terrain around the sea level (phase 5 review).

    A sand beach up to `beach` above the water, ground under the water tinted from `shallow` to
    `deep` over `depth`, and surf: a broken foam line at the water's edge and bands of foam rolling
    in.
    """

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
    """The rock where it meets the lava: a glowing edge `width` high, and glowing cracks.

    The cracks rise up to `cracks` above it.
    """

    def __init__(self, color: Rgb, width: float, cracks: float) -> None:
        self.color = color
        self.width = width
        self.cracks = cracks


class LavaLook:
    """Lava (GFX-TERRAIN-16): a self-lit liquid at the sea level, dark crust plates drifting.

    Breaking over a glowing melt. Only a look.
    """

    def __init__(
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
        """`crust`: the dark crust; `plate`: the lit side of its plates; `glow` and `hot`.

        The glow in the cracks and their white-hot heart. `cell`: world units across a plate.
        `crack`: width of the cracks (0..1 of a plate). `churn`: cycles a second. `intensity`:
        brightness of the self-lit colours.
        """
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
    """Water with a generated, drifting normal map that catches the sun (GFX-WATER-03)."""

    def __init__(
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
        liquid is lava (GFX-TERRAIN-16), not water.
        """
        self.color = color
        self.alpha = alpha
        self.roughness = roughness
        self.sunGlint = sun_glint
        self.normalMap = normal_map
        self.tileSize = tile_size
        self.drift = drift
        self.lava = lava


class CloudLayerLook:
    """A layer of clouds under the flight altitude (GFX-SKY-11)."""

    def __init__(
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
        """`coverage`: share (0..1) of the sky covered by this layer.

        `opacity`: 0 = invisible, 1 = opaque. `drift`: world units per second, on top of the
        scrolling. `softness`: fade width (0..1) of the cloud edges. `shade`: colour of the thin
        edges.
        """
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
    """The sun's shadow map: its size.

    The square of ground it covers (fixed, moved by whole texels so shadows do not shimmer), bias,
    normal bias and darkness (0 = black, 1 = none).
    """

    def __init__(
        self, map_size: float, frustum: float, bias: float, normal_bias: float, darkness: float
    ) -> None:
        self.mapSize = map_size
        self.frustum = frustum
        self.bias = bias
        self.normalBias = normal_bias
        self.darkness = darkness


class SunLook:
    """The sun: its elevation (degrees above the horizon).

    Azimuth (0 = straight ahead, +Z, positive towards +X), colour, intensity and shadow.
    """

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
    """The props: their specular and the brightness of their self-lit accents.

    The looks of the windows' atlas (D-210, see `window_atlas.py`) and of the cars' and the trees'
    imposters (D-211, D-212, see `imposters.py`) are read from the config record as it is
    (`look.props.windows`, `look.props.imposters`, `look.props.treeImposters`); these are None
    (drawn as they are) here, which is the case for the looks built by hand.
    """

    def __init__(self, specular: float, light_intensity: float) -> None:
        self.specular = specular
        self.lightIntensity = light_intensity
        self.windows: Any = None
        self.imposters: Any = None
        self.treeImposters: Any = None


class GlowLook:
    """The glow layer: its intensity and blur kernel size."""

    def __init__(self, intensity: float, blur_kernel_size: float) -> None:
        self.intensity = intensity
        self.blurKernelSize = blur_kernel_size


class SceneryLook:
    """How a scenery level looks: sky, light, terrain, sea, clouds and props.

    The optional fields are last: `atmosphere` (phase 8, its sky script, replaces the fixed sky,
    fog, sun, ambient, clouds and ground lights), `shotStyle` (phase 10, the enemy shot style of
    this level), `tone` (phase 14, 0..1, how bright the background is kept under the playfield; 1
    when None).
    """

    def __init__(
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
    """A column of smoke or steam rising from a prop (phase 10, GFX-PROP-18).

    From `at` (model space, at scale 1), of a kind of the engine's `PLUME_KINDS`, `scale` times as
    big as the kind's.
    """

    def __init__(
        self, at: tuple[float, float, float], kind: str, scale: float | None = None
    ) -> None:
        self.at = at
        self.kind = kind
        self.scale = scale


class PropGeometry:
    """Raw geometry of a prop (GFX-PROP-04): its lit structure and its self-lit accents.

    Its lit structure casts shadows. The smoke or steam it sends up, its windows (D-210: quads on
    the walls, mapped on the windows' atlas) and a stand-in that only casts its shadow (D-212: a
    prop drawn as an imposter, whose quad would cast a wrong one; a few low-poly solids round where
    it stands).
    """

    def __init__(
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
    """The camera above the playfield (GFX-CAM-02): its tilt from straight down.

    Vertical field of view, the height of the playfield plane, and `groundScale` (how much bigger
    the ground is drawn, as if flying lower; 1 when None).
    """

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
