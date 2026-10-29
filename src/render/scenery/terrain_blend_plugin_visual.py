# ruff: noqa: E501 (GLSL shader source lines, kept as in the TypeScript)
"""The terrain's blend plugin (P04-R01, P10-R05): turns a standard material into a terrain material,
blending generated textures by altitude and slope, with a beach, shallows and surf (or lava).
Ported from `render/scenery/terrain-blend-plugin.visual.ts`.

Transcrypt cannot subclass a JavaScript class, so the `MaterialPluginBase` subclass is made by
`render.babylon.new_material_plugin`, whose hooks call the methods of `TerrainBlendOwner`.
"""

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
from org.transcrypt.stubs.browser import __pragma__

from render.babylon import js_object, js_set, new_material_plugin
from render.scenery.terrain_geometry import SURFACE_SCALE

__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")


class TerrainTextures:
    """Textures the terrain blends between, plus a noise texture (R fine, G coarse)."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        low: Any,
        ground: Any,
        steep: Any,
        high: Any,
        lush: Any,
        paved: Any,
        sand: Any,
        noise: Any,
    ) -> None:
        self.low = low
        self.ground = ground
        self.steep = steep
        self.high = high
        self.lush = lush
        self.paved = paved
        self.sand = sand
        self.noise = noise


class TerrainBlendState:
    """Values that change while the scene runs. `lava` (phase 10): the sea is lava, and the rock by
    it glows (P10-R05). `ground` (None when drawn as it is): how the ground is drawn, its colours
    following the ground, not the world (`GroundTransform`)."""

    def __init__(  # noqa: PLR0917 (positional: Transcrypt has no keyword arguments)
        self,
        sea_level: float,
        sea_enabled: bool,
        time: float,
        lava: Any = None,
        ground: Any = None,
    ) -> None:
        self.sea_level = sea_level
        self.sea_enabled = sea_enabled
        self.time = time
        self.lava = lava
        self.ground = ground


SAMPLERS = [
    "terrainLow",
    "terrainGround",
    "terrainSteep",
    "terrainHigh",
    "terrainLush",
    "terrainPaved",
    "terrainSandy",
    "terrainNoise",
]

UNIFORMS = [
    ("terrainHeights", 4, "vec4"),
    ("terrainSlope", 4, "vec4"),
    ("terrainScale", 4, "vec4"),
    ("terrainTintA", 3, "vec3"),
    ("terrainTintB", 3, "vec3"),
    ("terrainSea", 4, "vec4"),
    ("terrainSand", 4, "vec4"),
    ("terrainShallow", 4, "vec4"),
    ("terrainDeep", 3, "vec3"),
    ("terrainFoam", 4, "vec4"),
    ("terrainSurf", 4, "vec4"),
    ("terrainLava", 4, "vec4"),
    ("terrainGroundFrame", 4, "vec4"),
]


def _to_fixed_4(value: float) -> str:
    """`value.toFixed(4)` of JavaScript (the GLSL text takes it as a constant)."""
    __pragma__("js", "{}", "return value.toFixed(4);")
    return ""


# The GLSL text names `SURFACE_SCALE` where the TypeScript template interpolates it.
_SURFACE_TOKEN = "@SURFACE_SCALE@"
_SURFACE_TEXT = _to_fixed_4(SURFACE_SCALE)

_FRAGMENT_DEFINITIONS_TEXT = """
#ifdef TERRAIN_BLEND
uniform sampler2D terrainLow;
uniform sampler2D terrainGround;
uniform sampler2D terrainSteep;
uniform sampler2D terrainHigh;
uniform sampler2D terrainLush;
uniform sampler2D terrainPaved;
uniform sampler2D terrainSandy;
uniform sampler2D terrainNoise;

// Planes and layers weighing less than this are not read (reviewer, 2026-10-28): they would change
// the colour by less than half a step. On flat paved ground, one texture read instead of 21.
const float TERRAIN_SKIP = 1.0 / 512.0;

// Samples a ground texture from the three axis planes, weighted by the normal, so steep
// slopes are not stretched.
vec3 terrainTriplanar(sampler2D tex, vec3 p, vec3 w) {
  float s = terrainScale.x;
  vec3 color = vec3(0.0);
  if (w.x > 0.0) color += texture2D(tex, p.zy * s).rgb * w.x;
  if (w.y > 0.0) color += texture2D(tex, p.xz * s).rgb * w.y;
  if (w.z > 0.0) color += texture2D(tex, p.xy * s).rgb * w.z;
  return color;
}

