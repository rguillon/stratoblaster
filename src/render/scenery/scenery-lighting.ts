import { Scene } from '@babylonjs/core/scene';
import { DirectionalLight } from '@babylonjs/core/Lights/directionalLight';
import { HemisphericLight } from '@babylonjs/core/Lights/hemisphericLight';
import { Color3, Color4 } from '@babylonjs/core/Maths/math.color';
import { Vector3 } from '@babylonjs/core/Maths/math.vector';
import type { Atmosphere } from '../../core/scenery/atmosphere';

const DEG = Math.PI / 180;

/** Direction the sunlight travels, from its elevation and azimuth (0 = from straight ahead). */
export function sunDirection(elevationDeg: number, azimuthDeg: number): Vector3 {
  const el = elevationDeg * DEG;
  const az = azimuthDeg * DEG;
  return new Vector3(-Math.cos(el) * Math.sin(az), -Math.sin(el), -Math.cos(el) * Math.cos(az));
}

/** The lights of a scenery scene: the sun (or the moon) and the sky's ambient light. */
export interface SceneryLights {
  readonly sun: DirectionalLight;
  readonly ambient: HemisphericLight;
}

/** Creates the sun and the ambient light, then lights the scene as `atmosphere` says. */
export function lightScenery(scene: Scene, atmosphere: Atmosphere): SceneryLights {
  scene.fogMode = Scene.FOGMODE_LINEAR;
  scene.clearColor = new Color4(0, 0, 0, 1);
  scene.fogColor = new Color3();
  const ambient = new HemisphericLight('scenery-ambient', Vector3.Up(), scene);
  ambient.specular = Color3.Black();
  const sun = new DirectionalLight('scenery-sun', Vector3.Down(), scene);
  const lights = { sun, ambient };
  applyAtmosphere(scene, lights, atmosphere);
  return lights;
}

/**
 * Lights the scene as `atmosphere` says (P08-R04): haze (clear colour and linear fog), sky and
 * ground ambient light, and the sun's direction, colour and strength. Called every frame.
 */
export function applyAtmosphere(scene: Scene, lights: SceneryLights, atmosphere: Atmosphere): void {
  const [r, g, b] = atmosphere.sky.haze;
  scene.clearColor.set(r, g, b, 1);
  scene.fogColor.set(r, g, b);
  scene.fogStart = atmosphere.fog.start;
  scene.fogEnd = atmosphere.fog.end;
  const { ambient, sun } = lights;
  ambient.diffuse.set(...atmosphere.ambient.sky);
  ambient.groundColor.set(...atmosphere.ambient.ground);
  ambient.intensity = atmosphere.ambient.intensity;
  const s = atmosphere.sun;
  sun.direction = sunDirection(s.elevationDeg, s.azimuthDeg);
  sun.diffuse.set(...s.color);
  sun.specular.set(...s.color);
  sun.intensity = s.intensity;
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
