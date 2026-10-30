# ruff: noqa: E501 (GLSL shader source lines, kept as in the TypeScript)
"""A cloud layer's material (P04-R03): a generated noise texture cut at a threshold set by the
coverage. Ported from `render/scenery/cloud-material.visual.ts`.
"""

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
from org.transcrypt.stubs.browser import __pragma__

from render.babylon import color3, new_glsl_material, vector2, vector4

__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

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

# cloudParams: coverage, opacity, softness, 1 / tile size. The texture holds evenly spread
# noise (R fine, G coarse), so a coverage of 0.3 covers about 30 % of the sky.
FRAGMENT = """
precision highp float;
varying vec3 vWorld;
uniform sampler2D cloudTexture;
uniform vec4 cloudParams;
uniform vec2 cloudOffset;
uniform vec3 cloudColor;
uniform vec3 cloudShade;
uniform vec3 fogColor;
uniform vec2 fogRange;
uniform vec3 cameraPosition;
void main() {
  vec2 uv = (vWorld.xz + cloudOffset) * cloudParams.w;
  float density = texture2D(cloudTexture, uv).g * 0.65 + texture2D(cloudTexture, uv * 3.1 + 0.37).r * 0.35;
  float threshold = 1.0 - cloudParams.x;
  float edge = smoothstep(threshold - cloudParams.z, threshold + cloudParams.z, density);
  float core = smoothstep(threshold, threshold + cloudParams.z * 4.0, density);
  vec3 color = mix(cloudShade, cloudColor, core);
  float fog = clamp((distance(vWorld, cameraPosition) - fogRange.x) / (fogRange.y - fogRange.x), 0.0, 1.0);
  gl_FragColor = vec4(mix(color, fogColor, fog), edge * cloudParams.y);
}
"""

UNIFORMS = [
    "world",
    "viewProjection",
    "cloudParams",
    "cloudOffset",
    "cloudColor",
    "cloudShade",
    "fogColor",
    "fogRange",
    "cameraPosition",
]


class CloudMaterialImpl:
    """The cloud layer's material, driven frame by frame (the `CloudMaterial` of `scenery_kit`)."""

    def __init__(self, material: Any, look: Any, camera_position: Any) -> None:
        self.material = material
        self._look = look
        self._camera_position = camera_position
        self._params = vector4(0, 0, 0, 0)
        self._offset = vector2(0, 0)
        self._fog_range = vector2(0, 0)
        self._color = color3(0, 0, 0)
        self._shade = color3(0, 0, 0)
        self._fog_color = color3(0, 0, 0)

    def set(self, state: Any) -> None:
        look = self._look
        material = self.material
        self._params.set(state.coverage, state.opacity, look.softness, 1 / look.tileSize)
        self._offset.set(state.offset_x, state.offset_z)
        # P08-R04: the clouds' colours follow the time of day, and fade into its haze.
        material.setColor3(
            "cloudColor", self._color.set(state.color[0], state.color[1], state.color[2])
        )
        material.setColor3(
            "cloudShade", self._shade.set(state.shade[0], state.shade[1], state.shade[2])
        )
        material.setColor3(
            "fogColor",
            self._fog_color.set(state.fog.color[0], state.fog.color[1], state.fog.color[2]),
        )
        material.setVector2("fogRange", self._fog_range.set(state.fog.start, state.fog.end))
        material.setVector4("cloudParams", self._params)
        material.setVector2("cloudOffset", self._offset)
        material.setVector3("cameraPosition", self._camera_position())


def create_cloud_material(
    scene: Any, look: Any, texture: Any, camera_position: Any
) -> CloudMaterialImpl:
    """A cloud layer material (P04-R03): a generated noise texture cut at a threshold set by the
    coverage, with soft edges, faded by the opacity and the fog. Drawn blended, without writing
    depth. `camera_position` is a function giving the camera's position."""
    material = new_glsl_material(
        "cloud-" + str(look.altitude),
        scene,
        VERTEX,
        FRAGMENT,
        ["position"],
        UNIFORMS[:],
        ["cloudTexture"],
        True,
    )
    material.backFaceCulling = False
    material.disableDepthWrite = True
    material.setTexture("cloudTexture", texture)
    return CloudMaterialImpl(material, look, camera_position)
