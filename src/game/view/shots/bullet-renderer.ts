import type { Scene } from '@babylonjs/core/scene';
import { createRng } from '../../../core/math/rng';
import { NodePool } from '../../../render/node-pool';
import type { ShotRenderer } from '../../../render/game-view';
import { SHOT_LOOK } from '../../config/shot-look';
import { buildGlowDisc } from '../shot-geometry';
import { additiveTemplate } from './shot-meshes';
import { SparkBursts } from './spark-bursts';

/**
 * P03-R01: neon green blobs with fading edges, stretched along their direction of travel, and a
 * burst of sparkling metal sparks where they hit (phase 3 review).
 */
export function createBulletRenderer(scene: Scene): ShotRenderer {
  const look = SHOT_LOOK.bullet;
  const template = additiveTemplate('bullet', buildGlowDisc(look.segments, look.colors), scene);
  const pool = new NodePool((i) => template.clone(`bullet-${String(i)}`));
  const sparkLook = SHOT_LOOK.impact.bullet;
  const sparkTemplate = additiveTemplate(
    'bullet-spark',
    buildGlowDisc(sparkLook.segments, sparkLook.colors),
    scene,
  );
  const sparkPool = new NodePool((i) => sparkTemplate.clone(`bullet-spark-${String(i)}`));
  const sparks = new SparkBursts(sparkLook, createRng(sparkLook.seed));
  return {
    sync: (frame) => {
      pool.show(frame.projectiles.length).forEach((mesh, i) => {
        const shot = frame.projectiles[i];
        if (!shot) return;
        mesh.position.set(shot.x, shot.y, 0);
        mesh.rotation.z = -shot.heading;
        mesh.scaling.set(look.radius, look.radius * look.stretch, 1);
      });
      for (const impact of frame.impacts) sparks.emit(impact.x, impact.y);
      const spots = sparks.step(frame.dtSeconds);
      sparkPool.show(spots.length).forEach((mesh, i) => {
        const spark = spots[i];
        if (!spark) return;
        // Additive: a dimmer, thinner streak reads as a fading spark.
        const width = sparkLook.width * spark.brightness;
        mesh.position.set(spark.x, spark.y, -1);
        mesh.rotation.z = -spark.heading;
        mesh.scaling.set(width, Math.max(width, spark.length / 2), 1);
      });
    },
    dispose: () => {
      pool.dispose();
      sparkPool.dispose();
      template.dispose();
      sparkTemplate.dispose();
    },
  };
}
