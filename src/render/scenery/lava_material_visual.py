# ruff: noqa: E501
"""Lava (P10-R05): crust plates over a glowing melt, drawn by one self-lit material."""

# Typing names are for mypy only: Transcrypt skips this block (it has no typing module).
from org.transcrypt.stubs.browser import __pragma__

from render.babylon import color3, new_glsl_material, vector2, vector3, vector4

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

# shape: plate size, crack width, churn (cycles / s), brightness. motion: time, flow X, flow Z.
FRAGMENT = """
precision highp float;
varying vec3 vWorld;
uniform vec4 shape;
uniform vec3 motion;
uniform vec3 crustColor;
uniform vec3 plateColor;
uniform vec3 glowColor;
uniform vec3 hotColor;
uniform vec3 cameraPosition;
uniform vec3 fogColor;
uniform vec2 fogRange;

vec2 hash2(vec2 p) {
  p = vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3)));
  return fract(sin(p) * 43758.5453);
}

float noise(vec2 p) {
  vec2 i = floor(p);
  vec2 f = fract(p);
  vec2 u = f * f * (3.0 - 2.0 * f);
  float a = hash2(i).x;
  float b = hash2(i + vec2(1.0, 0.0)).x;
  float c = hash2(i + vec2(0.0, 1.0)).x;
  float d = hash2(i + vec2(1.0, 1.0)).x;
  return mix(mix(a, b, u.x), mix(c, d, u.x), u.y);
}

// Distances to the nearest and second nearest plate centres, and the nearest plate's own random
// value. The centres wander, so the plates churn, part and close up again.
vec3 plates(vec2 p, float t) {
  vec2 cell = floor(p);
  float f1 = 8.0;
  float f2 = 8.0;
  float id = 0.0;
  for (int j = -1; j <= 1; j++) {
    for (int i = -1; i <= 1; i++) {
      vec2 o = vec2(float(i), float(j));
      vec2 h = hash2(cell + o);
      vec2 centre = o + 0.5 + 0.42 * sin(6.2831 * (h + t * (0.5 + h.yx)));
      float d = length(centre - fract(p));
      if (d < f1) {
        f2 = f1;
        f1 = d;
        id = h.x;
      } else if (d < f2) {
        f2 = d;
      }
    }
  }
  return vec3(f1, f2, id);
}

void main() {
  float t = motion.x;
  vec2 p = (vWorld.xz - motion.yz * t) / shape.x;
  // A slow warp, so the plates drift and turn rather than slide as one sheet.
  p += 0.35 * vec2(noise(p * 0.45 + t * shape.z), noise(p * 0.45 - t * shape.z + 7.3));
  vec3 w = plates(p, t * shape.z);
  float border = w.y - w.x;
  // Cracks open and close along the borders; some plates break up where the noise is low.
  float width = shape.y * (0.6 + 0.8 * noise(p * 0.7 + t * shape.z * 2.0));
  float crack = 1.0 - smoothstep(0.0, width * 0.45, border);
  float warm = 1.0 - smoothstep(0.0, width * 1.6, border);
  // Mostly dark crust: each plate a little lighter towards its middle, glowing only at its rim.
  vec3 plate = mix(crustColor, plateColor, w.z * (1.0 - smoothstep(0.0, 0.6, w.x)));
  vec3 color = mix(plate, glowColor * 0.5, warm * 0.35);
  color = mix(color, glowColor, crack);
  float pulse = 0.75 + 0.25 * sin(t * 1.7 + w.z * 6.2831);
  color = mix(color, hotColor, crack * crack * pulse);
  color *= shape.w;
  // Self-lit: the haze dims it with distance but never quite hides its glow.
  float fog = clamp((distance(vWorld, cameraPosition) - fogRange.x) / (fogRange.y - fogRange.x), 0.0, 1.0);
  gl_FragColor = vec4(mix(color, fogColor, fog * 0.85), 1.0);
}
"""

UNIFORMS = [
    "world",
    "viewProjection",
    "shape",
    "motion",
    "crustColor",
    "plateColor",
    "glowColor",
    "hotColor",
    "cameraPosition",
    "fogColor",
    "fogRange",
]


class LavaFrame:
    """What the lava shows on one frame."""

    def __init__(self, time: float, fog: Any) -> None:
        self.time = time
        self.fog = fog


class LavaMaterialImpl:
    """The lava's material, driven frame by frame (`set`)."""

    def __init__(self, scene: Any, material: Any, flow: tuple[float, float]) -> None:
        self.material = material
        self._scene = scene
        self._flow = flow
        self._fog_color = color3(0, 0, 0)
        self._fog_range = vector2(0, 0)
        self._motion = vector3(0, 0, 0)

    def set(self, frame: LavaFrame) -> None:
        material = self.material
        fog = frame.fog
        material.setVector3("motion", self._motion.set(frame.time, self._flow[0], self._flow[1]))
        material.setColor3(
            "fogColor", self._fog_color.set(fog.color[0], fog.color[1], fog.color[2])
        )
        material.setVector2("fogRange", self._fog_range.set(fog.start, fog.end))
        camera = self._scene.activeCamera
        if camera and camera.globalPosition:
            material.setVector3("cameraPosition", camera.globalPosition)


def create_lava_material(scene: Any, look: Any, flow: tuple[float, float]) -> LavaMaterialImpl:
    """Lava (P10-R05): dark crust plates over a glowing melt that shows in the cracks between them,
    white-hot at their heart, the plates churning, parting and closing as they drift with the
    `flow` (world units a second). Self-lit, so it shows by night and blooms in the glow layer
    (it is drawn there with this same material); it lights nothing (no real light, P10-R05)."""
    material = new_glsl_material(
        "lava",
        scene,
        VERTEX,
        FRAGMENT,
        ["position"],
        UNIFORMS[:],
        None,
        None,
    )
    material.setVector4("shape", vector4(look.cell, look.crack, look.churn, look.intensity))
    material.setColor3("crustColor", color3(look.crust[0], look.crust[1], look.crust[2]))
    material.setColor3("plateColor", color3(look.plate[0], look.plate[1], look.plate[2]))
    material.setColor3("glowColor", color3(look.glow[0], look.glow[1], look.glow[2]))
    material.setColor3("hotColor", color3(look.hot[0], look.hot[1], look.hot[2]))
    return LavaMaterialImpl(scene, material, flow)
