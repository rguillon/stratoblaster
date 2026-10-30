# ruff: noqa: E501 (GLSL shader source lines, kept as in the TypeScript)
"""The material of the rain rings (P09-R05): thin rings spreading in each cell of the water. Ported
from `render/scenery/rain-rings-material.visual.ts`.
"""

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
from org.transcrypt.stubs.browser import __pragma__

from render.babylon import color3, new_glsl_material, vector2, vector3, vector4

__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

# rings: cell size, rings per cell (at strength 1), largest radius, seconds a ring lives.
# state: time, strength, ring opacity.
VERTEX = """
precision highp float;
attribute vec3 position;
uniform mat4 world;
uniform mat4 viewProjection;
varying vec3 vWorld;
void main() {
  vec4 p = world * vec4(position, 1.0);
  vWorld = p.xyz;
  gl_Position = viewProjection * p;
}
"""

FRAGMENT = """
precision highp float;
varying vec3 vWorld;
uniform vec3 cameraPosition;
uniform vec4 rings;
uniform vec3 state;
uniform vec3 ringColor;
uniform vec3 fogColor;
uniform vec2 fogRange;
float hash(vec2 p, float k) {
  return fract(sin(dot(p, vec2(127.1, 311.7)) + k * 74.7) * 43758.5453);
}
void main() {
  vec2 cell = floor(vWorld.xz / rings.x);
  vec2 local = vWorld.xz - cell * rings.x;
  float radius = rings.z;
  // Each cell has one ring at a time, starting at a random moment, in a random place.
  float phase = hash(cell, 1.0);
  float age = fract(state.x / rings.w + phase);
  float round_ = floor(state.x / rings.w + phase);
  vec2 centre = radius + vec2(hash(cell, round_ + 2.0), hash(cell, round_ + 3.0))
    * (rings.x - 2.0 * radius);
  // Fewer cells ring in a lighter rain.
  float lit = step(hash(cell, round_ + 5.0), state.y * rings.y);
  float d = distance(local, centre);
  float r = age * radius;
  float ring = 1.0 - smoothstep(0.0, 0.18 + 0.12 * age, abs(d - r));
  float fade = (1.0 - age) * lit;
  float fog = clamp((distance(vWorld, cameraPosition) - fogRange.x) / (fogRange.y - fogRange.x), 0.0, 1.0);
  gl_FragColor = vec4(mix(ringColor, fogColor, fog), ring * fade * state.z * (1.0 - fog));
}
"""


class RingsMaterialImpl:
    """The rings' material, driven frame by frame (the `RingsMaterial` of `rain_rings`)."""

    def __init__(self, scene: Any, material: Any, rings: Any) -> None:
        self.material = material
        self._scene = scene
        self._rings = rings
        self._state = vector3(0, 0, 0)
        self._fog_color = color3(0, 0, 0)
        self._fog_range = vector2(0, 0)

    def set(self, frame: Any) -> None:
        material = self.material
        fog = frame.fog
        material.setVector3("state", self._state.set(frame.time, frame.strength, self._rings.alpha))
        material.setColor3(
            "fogColor", self._fog_color.set(fog.color[0], fog.color[1], fog.color[2])
        )
        material.setVector2("fogRange", self._fog_range.set(fog.start, fog.end))
        camera = self._scene.activeCamera
        if camera:
            material.setVector3("cameraPosition", camera.globalPosition)


def create_rain_rings_material(scene: Any, rings: Any) -> RingsMaterialImpl:
    """The material of the rain rings (P09-R05): in each cell of the water, a thin ring spreading
    from where a drop landed and fading, one after another at random places; blended, without
    writing depth, so the terrain above the water hides them."""
    material = new_glsl_material(
        "rain-rings",
        scene,
        VERTEX,
        FRAGMENT,
        ["position"],
        [
            "world",
            "viewProjection",
            "cameraPosition",
            "rings",
            "state",
            "ringColor",
            "fogColor",
            "fogRange",
        ],
        None,
        True,
    )
    material.disableDepthWrite = True
    material.setVector4("rings", vector4(rings.cell, rings.per_cell, rings.radius, rings.period))
    material.setColor3("ringColor", color3(rings.color[0], rings.color[1], rings.color[2]))
    return RingsMaterialImpl(scene, material, rings)
