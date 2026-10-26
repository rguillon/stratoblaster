import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../render/geometry/outline';
import type { EnemyModel } from '../../../render/game-view';
import { ELITE_CONFIG } from '../../config/enemies-elite';
import { ELITE_NEON } from '../../config/enemy-look-elite';
import { bossPoint } from '../bosses/boss-limbs';
import type { EnemyParts } from './enemy-mesh';
import { ahead, barrel, H, WHITE } from './elite-shapes';
import { buildJointedModel } from './jointed-model';

// P05-R20: the Orbiter. Logical pixels, nose +Z, Y up (towards the camera).
const CFG = ELITE_CONFIG.orbiter;
const NEON = ELITE_NEON.orbiter;

type Drone = (typeof CFG.drones)[number];

/** The core: a sphere squashed a little (it flies low), as a lathe profile, bottom to top. */
const SQUASH = 0.72;
const CORE = [-90, -60, -30, 0, 30, 60, 90].map((deg): [number, number] => {
  const a = (deg * Math.PI) / 180;
  return [CFG.coreRadius * Math.cos(a), CFG.coreRadius * SQUASH * Math.sin(a)];
});
/** A drone around its centre, its nose (+Z) out from the core. */
const DRONE: OutlinePoint[] = [
  [-3.6, -3.4],
  [3.6, -3.4],
  [4.4, 0.8],
  [2, 3.6],
  [-2, 3.6],
  [-4.4, 0.8],
];

/** The core with its glowing equator, the vents around it, and lights at its poles. */
function body({ hull, neon, charge, muzzle }: EnemyParts): void {
  hull.lathe(CORE, 12, H.base);
  // Dark armour bands above and below the equator.
  for (const y of [-5.2, 3.6]) hull.ring(CFG.coreRadius * 0.86, 1.6, 12, H.dark, { at: [0, y, 0] });
  neon.ring(CFG.coreRadius + 0.3, 1.8, 12, NEON, { at: [0, -0.9, 0] });
  // A light on top, brightening as the next ring of bullets comes.
  const pole = [
    [0, 0],
    [3.2, 0.4],
    [0, 1.6],
  ] as const;
  charge.lathe(pole, 8, WHITE, { at: [0, CFG.coreRadius * SQUASH - 0.4, 0] });
  for (const m of CFG.ringMuzzles) muzzle(bossPoint(...m), 'ring');
}

/** A small armoured drone with a gun on its nose and a neon slit. */
function drone(spec: Drone): (p: EnemyParts) => void {
  const at = bossPoint(spec.centre[0], spec.centre[1], 0);
  const yaw = spec.aim;
  const tip = bossPoint(...spec.muzzle);
  return (p) => {
    p.hull.bevelSlab(DRONE, [-2, 0, 2.6], [0.6, 1], H.panel, { at, yaw }, H.base);
    const [x, , z] = ahead(at, yaw, -0.6);
    p.neon.box([4.6, 0.5, 1], NEON, { at: [x, 2.6, z], yaw });
    barrel(p, tip, yaw, [0.8, 2.2]);
  };
}

/** P05-R20: a spherical core with a white-gold equator, three armoured drones orbiting it. */
export function buildOrbiter(scene: Scene): EnemyModel {
  return buildJointedModel('orbiter', scene, NEON, CFG.design, {
    body,
    parts: Object.fromEntries(CFG.drones.map((d) => [d.id, drone(d)])),
  });
}
