# ruff: noqa: E501 (GLSL shader source lines, kept as in the TypeScript)
"""The material of a kind of plume (phase 10, P10-R08): soft puffs rising from a prop's column, drawn
with instancing. Ported from `render/scenery/plume-material.visual.ts`.
"""

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
from org.transcrypt.stubs.browser import __pragma__

from render.babylon import color3, new_glsl_material, vector2, vector4

__pragma__("skip")
from typing import Any  # noqa: E402

__pragma__("noskip")

# motion: time, seconds to rise, height, lean. size: bottom, top.
VERTEX = """
precision highp float;
attribute vec3 position;
attribute vec4 puff;
attribute float puffScale;
#include<instancesDeclaration>
uniform mat4 viewProjection;
uniform vec3 cameraPosition;
uniform vec3 cameraRight;
uniform vec3 cameraUp;
uniform vec4 motion;
uniform vec2 size;
varying vec2 vCorner;
varying float vFade;
varying float vDistance;
void main() {
#include<instancesVertex>
  // Each placed prop puffs out of step with the others.
  float offset = fract(dot(finalWorld[3].xz, vec2(0.0131, 0.0173)));
  float age = fract(motion.x / motion.y + puff.w + offset);
  float scale = length(finalWorld[0].xyz) * puffScale;
  vec3 foot = (finalWorld * vec4(puff.xyz, 1.0)).xyz;
  vec3 centre = foot + vec3(motion.w * age * age, motion.z * age, 0.0) * scale;
  float across = mix(size.x, size.y, sqrt(age)) * scale;
  vec3 p = centre + (cameraRight * position.x + cameraUp * position.y) * across;
  vCorner = position.xy * 2.0;
  vFade = smoothstep(0.0, 0.12, age) * (1.0 - smoothstep(0.5, 1.0, age));
  vDistance = distance(p, cameraPosition);
  gl_Position = viewProjection * vec4(p, 1.0);
}
"""

FRAGMENT = """
precision highp float;
varying vec2 vCorner;
varying float vFade;
varying float vDistance;
uniform vec3 plumeColor;
uniform float plumeAlpha;
uniform vec3 fogColor;
uniform vec2 fogRange;
void main() {
  float r = length(vCorner);
  // A soft, slightly lumpy puff.
  float lumps = 0.85 + 0.15 * sin(atan(vCorner.y, vCorner.x) * 5.0 + vFade * 3.0);
  float soft = 1.0 - smoothstep(0.25 * lumps, lumps, r);
  float fog = clamp((vDistance - fogRange.x) / (fogRange.y - fogRange.x), 0.0, 1.0);
  gl_FragColor = vec4(mix(plumeColor, fogColor, fog), soft * vFade * plumeAlpha * (1.0 - 0.6 * fog));
}
"""

UNIFORMS = [
    "world",
    "viewProjection",
    "cameraPosition",
    "cameraRight",
    "cameraUp",
    "motion",
    "size",
    "plumeColor",
    "plumeAlpha",
    "fogColor",
    "fogRange",
]


def _lit_channel(kind: Any, light: Any, i: int) -> float:
    """One channel of a plume's colour: lit by the scene, never less than its self-lit share."""
    value: float = kind.color[i] * max(kind.self_lit, min(1, light[i]))
    return value


class PlumeMaterialImpl:
    """The plume material, driven frame by frame (the `PlumeMaterial` of `plume_layer`)."""

    def __init__(self, material: Any, kind: Any) -> None:
        self.material = material
        self._kind = kind
        self._motion = vector4(0, kind.seconds, kind.height, kind.lean)
        self._color = color3(0, 0, 0)
        self._fog_color = color3(0, 0, 0)
        self._fog_range = vector2(0, 0)

    def set(self, frame: Any) -> None:
        material = self.material
        self._motion.x = frame.time
        material.setVector4("motion", self._motion)
        lit = _lit_channel
        kind = self._kind
        material.setColor3(
            "plumeColor",
            self._color.set(
                lit(kind, frame.light, 0), lit(kind, frame.light, 1), lit(kind, frame.light, 2)
            ),
        )
        material.setVector3("cameraPosition", frame.camera_position)
        material.setVector3("cameraRight", frame.right)
        material.setVector3("cameraUp", frame.up)
        material.setColor3(
            "fogColor",
            self._fog_color.set(frame.fog.color[0], frame.fog.color[1], frame.fog.color[2]),
        )
        material.setVector2("fogRange", self._fog_range.set(frame.fog.start, frame.fog.end))


def create_plume_material(scene: Any, kind: Any) -> PlumeMaterialImpl:
    """The material of a kind of plume (phase 10, P10-R08): soft puffs facing the camera, rising
    from the column's foot, growing, bending with the wind and fading out at the top, lit by the
    scene (a little self-lit, as if from the fire below at night). Blended without writing depth,
    so the ground in front hides it but it never hides what is drawn after it (the playfield)."""
    material = new_glsl_material(
        "plume",
        scene,
        VERTEX,
        FRAGMENT,
        ["position", "puff", "puffScale"],
        UNIFORMS[:],
        None,
        True,
    )
    material.backFaceCulling = False
    material.disableDepthWrite = True
    material.setVector4("motion", vector4(0, kind.seconds, kind.height, kind.lean))
    material.setVector2("size", vector2(kind.size[0], kind.size[1]))
    material.setFloat("plumeAlpha", kind.alpha)
    return PlumeMaterialImpl(material, kind)
