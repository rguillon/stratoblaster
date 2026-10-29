import type { Scene } from '@babylonjs/core/scene';
import type { OutlinePoint } from '../../../render/geometry/outline';
import type { EnemyModel } from '../../../render/game-view';
import type { SegmentedBody } from '../../../render/geometry/organic';
import { curve, segmentedBody, vein as veinTube } from '../../../render/geometry/organic';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { ELITE_CONFIG } from '../../config/enemies-elite';
import { ELITE_NEON } from '../../config/enemy-look-elite';
import { bossPoint } from '../bosses/boss-limbs';
import type { EnemyParts } from './enemy-mesh';
import { ahead, barrel, H, WHITE } from './elite-shapes';
import { buildJointedModel } from './jointed-model';

// P05-R20, P16-R04: the Orbiter. Logical pixels, nose +Z, Y up (towards the camera).
const CFG = ELITE_CONFIG.orbiter;
const NEON = ELITE_NEON.orbiter;
const F = ENEMY_LOOK.flesh;

type Drone = (typeof CFG.drones)[number];

/** The core: a sphere squashed a little (it flies low), as a lathe profile, bottom to top. */
const SQUASH = 0.72;
const CORE = [-90, -60, -30, 0, 30, 60, 90].map((deg): [number, number] => {
  const a = (deg * Math.PI) / 180;
  return [CFG.coreRadius * Math.cos(a), CFG.coreRadius * SQUASH * Math.sin(a)];
});
/** A drone's flesh pod around its centre, along +Z, under its shell. */
const POD: SegmentedBody = {
  tail: -3.6,
  nose: 3.4,
  segments: 2,
  width: 3.8,
  bottom: -1.8,
  top: 1.4,
};
/** A drone's armour shell around its centre, its nose (+Z) out from the core. */
const DRONE: OutlinePoint[] = [
  [-3.6, -3.4],
  [3.6, -3.4],
  [4.4, 0.8],
  [2, 3.6],
  [-2, 3.6],
  [-4.4, 0.8],
];

/** The core: a flesh heart in metal bands, its glowing equator, veins and its pole light. */
function body({ hull, flesh, neon, vein, charge, muzzle }: EnemyParts): void {
  flesh.lathe(CORE, 12, F.purple);
  // P16-R04: armour bands above and below the equator, metal grafted on the heart.
  for (const y of [-5.2, 3.6]) hull.ring(CFG.coreRadius * 0.86, 1.6, 12, H.dark, { at: [0, y, 0] });
  neon.ring(CFG.coreRadius + 0.3, 1.8, 12, NEON, { at: [0, -0.9, 0] });
  // Veins over its top, from the pole down to the upper band.
  const top = CFG.coreRadius * SQUASH;
  for (const a of [0, 1, 2, 3].map((k) => (k * Math.PI) / 2 + Math.PI / 4)) {
    const out = (r: number, y: number) => [Math.sin(a) * r, y, Math.cos(a) * r] as const;
    veinTube(
      vein,
      curve(out(2.5, top), out(CFG.coreRadius * 0.82, 5.2), [0, 1.5, 0], 2),
      0.9,
      NEON,
    );
  }
  // A light on top, brightening as the next ring of bullets comes.
  const pole = [
    [0, 0],
    [3.2, 0.4],
    [0, 1.6],
  ] as const;
  charge.lathe(pole, 8, WHITE, { at: [0, top - 0.4, 0] });
  for (const m of CFG.ringMuzzles) muzzle(bossPoint(...m), 'ring');
}

/** A drone: a flesh pod under a metal shell, an eye slit and a gun on its nose. */
function drone(spec: Drone): (p: EnemyParts) => void {
  const at = bossPoint(spec.centre[0], spec.centre[1], 0);
  const yaw = spec.aim;
  const tip = bossPoint(...spec.muzzle);
  return (p) => {
    segmentedBody(p.flesh, POD, F.crimson, { at, yaw });
    p.hull.bevelSlab(DRONE, [0.6, 1.2, 2.6], [0.2, 1], H.panel, { at, yaw }, H.base);
    const [x, , z] = ahead(at, yaw, -0.6);
    p.neon.box([4.6, 0.5, 1], NEON, { at: [x, 2.6, z], yaw });
    // A gland at its back, pulsing.
    const [gx, , gz] = ahead(at, yaw, -3.2);
    p.vein.box([1.4, 0.6, 1.2], NEON, { at: [gx, 1.6, gz], yaw });
    barrel(p, tip, yaw, [0.8, 2.2]);
  };
}

/**
 * P05-R20, P16-R04: a flesh heart in armour bands with a white-gold equator, three armoured
 * drone pods orbiting it.
 */
export function buildOrbiter(scene: Scene): EnemyModel {
  return buildJointedModel('orbiter', scene, NEON, CFG.design, {
    body,
    parts: Object.fromEntries(CFG.drones.map((d) => [d.id, drone(d)])),
  });
}
