import type { Scene } from '@babylonjs/core/scene';
import { ShaderMaterial } from '@babylonjs/core/Materials/shaderMaterial';
import { Color3 } from '@babylonjs/core/Maths/math.color';
import { Vector2, Vector4 } from '@babylonjs/core/Maths/math.vector';
import type { WeatherKind } from '../../config/weather';
import type { WeatherMaterial } from './weather-layer';

// volume: half width, length, bottom, top. motion: time, slowest fall, fastest fall, wind.
// shape: smallest size, largest size, streak, sway. drift: box start Z, sway frequency.
// align: 0 = stretched sideways (snow in a blizzard), 1 = stretched along the fall (rain).
const VERTEX = /* glsl */ `
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
varying vec2 vCorner;
varying float vDistance;
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
  gl_Position = viewProjection * vec4(p, 1.0);
}
`;

const FRAGMENT = /* glsl */ `
precision highp float;
varying vec2 vCorner;
varying float vDistance;
uniform vec3 particleColor;
uniform float particleAlpha;
uniform vec3 fogColor;
uniform vec2 fogRange;
void main() {
  float soft = 1.0 - smoothstep(0.35, 1.0, length(vCorner));
  float fog = clamp((vDistance - fogRange.x) / (fogRange.y - fogRange.x), 0.0, 1.0);
  gl_FragColor = vec4(mix(particleColor, fogColor, fog), soft * particleAlpha * (1.0 - 0.7 * fog));
}
`;

const UNIFORMS = [
  'viewProjection',
  'cameraPosition',
  'cameraRight',
  'cameraUp',
  'volume',
  'motion',
  'shape',
  'drift',
  'align',
  'particleColor',
  'particleAlpha',
  'fogColor',
  'fogRange',
] as const;

/**
 * The material of a weather's particles (P08-R05): soft, faint discs placed and moved on the GPU
 * in a box of air that follows the view, falling, swaying and blown sideways by a wind that
 * grows with the strength (streaking them at 1), fading into the haze. Phase 9: a kind aligned
 * with its fall (rain) is drawn as thin streaks along the way it falls, at every strength. Blended, without
 * writing depth, so they never hide what is drawn after them (the playfield).
 */
export function createWeatherMaterial(scene: Scene, kind: WeatherKind): WeatherMaterial {
  const material = new ShaderMaterial(
    'weather',
    scene,
    { vertexSource: VERTEX, fragmentSource: FRAGMENT },
    {
      attributes: ['position', 'flake'],
      uniforms: [...UNIFORMS],
      needAlphaBlending: true,
    },
  );
  material.backFaceCulling = false;
  material.disableDepthWrite = true;
  const v = kind.volume;
  material.setVector4('volume', new Vector4(v.halfWidth, v.length, v.bottom, v.top));
  material.setColor3('particleColor', new Color3(...kind.color));
  material.setFloat('particleAlpha', kind.alpha);
  const alongFall = kind.align === 'fall';
  material.setFloat('align', alongFall ? 1 : 0);
  const [motion, shape, drift, fogRange] = [
    new Vector4(),
    new Vector4(),
    new Vector2(),
    new Vector2(),
  ];
  const fogColor = new Color3();
  return {
    material,
    set: (frame) => {
      const s = Math.min(1, Math.max(0, frame.strength));
      const wind = kind.wind[0] + (kind.wind[1] - kind.wind[0]) * s;
      motion.set(frame.time, kind.fall[0], kind.fall[1], wind);
      shape.set(kind.size[0], kind.size[1], kind.streak * (alongFall ? 1 : s * s), kind.sway[0]);
      drift.set(frame.start, kind.sway[1]);
      material.setVector4('motion', motion);
      material.setVector4('shape', shape);
      material.setVector2('drift', drift);
      material.setVector3('cameraPosition', frame.cameraPosition);
      material.setVector3('cameraRight', frame.right);
      material.setVector3('cameraUp', frame.up);
      material.setColor3('fogColor', fogColor.set(...frame.fog.color));
      material.setVector2('fogRange', fogRange.set(frame.fog.start, frame.fog.end));
    },
  };
}
