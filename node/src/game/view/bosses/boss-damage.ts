import type { Scene } from '@babylonjs/core/scene';
import { StandardMaterial } from '@babylonjs/core/Materials/standardMaterial';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import { Color3 } from '@babylonjs/core/Maths/math.color';
import type { Enemy } from '../../../core/entities/enemy';
import { createRng } from '../../../core/math/rng';
import { organ, tendril } from '../../../render/geometry/organic';
import { SolidBuilder } from '../../../render/geometry/solids';
import { BOSS_LOOK } from '../../config/boss-look';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { buildEnemyModel, meshOf } from '../enemies/enemy-mesh';

// The damage shown on a boss's parts (P07-R01): its hit flash, its smoke, its wound (P16-R05).

type Vec3 = [number, number, number];

const FLASH_CACHE = new WeakMap<Scene, { flash: StandardMaterial; smoke: StandardMaterial }>();

/** The flash and smoke materials of the scene, created on first use. */
export function effectMaterials(scene: Scene): {
  flash: StandardMaterial;
  smoke: StandardMaterial;
} {
  let mats = FLASH_CACHE.get(scene);
  if (!mats) {
    const flash = new StandardMaterial('boss-flash', scene);
    flash.emissiveColor = new Color3(...BOSS_LOOK.flash.color);
    flash.disableLighting = true;
    const smoke = new StandardMaterial('boss-smoke', scene);
    smoke.emissiveColor = new Color3(...BOSS_LOOK.smoke.color);
    smoke.disableLighting = true;
    smoke.alpha = BOSS_LOOK.smoke.alpha;
    smoke.backFaceCulling = false;
    mats = { flash, smoke };
    FLASH_CACHE.set(scene, mats);
  }
  return mats;
}

/** The smoke rising from a damaged part (P07-R01): a few puffs drifting back and fading. */
export function buildSmoke(name: string, radius: number, scene: Scene, parent: TransformNode) {
  const look = BOSS_LOOK.smoke;
  const node = new TransformNode(`${name}-smoke`, scene);
  node.parent = parent;
  const disc = new SolidBuilder();
  const outline = Array.from({ length: 6 }, (_, k) => {
    const a = (2 * Math.PI * k) / 6;
    return [Math.cos(a) * radius * look.size, Math.sin(a) * radius * look.size] as const;
  });
  disc.slab(outline, [0, 0.1], [1, 1, 1]);
  const puffs = Array.from({ length: look.puffs }, (_, i) => {
    const mesh = meshOf(
      `${name}-puff-${String(i)}`,
      disc.geometry,
      effectMaterials(scene).smoke,
      scene,
    );
    mesh.parent = node;
    return mesh;
  });
  let time = 0;
  return {
    node,
    step(dt: number): void {
      time += dt;
      puffs.forEach((puff, i) => {
        const t = (time / look.seconds + i / puffs.length) % 1;
        puff.position.set(0, look.rise * t + radius, -look.drift * t);
        puff.scaling.setAll(0.6 + t);
        puff.visibility = 1 - t;
      });
    },
  };
}

/**
 * The wound where a destroyed part was (P16-R05, P07-R01): torn flesh around a dimmed organ, a
 * few ribs and shards of plating sticking out, sparks flickering in it.
 */
export function buildStump(name: string, radius: number, scene: Scene, parent: TransformNode) {
  const look = BOSS_LOOK.stump;
  const flesh = ENEMY_LOOK.flesh;
  const node = new TransformNode(`${name}-stump`, scene);
  node.parent = parent;
  const model = buildEnemyModel(name + '-stump', scene, look.spark, (p) => {
    const random = createRng(name.length * 31 + 7);
    const torn = Array.from({ length: 7 }, (_, k): [number, number] => {
      const a = (2 * Math.PI * k) / 7;
      const r = radius * (0.45 + 0.2 * random());
      return [Math.cos(a) * r, Math.sin(a) * r];
    });
    p.flesh.bevelSlab(torn, [0, radius * 0.08, radius * 0.18], [0, radius * 0.12], flesh.wound);
    organ(p.flesh, radius * 0.22, 6, look.organ, { at: [0, radius * 0.05, 0] }, 0.6);
    for (let k = 0; k < 3; k++) {
      const a = (2 * Math.PI * k) / 3 + 0.4;
      const [cx, cz] = [Math.cos(a) * radius * 0.4, Math.sin(a) * radius * 0.4];
      const tip: Vec3 = [cx * 1.5, radius * 0.4, cz * 1.5];
      tendril(p.flesh, [[cx, radius * 0.1, cz], tip], [radius * 0.05, 0], 3, flesh.bone);
      const shard = [
        [-radius * 0.12, 0],
        [radius * 0.12, 0],
        [0, radius * 0.4],
      ] as const;
      p.hull.slab(shard, [0, radius * 0.1], look.char, { yaw: a + 1, at: [0, radius * 0.15, 0] });
    }
    p.charge.cylinder(radius * 0.12, radius * 0.3, 4, [1, 1, 1], {});
  });
  model.root.parent = node;
  const random = createRng(name.length * 7919);
  return {
    node,
    sync(enemy: Enemy, dt: number): void {
      // Sparks flicker at random.
      enemy.charge = random() < look.sparkChance ? 1 : 0;
      model.sync(enemy, dt);
    },
  };
}
