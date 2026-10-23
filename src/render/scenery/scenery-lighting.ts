import { Scene } from '@babylonjs/core/scene';
import { DirectionalLight } from '@babylonjs/core/Lights/directionalLight';
import { HemisphericLight } from '@babylonjs/core/Lights/hemisphericLight';
import { Color3, Color4 } from '@babylonjs/core/Maths/math.color';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';
import type { SceneryLook } from './scenery-look';

const DEG = Math.PI / 180;

/** Direction the sunlight travels, from its elevation and azimuth (0 = from straight ahead). */
export function sunDirection(elevationDeg: number, azimuthDeg: number): Vector3 {
  const el = elevationDeg * DEG;
  const az = azimuthDeg * DEG;
  return new Vector3(-Math.cos(el) * Math.sin(az), -Math.sin(el), -Math.cos(el) * Math.cos(az));
}

/** Haze (clear colour and linear fog), sky / ground ambient light and the sun. Returns the sun. */
export function lightScenery(scene: Scene, look: SceneryLook): DirectionalLight {
  const [r, g, b] = look.sky.haze;
  scene.clearColor = new Color4(r, g, b, 1);
  scene.fogMode = Scene.FOGMODE_LINEAR;
  scene.fogColor = new Color3(r, g, b);
  scene.fogStart = look.fog.start;
  scene.fogEnd = look.fog.end;
  const ambient = new HemisphericLight('scenery-ambient', Vector3.Up(), scene);
  ambient.diffuse = new Color3(...look.ambient.sky);
  ambient.groundColor = new Color3(...look.ambient.ground);
  ambient.specular = Color3.Black();
  ambient.intensity = look.ambient.intensity;
  const { sun: s } = look;
  const sun = new DirectionalLight(
    'scenery-sun',
    sunDirection(s.elevationDeg, s.azimuthDeg),
    scene,
  );
  sun.diffuse = new Color3(...s.color);
  sun.specular = new Color3(...s.color);
  sun.intensity = s.intensity;
  return sun;
}

/**
 * Where to put a directional light of direction `direction` that looks at `target` from
 * `distance` away, with `target` moved to the nearest whole shadow texel (`texel` world units)
 * across the light: the shadow map then slides by whole texels as the view scrolls, and the
 * shadows stay still instead of shimmering (phase 4 review).
 */
export function snappedLightPosition(
  direction: Vector3,
  target: Vector3,
  distance: number,
  texel: number,
): Vector3 {
  const forward = direction.normalizeToNew();
  const right = Vector3.Cross(Vector3.Up(), forward).normalize();
  const up = Vector3.Cross(forward, right);
  const snap = (axis: Vector3): Vector3 => {
    const along = Vector3.Dot(target, axis);
    return axis.scale(Math.round(along / texel) * texel - along);
  };
  const snapped = target.add(snap(right)).add(snap(up));
  return snapped.subtract(forward.scale(distance));
}
