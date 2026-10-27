import type { Scene } from '@babylonjs/core/scene';
import { Constants } from '@babylonjs/core/Engines/constants';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import type { ModelFactory, ShotRendererFactory } from '../../render/game-view';
import { outlineModel } from '../../render/outline';
import type { VeilLook } from '../../render/scenery/background-veil';
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

/** `looks`, each with the background veil `veil` (P14-R01). */
export function withVeil(
  looks: Readonly<Record<string, SceneryLook>>,
  veil: VeilLook,
): Readonly<Record<string, SceneryLook>> {
  return Object.fromEntries(Object.entries(looks).map(([id, look]) => [id, { ...look, veil }]));
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
