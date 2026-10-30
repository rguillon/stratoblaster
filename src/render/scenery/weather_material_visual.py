"""The material of a weather's particles (P08-R05, phases 9-10): soft discs, streaks or sparks moved
on the GPU in a box of air that follows the view.
"""

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
from org.transcrypt.stubs.browser import __pragma__

from render.babylon import (
    babylon_constant,
    color3,
    new_glsl_material,
    vector2,
    vector3,
    vector4,
)

__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

# volume: half width, length, bottom, top. motion: time, slowest fall, fastest fall, wind.
# shape: smallest size, largest size, streak, sway. drift: box start Z, sway frequency.
# align: 0 = stretched sideways (snow in a blizzard), 1 = stretched along the fall (rain).
VERTEX = """
precision highp float;
attribute vec3 position;
attribute vec4 flake;
uniform mat4 viewProjection;
uniform vec3 cameraPosition;
uniform vec3 cameraRight;
uniform vec3 cameraUp;
uniform vec4 volume;
uniform vec4 motion;
uniform vec4 shape;
uniform vec2 drift;
uniform float align;
uniform vec3 spark;
varying vec2 vCorner;
varying float vDistance;
varying float vGlow;
void main() {
  float t = motion.x;
  float height = volume.w - volume.z;
  float width = 2.0 * volume.x;
  float fall = mix(motion.y, motion.z, flake.w);
  float y = volume.w - mod(flake.y * height + fall * t, height);
  float sway = shape.w * sin(6.2831 * (drift.y * t + flake.w * 7.0));
  float x = mod(flake.x * width + motion.w * t + sway, width) - volume.x;
  // Each particle keeps its place along the level: the box slides with the view.
  float z = drift.x + mod(flake.z * volume.y - drift.x, volume.y);
  float size = mix(shape.x, shape.y, fract(flake.w * 13.7));
  vec3 centre = vec3(x, y, z);
  vec3 sideways = cameraRight * position.x * size * (1.0 + shape.z) + cameraUp * position.y * size;
  // Along its way down (wind across, fall down), as thin as its size across the view.
  vec3 along = normalize(vec3(motion.w, -fall, 0.0));
  vec3 across = normalize(cross(along, cameraPosition - centre));
  vec3 streak = across * position.x * size + along * position.y * size * (1.0 + shape.z);
  vec3 p = centre + mix(sideways, streak, align);
  vCorner = position.xy * 2.0;
  vDistance = distance(p, cameraPosition);
  // Phase 10: sparks flicker, each on its own beat, and fade out near the top as they cool.
  float beat = sin(6.2831 * (spark.y * t + flake.w * 11.0)) * 0.5 + 0.5;
  float cool = 1.0 - smoothstep(1.0 - spark.z, 1.0, (y - volume.z) / height);
  vGlow = (1.0 - spark.x * beat) * mix(1.0, cool, step(0.0001, spark.z));
  gl_Position = viewProjection * vec4(p, 1.0);
}
"""

FRAGMENT = """
precision highp float;
varying vec2 vCorner;
varying float vDistance;
varying float vGlow;
uniform vec3 particleColor;
uniform float particleAlpha;
uniform vec3 fogColor;
uniform vec2 fogRange;
uniform float additive;
void main() {
  float soft = 1.0 - smoothstep(0.35, 1.0, length(vCorner));
  float fog = clamp((vDistance - fogRange.x) / (fogRange.y - fogRange.x), 0.0, 1.0);
  float alpha = soft * particleAlpha * (1.0 - 0.7 * fog) * vGlow;
  // Added sparks fade into the haze by dimming; blended particles take its colour.
  vec3 color = mix(mix(particleColor, fogColor, fog), particleColor * alpha, additive);
  gl_FragColor = vec4(color, alpha);
}
"""

UNIFORMS = [
    "viewProjection",
    "cameraPosition",
    "cameraRight",
    "cameraUp",
    "volume",
    "motion",
    "shape",
    "drift",
    "align",
    "spark",
    "additive",
    "particleColor",
    "particleAlpha",
    "fogColor",
    "fogRange",
]


class WeatherMaterialImpl:
    """The particles' material, driven frame by frame (the `WeatherMaterial` of `weather_layer`)."""

    def __init__(self, scene: Any, material: Any, kind: Any) -> None:
        self.material = material
        self._kind = kind
        self._motion = vector4(0, 0, 0, 0)
        self._shape = vector4(0, 0, 0, 0)
        self._drift = vector2(0, 0)
        self._fog_range = vector2(0, 0)
        self._fog_color = color3(0, 0, 0)

    def set(self, frame: Any) -> None:
        kind = self._kind
        material = self.material
        along_fall = kind.align == "fall"
        s = min(1, max(0, frame.strength))
        wind = kind.wind[0] + (kind.wind[1] - kind.wind[0]) * s
        self._motion.set(frame.time, kind.fall[0], kind.fall[1], wind)
        self._shape.set(
            kind.size[0],
            kind.size[1],
            kind.streak * (1 if along_fall else s * s),
            kind.sway[0],
        )
        self._drift.set(frame.start, kind.sway[1])
        material.setVector4("motion", self._motion)
        material.setVector4("shape", self._shape)
        material.setVector2("drift", self._drift)
        material.setVector3("cameraPosition", frame.camera_position)
        material.setVector3("cameraRight", frame.right)
        material.setVector3("cameraUp", frame.up)
        material.setColor3(
            "fogColor",
            self._fog_color.set(frame.fog.color[0], frame.fog.color[1], frame.fog.color[2]),
        )
        material.setVector2("fogRange", self._fog_range.set(frame.fog.start, frame.fog.end))


def create_weather_material(scene: Any, kind: Any) -> WeatherMaterialImpl:
    """The material of a weather's particles (P08-R05): soft, faint discs placed and moved on the
    GPU in a box of air that follows the view, falling, swaying and blown sideways by a wind that
    grows with the strength (streaking them at 1), fading into the haze. Phase 9: a kind aligned
    with its fall (rain) is drawn as thin streaks along the way it falls, at every strength. Blended
    (phase 10: or added, for self-lit sparks that flicker and cool as they rise: embers), without
    writing depth, so they never hide what is drawn after them (the playfield)."""
    material = new_glsl_material(
        "weather",
        scene,
        VERTEX,
        FRAGMENT,
        ["position", "flake"],
        UNIFORMS[:],
        None,
        True,
    )
    material.backFaceCulling = False
    material.disableDepthWrite = True
    additive = kind.blend == "add"
    if additive:
        material.alphaMode = babylon_constant("ALPHA_ONEONE")
    material.setFloat("additive", 1 if additive else 0)
    flicker = kind.flicker
    amount = flicker.amount if flicker else 0
    hz = flicker.hz if flicker else 0
    fade_high = kind.fade_high if kind.fade_high is not None else 0
    material.setVector3("spark", vector3(amount, hz, fade_high))
    volume = kind.volume
    material.setVector4(
        "volume", vector4(volume.half_width, volume.length_, volume.bottom, volume.top)
    )
    material.setColor3("particleColor", color3(kind.color[0], kind.color[1], kind.color[2]))
    material.setFloat("particleAlpha", kind.alpha)
    along_fall = kind.align == "fall"
    material.setFloat("align", 1 if along_fall else 0)
    return WeatherMaterialImpl(scene, material, kind)