// A layer of the ground: its texture times its share `k` of the colour, and that share; none
// when too small to show.
vec4 terrainLayer(sampler2D tex, vec3 p, vec3 w, float k) {
  if (k <= TERRAIN_SKIP) return vec4(0.0);
  return vec4(terrainTriplanar(tex, p, w) * k, k);
}

// Where the ground meets the sea: a sand beach above the water, the ground under it tinted by
// the water from turquoise shallows to the deep, and surf (phase 5 review). The sea plane over
// it is mostly see-through, so it only adds the waves' glints: no hard line where they meet.
vec3 terrainShore(vec3 color, vec3 p, vec4 noise, float slope) {
  float time = terrainSea.z;
  float fine = texture2D(terrainNoise, p.xz * terrainScale.y * 7.0).r;
  float depth = terrainSea.x - p.y + (noise.r - 0.5) * 0.8;
  float gentle = 1.0 - smoothstep(terrainSlope.x, terrainSlope.y, slope);
  // Beach: dry sand fading into the ground, darker where the swash wets it.
  vec3 sand = terrainSand.rgb * (0.9 + 0.2 * fine);
  float beach = 1.0 - smoothstep(terrainSand.w * 0.4, terrainSand.w, -depth + (noise.g - 0.5) * 3.0);
  color = mix(color, sand, beach * gentle);
  color *= 1.0 - 0.3 * (1.0 - smoothstep(-1.2, 0.0, -depth)) * gentle;
  // Water: the deeper, the darker, up to the colour of the open sea.
  float deep = smoothstep(0.0, terrainShallow.w, depth);
  vec3 water = mix(terrainShallow.rgb, terrainDeep, sqrt(deep));
  color = mix(color, water, smoothstep(0.0, 1.2, depth) * mix(0.55, 1.0, deep));
  // Surf: a broken line of foam swashing up and down the beach, and bands rolling in.
  float swash = sin(time * 0.9 + noise.g * 14.0) * terrainFoam.w;
  float edge = 1.0 - smoothstep(0.0, terrainFoam.w, abs(depth - swash));
  edge *= smoothstep(0.25, 0.55, fine + noise.r * 0.3);
  float roll = fract(depth / terrainSurf.x + time * terrainSurf.y + noise.g * 1.5);
  float band = smoothstep(0.82, 0.95, roll) * (1.0 - smoothstep(0.92, 1.0, roll) * 0.6);
  band *= smoothstep(0.0, 0.8, depth) * (1.0 - smoothstep(0.0, terrainSurf.z, depth));
  band *= smoothstep(0.4, 0.7, fine);
  return mix(color, terrainFoam.rgb, clamp(edge * 0.9 + band * 0.7, 0.0, 1.0));
}

// Phase 10: where the rock meets lava (P10-R05), it is scorched dark under a hot glowing edge.
vec3 terrainScorch(vec3 color, vec3 p) {
  float above = p.y - terrainSea.x;
  return color * mix(vec3(0.55, 0.42, 0.38), vec3(1.0), smoothstep(0.0, terrainLava.w * 4.0, above));
}

// The glow of the rock by the lava: a bright edge at its level and glowing cracks a little above.
// The ground point drawn at world point `p` (the ground may be drawn scaled and moved).
vec3 groundPoint(vec3 p) {
  return vec3(p.x, p.y, p.z - terrainGroundFrame.y) / terrainGroundFrame.x;
}

vec3 terrainHeat(vec3 p) {
  if (terrainSea.w < 0.5 || terrainSea.y < 0.5) return vec3(0.0);
  float above = p.y - terrainSea.x;
  vec4 noise = texture2D(terrainNoise, p.xz * terrainScale.y * 5.0);
  float flicker = 0.8 + 0.2 * sin(terrainSea.z * 2.3 + noise.g * 12.0);
  float edge = 1.0 - smoothstep(0.0, terrainLava.w * (0.7 + 0.6 * noise.r), above);
  float crack = 1.0 - smoothstep(0.0, 0.035, abs(noise.r - 0.5));
  crack *= 1.0 - smoothstep(0.0, terrainSurf.w, above);
  return terrainLava.rgb * clamp(edge * 1.4 + crack * 0.8, 0.0, 1.6) * flicker;
}

