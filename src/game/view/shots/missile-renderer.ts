import type { Scene } from '@babylonjs/core/scene';
import { NodePool } from '../../../render/node-pool';
import type { ShotRenderer } from '../../../render/game-view';
import { stepModelAnimations } from '../../../render/model-animation';
import { SHOT_LOOK } from '../../config/shot-look';
import { ImpactFlashes } from './impact-flashes';
import { createMissileExhaust } from './missile-exhaust';
import { buildMissile } from './missile-model';

/**
 * P03-R03: missiles turned along their heading, with flames, and explosions on impact. Missiles
 * are drawn behind the ship, which covers them as they leave its centre. Each has a bright motor
 * flare and a glowing exhaust trail, so it shows on any ground (phase 5 review).
 */
export function createMissileRenderer(scene: Scene): ShotRenderer {
  const pool = new NodePool((i) => buildMissile(`missile-${String(i)}`, scene));
  const exhaust = createMissileExhaust(scene);
  const { depth } = SHOT_LOOK.missile;
  const look = SHOT_LOOK.impact.missile;
  const explosions = new ImpactFlashes(
    scene,
    'missile-blast',
    { colors: look.colors, segments: SHOT_LOOK.impact.segments },
    look.duration,
    (impact) => impact.blastRadius * look.radiusFactor,
  );
  return {
    sync: (frame) => {
      const shots = frame.projectiles;
      pool.show(shots.length).forEach((node, i) => {
        const shot = shots[i];
        if (!shot) return;
        node.position.set(shot.x, shot.y, depth);
        node.rotation.z = -shot.heading;
        stepModelAnimations(node, frame.dtSeconds);
      });
      exhaust.sync(shots);
      explosions.sync(frame.impacts, frame.dtSeconds);
    },
    dispose: () => {
      pool.dispose();
      exhaust.dispose();
      explosions.dispose();
    },
  };
}
