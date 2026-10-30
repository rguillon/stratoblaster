import type { Scene } from '@babylonjs/core/scene';
import { Constants } from '@babylonjs/core/Engines/constants';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import type { ModelFactory, ShotRendererFactory } from '../../render/game-view';
import { outlineModel } from '../../render/outline';
import type { SceneryLook } from '../../render/scenery/scenery-look';
import { READABILITY } from '../config/readability';
import { buildGlowDisc } from './shot-geometry';
import { blendedTemplate } from './shots/shot-meshes';

const LOOK = READABILITY;

/** Distance in front of the ship (towards the camera, -Z), so the marker shows over it. */
const MARKER_DEPTH = -6;

/** The player ship models, each with a rim glow in the player colour (P14-R03). */
export function outlinedShips(
  models: Readonly<Record<string, ModelFactory>>,
): Readonly<Record<string, ModelFactory>> {
  return Object.fromEntries(
    Object.entries(models).map(([id, build]) => [
      id,
      (scene: Scene) => {
        const root = build(scene);
        outlineModel(root, LOOK.playerOutline.color);
        return root;
      },
    ]),
  );
}

/**
 * P14-R03: a marker on the ship's hitbox, `radius` its radius: a white dot ringed in the player
 * colour, always drawn over the ship.
 */
export function buildHitboxMarker(scene: Scene, radius: number): TransformNode {
  const { color, rim, segments } = LOOK.hitboxMarker;
  const colors = [color, color, color, rim, rim];
  const alphas = colors.flatMap((_, ring) => Array<number>(ring === 0 ? 1 : segments).fill(1));
  const disc = blendedTemplate('hitbox-marker', buildGlowDisc(segments, colors), alphas, scene);
  const material = disc.material;
  if (material) material.depthFunction = Constants.ALWAYS;
  disc.alphaIndex = Number.MAX_SAFE_INTEGER;
  disc.setEnabled(true);
  const root = new TransformNode('hitbox-marker-root', scene);
  disc.parent = root;
  disc.position.set(0, 0, MARKER_DEPTH);
  disc.scaling.setAll(radius);
  return root;
}

type Rgb = readonly [number, number, number];

/** `value` with every colour (3 numbers) in it times `k`, but under the `skip` keys. */
function scaled<T>(value: T, k: number, skip: RegExp): T {
  if (Array.isArray(value)) {
    if (value.length === 3 && value.every((v) => typeof v === 'number')) {
      return (value as unknown as Rgb).map((v) => v * k) as T;
    }
    return value.map((v: unknown) => scaled(v, k, skip)) as T;
  }
  if (typeof value !== 'object' || value === null) return value;
  return Object.fromEntries(
    Object.entries(value).map(([key, v]) => [key, skip.test(key) ? v : scaled(v, k, skip)]),
  ) as T;
}

/** Colours that are not darkened: tint factors, and lava, which glows by itself. */
const KEEP = /^(tints|lava)$/;

/**
 * P14-R01: `look` with its ground, shores, water and roads darkened to `tone` (0..1) of their
 * colours, and its props, haze and clouds by the engine (`SceneryLook.tone`), so the ships and
 * shots stand out over them. The props' self-lit accents keep their brightness.
 */
export function toned(look: SceneryLook, tone: number): SceneryLook {
  return {
    ...look,
    terrain: scaled(look.terrain, tone, KEEP),
    sea: scaled(look.sea, tone, KEEP),
    roads: scaled(look.roads, tone, KEEP),
    tone,
  };
}

/** `looks`, each {@link toned} to `tone`. */
export function allToned(
  looks: Readonly<Record<string, SceneryLook>>,
  tone: number,
): Readonly<Record<string, SceneryLook>> {
  return Object.fromEntries(Object.entries(looks).map(([id, look]) => [id, toned(look, tone)]));
}

/**
 * P14-R06: the shot renderers, their glows (added on) toned down to `playerShotMaxOpacity`, so
 * they never hide the enemy bullets.
 */
export function tonedShots(
  renderers: Readonly<Record<string, ShotRendererFactory>>,
): Readonly<Record<string, ShotRendererFactory>> {
  return Object.fromEntries(
    Object.entries(renderers).map(([id, create]) => [
      id,
      (scene: Scene) => {
        const before = new Set(scene.materials);
        const renderer = create(scene);
        for (const material of scene.materials) {
          if (!before.has(material) && material.alphaMode === Constants.ALPHA_ADD) {
            material.alpha = Math.min(material.alpha, LOOK.playerShotMaxOpacity);
          }
        }
        return renderer;
      },
    ]),
  );
}