vec3 terrainColor(vec3 p, vec3 n) {
  vec3 w = pow(abs(n), vec3(4.0));
  w /= (w.x + w.y + w.z);
  w *= step(vec3(TERRAIN_SKIP), w);
  w /= (w.x + w.y + w.z);
  vec4 noise = texture2D(terrainNoise, p.xz * terrainScale.y);
  float jitter = noise.r - 0.5;
  float h = p.y + jitter * terrainSlope.z;
  float slope = 1.0 - clamp(n.y, 0.0, 1.0) + jitter * terrainSlope.w;
  float blend = terrainHeights.z;
  // The ground above the low layer, the high layer over them, and the steep layer over all.
  float above = smoothstep(terrainHeights.x - blend, terrainHeights.x + blend, h);
  float high = smoothstep(terrainHeights.y - blend, terrainHeights.y + blend, h);
  float steep = smoothstep(terrainSlope.x, terrainSlope.y, slope);
  float sandy = 0.0;
  float lush = 0.0;
  float paved = 0.0;
#ifdef VERTEXCOLOR
  // Ground cover of the section, from the vertex colour (see terrain-geometry.ts).
  float lushCover = clamp((1.0 - vColor.r) / @SURFACE_SCALE@, 0.0, 1.0);
  float pavedCover = clamp((1.0 - vColor.b) / @SURFACE_SCALE@, 0.0, 1.0);
  float sandyCover = clamp((1.0 - vColor.g) / @SURFACE_SCALE@, 0.0, 1.0);
  // Cover fades in with noise, in patches rather than as a flat gradient: sand over the ground,
  // grass over that, paving over all.
  float patchy = clamp(noise.g * 0.6 + 0.2, 0.0, 1.0);
  sandy = smoothstep(patchy - 0.25, patchy + 0.25, sandyCover);
  lush = smoothstep(patchy - 0.25, patchy + 0.25, lushCover);
  paved = smoothstep(patchy - 0.25, patchy + 0.25, pavedCover);
#endif
  // Each texture's share of the colour, from the layers laid one over the other.
  float ground = above * (1.0 - high) * (1.0 - steep);
  float bare = ground * (1.0 - sandy) * (1.0 - lush) * (1.0 - paved);
  vec4 sum = terrainLayer(terrainLow, p, w, (1.0 - above) * (1.0 - high) * (1.0 - steep));
  if (bare > TERRAIN_SKIP) {
    float tint = smoothstep(0.3, 0.7, texture2D(terrainNoise, p.xz * terrainScale.z).g);
    sum += terrainLayer(terrainGround, p, w, bare) * vec4(mix(terrainTintA, terrainTintB, tint), 1.0);
  }
  sum += terrainLayer(terrainSandy, p, w, ground * sandy * (1.0 - lush) * (1.0 - paved));
  sum += terrainLayer(terrainLush, p, w, ground * lush * (1.0 - paved));
  sum += terrainLayer(terrainPaved, p, w, ground * paved);
  sum += terrainLayer(terrainHigh, p, w, high * (1.0 - steep));
  sum += terrainLayer(terrainSteep, p, w, steep);
  // What was not read is shared out among what was.
  vec3 color = sum.rgb / sum.a;
  if (terrainSea.y > 0.5 && terrainSea.w > 0.5) return terrainScorch(color, p);
  if (terrainSea.y > 0.5) color = terrainShore(color, p, noise, slope);
  return color;
}
#endif
"""

UPDATE_DIFFUSE = """
#ifdef TERRAIN_BLEND
  baseColor.rgb = terrainColor(groundPoint(vPositionW), normalW);
#endif
"""

BEFORE_FOG = """
#ifdef TERRAIN_BLEND
  color.rgb += terrainHeat(groundPoint(vPositionW));
