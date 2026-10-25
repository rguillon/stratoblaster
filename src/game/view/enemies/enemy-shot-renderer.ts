import type { Scene } from '@babylonjs/core/scene';
import type { Mesh } from '@babylonjs/core/Meshes/mesh';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import type { EnemyBullet, EnemyMissile } from '../../../core/systems/enemy-shots';
import { SolidBuilder } from '../../../render/geometry/solids';
import type { EnemyShotRenderer } from '../../../render/game-view';
import { NodePool } from '../../../render/node-pool';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { buildGlowDisc } from '../shot-geometry';
import { additiveTemplate, blendedTemplate } from '../shots/shot-meshes';
import { enemyMaterials, meshOf } from './enemy-mesh';
import { EnemyLasers } from './enemy-lasers';

const LOOK = ENEMY_LOOK;
type Style = keyof typeof LOOK.bullets.styles;
const STYLES = Object.keys(LOOK.bullets.styles) as Style[];

/** A pool of clones of an additive glow template. */
function glowPool(name: string, template: Mesh): NodePool<Mesh> {
  return new NodePool((i) => template.clone(`${name}-${String(i)}`));
}

/** Opacity of each vertex of a bullet's disc: its centre, then each ring's. */
function discAlphas(segments: number, fade: readonly number[]): number[] {
  return fade.flatMap((alpha, ring) => Array<number>(ring === 0 ? 1 : segments).fill(alpha));
}

/** One pool of blobs of energy per bullet colour (GD-43). */
function bulletPools(scene: Scene): { pools: Map<string, NodePool<Mesh>>; templates: Mesh[] } {
  const pools = new Map<string, NodePool<Mesh>>();
  const templates: Mesh[] = [];
  for (const style of STYLES) {
    const { segments, fade } = LOOK.bullets;
    const disc = buildGlowDisc(segments, LOOK.bullets.styles[style]);
    const alphas = discAlphas(segments, fade);
    const template = blendedTemplate(`enemy-bullet-${style}`, disc, alphas, scene);
    // The pulsing white-hot core, added over the blob; its clones get one too.
    const color = LOOK.bullets.styles[style][2] ?? [1, 1, 1];
    const glow = buildGlowDisc(segments, [[1, 1, 1], [1, 1, 1], color, [0, 0, 0]]);
    const core = additiveTemplate(`enemy-bullet-${style}-core`, glow, scene);
    core.parent = template;
    core.position.z = -0.2;
    core.setEnabled(true);
    templates.push(template);
    pools.set(style, glowPool(`enemy-bullet-${style}`, template));
  }
  return { pools, templates };
}

/** Size of a bullet's core, relative to the bullet, `age` seconds after it was fired. */
function coreScale(age: number): number {
  const { size, pulse } = LOOK.bullets.core;
  return size * (1 + pulse.amount * Math.sin(2 * Math.PI * pulse.hz * age));
}

function syncBullets(pools: Map<string, NodePool<Mesh>>, bullets: readonly EnemyBullet[]): void {
  for (const [style, pool] of pools) {
    const own = bullets.filter((b) => (pools.has(b.style) ? b.style : STYLES[0]) === style);
    pool.show(own.length).forEach((mesh, i) => {
      const b = own[i];
      if (!b) return;
      const r = b.radius * LOOK.bullets.scale;
      mesh.position.set(b.x, b.y, -1);
      mesh.scaling.set(r, r, 1);
      const core = mesh.getChildren()[0] as Mesh | undefined;
      core?.scaling.setAll(coreScale(b.age));
    });
  }
}

/** A small dark missile pointing +Y with a red tip and a flame behind it. */
function buildMissile(scene: Scene, flame: Mesh, i: number): TransformNode {
  const look = LOOK.missile;
  const root = new TransformNode(`enemy-missile-${String(i)}`, scene);
  const body = new SolidBuilder().cylinder(look.radius, look.length, 6, LOOK.hull.panel, {
    at: [0, -look.length / 2, 0],
  });
  const tip = new SolidBuilder().cylinder(
    look.radius,
    3,
    6,
    look.tip,
    { at: [0, look.length / 2, 0] },
    0,
  );
  const mats = enemyMaterials(scene);
  meshOf(`${root.name}-body`, body.geometry, mats.hull, scene).parent = root;
  meshOf(`${root.name}-tip`, tip.geometry, mats.neon, scene).parent = root;
  const glow = flame.clone(`${root.name}-flame`);
  glow.parent = root;
  glow.setEnabled(true);
  const [w, h] = look.flameSize;
  glow.position.set(0, -look.length / 2 - h * 0.6, 0.5);
  glow.scaling.set(w, h, 1);
  return root;
}

function syncMissiles(pool: NodePool<TransformNode>, missiles: readonly EnemyMissile[]): void {
  pool.show(missiles.length).forEach((node, i) => {
    const m = missiles[i];
    if (!m) return;
    node.position.set(m.x, m.y, -0.5);
    node.rotation.z = -m.heading;
  });
}

/**
 * GD-43: the enemies' shots in playfield space: colourful glowing bullets, small red-tipped
 * missiles with a flame, and lasers ({@link EnemyLasers}).
 */
export function createEnemyShotRenderer(scene: Scene): EnemyShotRenderer {
  const bullets = bulletPools(scene);
  const flame = additiveTemplate(
    'enemy-missile-flame',
    buildGlowDisc(8, LOOK.missile.flame),
    scene,
  );
  const missiles = new NodePool((i) => buildMissile(scene, flame, i));
  const lasers = new EnemyLasers(scene);
  let time = 0;
  return {
    sync: (frame) => {
      time += frame.dtSeconds;
      syncBullets(bullets.pools, frame.bullets);
      syncMissiles(missiles, frame.missiles);
      lasers.sync(frame.lasers, time);
    },
    dispose: () => {
      for (const pool of bullets.pools.values()) pool.dispose();
      lasers.dispose();
      missiles.dispose();
      for (const template of [...bullets.templates, flame]) template.dispose();
    },
  };
}
