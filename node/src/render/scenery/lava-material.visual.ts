import type { Scene } from '@babylonjs/core/scene';
import { ShaderMaterial } from '@babylonjs/core/Materials/shaderMaterial';
import { Color3 } from '@babylonjs/core/Maths/math.color';
import { Vector2, Vector3, Vector4 } from '@babylonjs/core/Maths/math.vector';
import type { LavaLook } from './scenery-look';

const VERTEX = /* glsl */ `
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
`;

// shape: plate size, crack width, churn (cycles / s), brightness. motion: time, flow X, flow Z.
const FRAGMENT = /* glsl */ `
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
`;

const UNIFORMS = [
  'world',
  'viewProjection',
  'shape',
  'motion',
  'crustColor',
  'plateColor',
  'glowColor',
  'hotColor',
  'cameraPosition',
  'fogColor',
  'fogRange',
] as const;

type Rgb = readonly [number, number, number];

/** What the lava shows on one frame. */
export interface LavaFrame {
  readonly time: number;
  readonly fog: { readonly color: Rgb; readonly start: number; readonly end: number };
}

/** The lava's material, driven frame by frame. */
export interface LavaMaterial {
  readonly material: ShaderMaterial;
  set(frame: LavaFrame): void;
}

/**
 * Lava (P10-R05): dark crust plates over a glowing melt that shows in the cracks between them,
 * white-hot at their heart, the plates churning, parting and closing as they drift with the
 * `flow` (world units a second). Self-lit, so it shows by night and blooms in the glow layer
 * (it is drawn there with this same material); it lights nothing (no real light, P10-R05).
 */
export function createLavaMaterial(
  scene: Scene,
  look: LavaLook,
  flow: readonly [number, number],
): LavaMaterial {
  const material = new ShaderMaterial(
    'lava',
    scene,
    { vertexSource: VERTEX, fragmentSource: FRAGMENT },
    { attributes: ['position'], uniforms: [...UNIFORMS] },
  );
  material.setVector4('shape', new Vector4(look.cell, look.crack, look.churn, look.intensity));
  material.setColor3('crustColor', new Color3(...look.crust));
  material.setColor3('plateColor', new Color3(...look.plate));
  material.setColor3('glowColor', new Color3(...look.glow));
  material.setColor3('hotColor', new Color3(...look.hot));
  const fogColor = new Color3();
  const fogRange = new Vector2();
  const motion = new Vector3();
  return {
    material,
    set: ({ time, fog }) => {
      material.setVector3('motion', motion.set(time, flow[0], flow[1]));
      material.setColor3('fogColor', fogColor.set(...fog.color));
      material.setVector2('fogRange', fogRange.set(fog.start, fog.end));
      const camera = scene.activeCamera?.globalPosition;
      if (camera) material.setVector3('cameraPosition', camera);
    },
  };
}
