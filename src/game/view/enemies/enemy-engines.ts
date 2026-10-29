import type { Material } from '@babylonjs/core/Materials/material';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import { SolidBuilder } from '../../../render/geometry/solids';
import { addModelAnimation } from '../../../render/model-animation';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { buildReactorFlame } from '../reactor-flame';
import { enemyColor, flameMaterials, meshOf } from './enemy-materials';
import type { EnemyParts } from './enemy-mesh';

// The reactors and rotors of the enemy models (phase 5 review).

type Vec3 = readonly [number, number, number];

/** A reactor or a rotor: where, and how big. */
export interface Reactor {
  readonly at: Vec3;
  readonly radius: number;
}

/** The rotors' blades and hubs, each on a node spun by a model animation. */
export function addRotors(
  name: string,
  rotors: readonly Reactor[],
  material: Material,
  root: TransformNode,
): void {
  const look = ENEMY_LOOK.rotor;
  const scene = root.getScene();
  rotors.forEach(({ at: [x, y, z], radius }, i) => {
    const parts = new SolidBuilder();
    const blade = [
      [-0.12, 0.3],
      [0.12, 0.3],
      [0.22, 0.92],
      [-0.08, 0.95],
    ] as const;
    for (let k = 0; k < look.blades; k++) {
      const outline = blade.map(([u, v]) => [u * radius, v * radius] as const);
      parts.slab(outline, [-0.08, 0.08], ENEMY_LOOK.hull.panel, {
        yaw: (2 * Math.PI * k) / look.blades,
      });
    }
    parts.cylinder(radius * look.hub, radius * 0.3, 4, ENEMY_LOOK.hull.dark, {
      at: [0, -radius * 0.15, 0],
    });
    const node = new TransformNode(`${name}-rotor-${String(i)}`, scene);
    node.position.set(x, y, z);
    node.parent = root;
    meshOf(`${node.name}-blades`, parts.geometry, material, scene).parent = node;
    addModelAnimation(node, (dt) => {
      node.rotation.y += look.spinRadPerSec * dt;
    });
  });
}

/** Nozzles in the hull, cores in the neon, and an animated flame per reactor under `root`. */
export function addReactors(
  name: string,
  reactors: readonly Reactor[],
  parts: EnemyParts,
  root: TransformNode,
): void {
  const look = ENEMY_LOOK.reactor;
  const color = enemyColor(look.color);
  const behind = -Math.PI / 2;
  reactors.forEach(({ at: [x, y, z], radius }, i) => {
    const depth = radius * look.depth;
    // Pitched back, a band standing on `at` runs towards -Z: an open nozzle (no caps), with a
    // flat neon core across its mouth, facing back.
    const place = { at: [x, y, z + depth] as Vec3, pitch: behind };
    parts.hull.ring(radius, depth, look.sides, ENEMY_LOOK.hull.dark, place);
    const core = Array.from({ length: look.sides }, (_, k): Vec3 => {
      // Counter-clockwise seen from behind (-Z), so the face points back, out of the nozzle.
      const a = (-2 * Math.PI * k) / look.sides;
      return [x + Math.cos(a) * radius * look.core, y + Math.sin(a) * radius * look.core, z];
    });
    // Folded with the rest of the neon (`inEnemyFamily`): the colour of the flame.
    parts.neon.face(core, look.color);
    const node = new TransformNode(`${name}-reactor-${String(i)}`, root.getScene());
    node.position.set(x, y, 0);
    node.parent = root;
    buildReactorFlame(
      node.name,
      {
        nozzleZ: z - 0.05,
        length: radius * look.flameLength,
        diameter: radius * 2 * look.core * look.flameWidth,
        puffDiameter: radius * look.puffSize,
        sides: look.flameSides,
        light: { puffs: look.puffs },
      },
      node,
      flameMaterials(root.getScene(), color),
    );
  });
}
