import type { Scene } from '@babylonjs/core/scene';
import type { Mesh } from '@babylonjs/core/Meshes/mesh';
import { createRng } from '../../../core/math/rng';
import type { BlastRenderer } from '../../../render/game-view';
import { NodePool } from '../../../render/node-pool';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { buildGlowDisc } from '../shot-geometry';
import { additiveTemplate } from '../shots/shot-meshes';
import { BlastParticles, type BlastSpot } from './blast-particles';

const LOOK = ENEMY_LOOK.blasts;

function place(pool: NodePool<Mesh>, spots: readonly BlastSpot[], z: number): void {
  pool.show(spots.length).forEach((mesh, i) => {
    const spot = spots[i];
    if (!spot) return;
    mesh.position.set(spot.x, spot.y, z);
    mesh.scaling.set(spot.radius, spot.radius, 1);
  });
}

/** GD-62: explosions where enemies and missiles were destroyed, in playfield space. */
export function createBlastRenderer(scene: Scene): BlastRenderer {
  const fire = additiveTemplate(
    'blast-fireball',
    buildGlowDisc(LOOK.fireball.segments, LOOK.fireball.colors),
    scene,
  );
  const spark = additiveTemplate(
    'blast-debris',
    buildGlowDisc(LOOK.debris.segments, LOOK.debris.colors),
    scene,
  );
  const fireballs = new NodePool((i) => fire.clone(`blast-fireball-${String(i)}`));
  const debris = new NodePool((i) => spark.clone(`blast-debris-${String(i)}`));
  const particles = new BlastParticles(createRng(LOOK.seed));
  return {
    sync: (blasts, dt) => {
      for (const blast of blasts) particles.emit(blast);
      const spots = particles.step(dt);
      // In front of the ships (towards the camera, -Z).
      place(fireballs, spots.fireballs, -3);
      place(debris, spots.debris, -3.5);
    },
    dispose: () => {
      fireballs.dispose();
      debris.dispose();
      fire.dispose();
      spark.dispose();
    },
  };
}
