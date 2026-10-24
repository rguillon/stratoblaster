import type { Scene } from '@babylonjs/core/scene';
import type { Mesh } from '@babylonjs/core/Meshes/mesh';
import { TransformNode } from '@babylonjs/core/Meshes/transformNode';
import type { EnemyBullet, EnemyLaser, EnemyMissile } from '../../../core/systems/enemy-shots';
import { SolidBuilder } from '../../../render/geometry/solids';
import type { EnemyShotRenderer } from '../../../render/game-view';
import { NodePool } from '../../../render/node-pool';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { flicker } from '../reactor-flame';
import { buildGlowBar, buildGlowDisc } from '../shot-geometry';
import { additiveTemplate } from '../shots/shot-meshes';
import { enemyMaterials, meshOf } from './enemy-mesh';

const LOOK = ENEMY_LOOK;
type Style = keyof typeof LOOK.bullets.styles;
const STYLES = Object.keys(LOOK.bullets.styles) as Style[];

/** A pool of clones of an additive glow template. */
function glowPool(name: string, template: Mesh): NodePool<Mesh> {
  return new NodePool((i) => template.clone(`${name}-${String(i)}`));
}

/** One pool of glowing balls per bullet colour (GD-43). */
function bulletPools(scene: Scene): { pools: Map<string, NodePool<Mesh>>; templates: Mesh[] } {
  const pools = new Map<string, NodePool<Mesh>>();
  const templates: Mesh[] = [];
  for (const style of STYLES) {
    const disc = buildGlowDisc(LOOK.bullets.segments, LOOK.bullets.styles[style]);
    const template = additiveTemplate(`enemy-bullet-${style}`, disc, scene);
    templates.push(template);
    pools.set(style, glowPool(`enemy-bullet-${style}`, template));
  }
  return { pools, templates };
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

interface LaserPools {
  readonly warning: NodePool<Mesh>;
  readonly beam: NodePool<Mesh>;
  readonly emitter: NodePool<Mesh>;
}

function syncLasers(pools: LaserPools, lasers: readonly EnemyLaser[], time: number): void {
  const look = LOOK.laser;
  const warnings = lasers.filter((l) => l.phase === 'warning');
  const beams = lasers.filter((l) => l.phase === 'firing');
  // The warning line blinks: drawn at full or half width.
  const blink = Math.sin(2 * Math.PI * look.warning.blinkHz * time) > 0 ? 1 : 0.5;
  pools.warning.show(warnings.length).forEach((mesh, i) => {
    const l = warnings[i];
    if (!l) return;
    mesh.position.set(l.x, l.y, -0.8);
    mesh.rotation.z = -l.heading;
    mesh.scaling.set(look.warning.width * blink, l.length, 1);
  });
  const wobble = 1 + look.beam.flicker * flicker(time, 0, [look.beam.flickerHz]);
  pools.beam.show(beams.length).forEach((mesh, i) => {
    const l = beams[i];
    if (!l) return;
    mesh.position.set(l.x, l.y, -0.9);
    mesh.rotation.z = -l.heading;
    mesh.scaling.set(l.spec.width * look.beam.glowWidth * wobble, l.length, 1);
  });
  pools.emitter.show(beams.length).forEach((mesh, i) => {
    const l = beams[i];
    if (!l) return;
    const r = look.emitterRadius * wobble;
    mesh.position.set(l.x, l.y, -1.2);
    mesh.scaling.set(r, r, 1);
  });
}

/**
 * GD-43: the enemies' shots in playfield space: colourful glowing bullets, small red-tipped
 * missiles with a flame, and lasers (a blinking warning line, then a red beam with a glow at
 * the emitter).
 */
export function createEnemyShotRenderer(scene: Scene): EnemyShotRenderer {
  const bullets = bulletPools(scene);
  const flame = additiveTemplate(
    'enemy-missile-flame',
    buildGlowDisc(8, LOOK.missile.flame),
    scene,
  );
  const missiles = new NodePool((i) => buildMissile(scene, flame, i));
  const look = LOOK.laser;
  const templates = [
    additiveTemplate('enemy-laser-warning', buildGlowBar(look.warning.colors), scene),
    additiveTemplate('enemy-laser-beam', buildGlowBar(look.beam.colors), scene),
    additiveTemplate('enemy-laser-emitter', buildGlowDisc(16, look.emitter), scene),
  ] as const;
  const lasers: LaserPools = {
    warning: glowPool('enemy-laser-warning', templates[0]),
    beam: glowPool('enemy-laser-beam', templates[1]),
    emitter: glowPool('enemy-laser-emitter', templates[2]),
  };
  let time = 0;
  return {
    sync: (frame) => {
      time += frame.dtSeconds;
      syncBullets(bullets.pools, frame.bullets);
      syncMissiles(missiles, frame.missiles);
      syncLasers(lasers, frame.lasers, time);
    },
    dispose: () => {
      for (const pool of [...bullets.pools.values(), lasers.warning, lasers.beam, lasers.emitter]) {
        pool.dispose();
      }
      missiles.dispose();
      for (const template of [...bullets.templates, ...templates, flame]) template.dispose();
    },
  };
}