#endif
"""

FRAGMENT_DEFINITIONS = _SURFACE_TEXT.join(_FRAGMENT_DEFINITIONS_TEXT.split(_SURFACE_TOKEN))


def _uniform_spec(uniform_name: str, size: int, type_name: str) -> Any:
    """A uniform of the UBO, as the plugin API reads it (`{name, size, type}`)."""
    spec = js_object()
    js_set(spec, "name", uniform_name)
    js_set(spec, "size", size)
    js_set(spec, "type", type_name)
    return spec


class TerrainBlendOwner:
    """What the plugin's hooks read and write (see `new_terrain_blend_plugin`)."""

    def __init__(self, look: Any, textures: TerrainTextures, state: TerrainBlendState) -> None:
        self._look = look
        self._textures = textures
        self._state = state

    def prepare_defines(self, defines: Any) -> None:
        defines.TERRAIN_BLEND = True

    def get_samplers(self, samplers: Any) -> None:
        for sampler in SAMPLERS:
            samplers.push(sampler)

    def get_uniforms(self) -> Any:
        ubo = []
        declarations = []
        for uniform_name, size, type_name in UNIFORMS:
            ubo.append(_uniform_spec(uniform_name, size, type_name))
            declarations.append("uniform " + type_name + " " + uniform_name + ";")
        result = js_object()
        js_set(result, "ubo", ubo)
        js_set(
            result,
            "fragment",
            "#ifdef TERRAIN_BLEND\n" + "\n".join(declarations) + "\n#endif",
        )
        return result

    def bind_for_sub_mesh(self, ubo: Any) -> None:
        look = self._look
        state = self._state
        textures = self._textures
        ubo.updateFloat4("terrainHeights", look.lowHeight, look.highHeight, look.heightBlend, 0)
        ubo.updateFloat4(
            "terrainSlope",
            look.steepSlope[0],
            look.steepSlope[1],
            look.jitter.height,
            look.jitter.slope,
        )
        ubo.updateFloat4(
            "terrainScale",
            1 / look.tileSize,
            1 / look.noiseTileSize,
            1 / look.tintTileSize,
            0,
        )
        ubo.updateFloat3("terrainTintA", look.tints[0][0], look.tints[0][1], look.tints[0][2])
        ubo.updateFloat3("terrainTintB", look.tints[1][0], look.tints[1][1], look.tints[1][2])
        lava = state.lava
        ubo.updateFloat4(
            "terrainSea",
            state.sea_level,
            1 if state.sea_enabled else 0,
            state.time,
            1 if lava else 0,
        )
        edge_color = [0, 0, 0]
        edge_width = 1
        edge_cracks = 1
        if lava:
            edge_color = lava.edge.color
            edge_width = lava.edge.width
            edge_cracks = lava.edge.cracks
        ubo.updateFloat4("terrainLava", edge_color[0], edge_color[1], edge_color[2], edge_width)
        ground = state.ground
        ground_scale = ground.scale if ground else 1
        ground_offset = ground.offset_z if ground else 0
        ubo.updateFloat4("terrainGroundFrame", ground_scale, ground_offset, 0, 0)
        shore = look.shore
        ubo.updateFloat4("terrainSand", shore.sand[0], shore.sand[1], shore.sand[2], shore.beach)
        ubo.updateFloat4(
            "terrainShallow", shore.shallow[0], shore.shallow[1], shore.shallow[2], shore.depth
        )
        ubo.updateFloat3("terrainDeep", shore.deep[0], shore.deep[1], shore.deep[2])
        foam = shore.foam
        ubo.updateFloat4("terrainFoam", foam.color[0], foam.color[1], foam.color[2], foam.width)
        ubo.updateFloat4("terrainSurf", foam.spacing, foam.speed, foam.reach, edge_cracks)
        ubo.setTexture("terrainLow", textures.low)
        ubo.setTexture("terrainGround", textures.ground)
        ubo.setTexture("terrainSteep", textures.steep)
        ubo.setTexture("terrainHigh", textures.high)
        ubo.setTexture("terrainLush", textures.lush)
        ubo.setTexture("terrainPaved", textures.paved)
        ubo.setTexture("terrainSandy", textures.sand)
        ubo.setTexture("terrainNoise", textures.noise)

    def get_custom_code(self, shader_type: str) -> Any:
        if shader_type != "fragment":
            return None
        code = js_object()
        js_set(code, "CUSTOM_FRAGMENT_DEFINITIONS", FRAGMENT_DEFINITIONS)
        js_set(code, "CUSTOM_FRAGMENT_UPDATE_DIFFUSE", UPDATE_DIFFUSE)
        js_set(code, "CUSTOM_FRAGMENT_BEFORE_FOG", BEFORE_FOG)
        return code


def new_terrain_blend_plugin(
    material: Any, look: Any, textures: TerrainTextures, state: TerrainBlendState
) -> Any:
    """Turns a `StandardMaterial` into a terrain material (P04-R01): the colour comes from four
    generated textures blended by altitude and slope, with noise so the borders wander, large
    tinted patches, and a beach, shallows and surf where the ground meets the sea (phase 10: or,
    by lava, scorched rock with a glowing edge and cracks). Lighting, shadows and fog stay the
    standard material's. Returns the plugin (TypeScript: `new TerrainBlendPlugin(...)`)."""
    owner = TerrainBlendOwner(look, textures, state)
    return new_material_plugin(
        material, owner, "TerrainBlend", 200, "TERRAIN_BLEND", "TerrainBlendPlugin"
    )
