import type { Scene } from '@babylonjs/core/scene';
import type { Projectile } from '../../../core/systems/projectile-motion';
import { NodePool } from '../../../render/node-pool';
import { SHOT_LOOK } from '../../config/shot-look';
import { PLAYER_SHIP_SCALE } from '../../config/ship-look';
import { buildGlowDisc, buildTracer } from '../shot-geometry';
import { additiveTemplate } from './shot-meshes';

const { flare, trail, depth, length } = SHOT_LOOK.missile;
// From the missile's centre back to its nozzle, px.
const BACK = (length / 2) * PLAYER_SHIP_SCALE;

/**
 * Phase 5 review: a bright, flickering motor flare at each missile's nozzle and a glowing
 * exhaust trail behind it, added on, so the missiles show on any ground.
 */
export function createMissileExhaust(scene: Scene): {
  sync: (shots: readonly Projectile[]) => void;
  dispose: () => void;
} {
  const flareTemplate = additiveTemplate(
    'missile-flare',
    buildGlowDisc(flare.segments, flare.colors),
    scene,
  );
  const flares = new NodePool((i) => flareTemplate.clone(`missile-flare-${String(i)}`));
  const trailTemplate = additiveTemplate(
    'missile-trail',
    buildTracer(trail.colors, trail.rows),
    scene,
  );
  const trails = new NodePool((i) => trailTemplate.clone(`missile-trail-${String(i)}`));
  return {
    sync: (shots) => {
      const meshes = flares.show(shots.length);
      trails.show(shots.length).forEach((mesh, i) => {
        const [shot, glow] = [shots[i], meshes[i]];
        if (!shot || !glow) return;
        const x = shot.x - Math.sin(shot.heading) * BACK;
        const y = shot.y - Math.cos(shot.heading) * BACK;
        const size = flare.radius * (1 + flare.flicker * Math.sin(shot.age * flare.flickerRate));
        glow.position.set(x, y, depth);
        glow.scaling.set(size, size, 1);
        mesh.position.set(x, y, depth);
        mesh.rotation.z = -shot.heading;
        // Grows from the launch point, like a tracer.
        mesh.scaling.set(trail.width, Math.min(trail.length, shot.age * shot.speed), 1);
      });
    },
    dispose: () => {
      flares.dispose();
      trails.dispose();
      flareTemplate.dispose();
      trailTemplate.dispose();
    },
  };
}
