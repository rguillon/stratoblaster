import { ShaderMaterial } from '@babylonjs/core/Materials/shaderMaterial';
import { Color3 } from '@babylonjs/core/Maths/math.color';
import { Vector2, Vector3, Vector4 } from '@babylonjs/core/Maths/math.vector';
import type { RingsMaterialFactory } from './rain-rings';

// rings: cell size, rings per cell (at strength 1), largest radius, seconds a ring lives.
// state: time, strength, ring opacity.
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

const FRAGMENT = /* glsl */ `
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
`;

/**
 * The material of the rain rings (P09-R05): in each cell of the water, a thin ring spreading
 * from where a drop landed and fading, one after another at random places; blended, without
 * writing depth, so the terrain above the water hides them.
 */
export const createRainRingsMaterial: RingsMaterialFactory = (scene, rings) => {
  const material = new ShaderMaterial(
    'rain-rings',
    scene,
    { vertexSource: VERTEX, fragmentSource: FRAGMENT },
    {
      attributes: ['position'],
      uniforms: [
        'world',
        'viewProjection',
        'cameraPosition',
        'rings',
        'state',
        'ringColor',
        'fogColor',
        'fogRange',
      ],
      needAlphaBlending: true,
    },
  );
  material.disableDepthWrite = true;
  material.setVector4('rings', new Vector4(rings.cell, rings.perCell, rings.radius, rings.period));
  material.setColor3('ringColor', new Color3(...rings.color));
  const [state, fogColor, fogRange] = [new Vector3(), new Color3(), new Vector2()];
  return {
    material,
    set: (frame) => {
      material.setVector3('state', state.set(frame.time, frame.strength, rings.alpha));
      material.setColor3('fogColor', fogColor.set(...frame.fog.color));
      material.setVector2('fogRange', fogRange.set(frame.fog.start, frame.fog.end));
      const camera = scene.activeCamera;
      if (camera) material.setVector3('cameraPosition', camera.globalPosition);
    },
  };
};
