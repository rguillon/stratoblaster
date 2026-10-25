import type { EnemyParts } from '../enemies/enemy-mesh';
import { ENEMY_LOOK } from '../../config/enemy-look';
import { decal } from '../enemies/enemy-shapes';
import { TITAN_WEAR } from './refinery-titan-armour';
import { rect, TITAN_NEON } from './refinery-titan-parts';

// P07-R05 (phase 7 review: details, not all symmetric): the Refinery Titan's lopsided industrial
// kit, a flare stack and a control tower on its left (+X, the screen's left), a crane and a pipe
// rack on its right, clutter on the bridge's roof. Model space: logical pixels, nose +Z, Y up.
const H = ENEMY_LOOK.hull;
const WHITE = [1, 1, 1] as const;
const QUARTER = Math.PI / 2;

type Vec3 = [number, number, number];

/** A flame (lathe profile, bottom to top): rounded, licking up from the flare stack. */
const FLAME = [
  [1.8, 0],
  [3.2, 2.5],
  [2.6, 6],
  [0, 10],
] as const;
/** The flare stack's foot: on the left cradle arm, behind the tank. */
const STACK = { x: 87, z: -33, base: 13, top: 36 } as const;

/** A flare stack burning off gas on the left cradle arm: a tall tapered pipe, a walkway ring. */
function drawFlareStack({ hull, neon, charge }: EnemyParts): void {
  const { x, z, base, top } = STACK;
  hull.cylinder(3.4, 4, 6, H.dark, { at: [x, base, z] }, 2.6);
  hull.cylinder(2.2, top - base - 4, 6, H.panel, { at: [x, base + 4, z] }, 1.5);
  // A walkway ring two thirds up, lit along its edge, and the stack's lit crown.
  hull.cylinder(4.5, 0.8, 8, H.base, { at: [x, base + 13, z] });
  neon.ring(4.6, 0.5, 8, TITAN_NEON, { at: [x, base + 13.2, z] });
  hull.cylinder(2.2, 2, 6, H.dark, { at: [x, top, z] }, 2.4);
  neon.lathe(FLAME, 6, TITAN_NEON, { at: [x, top + 1.6, z] });
  charge.cylinder(1.2, 3, 5, WHITE, { at: [x, top + 1.8, z] }, 0.3);
  // A gas line down from the tank's rear valve to the stack's foot.
  hull.cylinder(1, 14, 6, H.panel, { at: [x - 14, 15, z + 1], roll: -QUARTER });
}

/** The crane's foot on the sponson's right corner, and where its boom reaches over the tank. */
const CRANE = { foot: [-45, 9] as const, reach: [-76, -12] as const, height: 33 } as const;

/** A dock crane on the right of the sponson: a mast, a boom over the tank, a hook hanging. */
function drawCrane({ hull, neon }: EnemyParts): void {
  const [fx, fz] = CRANE.foot;
  const [rx, rz] = CRANE.reach;
  const y = CRANE.height;
  hull.bevelSlab(rect(5, 5, [fx, fz]), [8, 8, 10], [0, 1], H.dark);
  hull.box([2.6, y - 10, 2.6], H.panel, { at: [fx, 10, fz] });
  const [dx, dz] = [rx - fx, rz - fz];
  const length = Math.hypot(dx, dz);
  const yaw = Math.atan2(dx, dz);
  // The boom out to the hook, the counter-jib and its weight the other way.
  hull.box([2.4, 2, length], H.panel, { at: [fx + dx / 2, y, fz + dz / 2], yaw });
  hull.box([2.4, 2, 12], H.panel, { at: [fx - dx * 0.15, y, fz - dz * 0.15], yaw });
  hull.box([4.4, 3.4, 4], H.dark, { at: [fx - dx * 0.24, y - 1, fz - dz * 0.24], yaw });
  decal(neon, rect(0.8, 0.8, [rx, rz]), y + 2.05, TITAN_NEON);
  neon.box([0.7, 0.4, length * 0.8], TITAN_NEON, { at: [fx + dx / 2, y + 2, fz + dz / 2], yaw });
  // The cab at the mast's top, its lit window towards the nose.
  hull.box([4.6, 3.6, 4.6], H.base, { at: [fx, y - 2.4, fz], yaw }, H.panel);
  neon.box([3, 1, 0.3], TITAN_NEON, { at: [fx, y - 1.2, fz + 2.4] });
  // The cable and the hook block, above the tank.
  hull.box([0.5, 5, 0.5], H.dark, { at: [rx, y - 5, rz] });
  hull.box([2.2, 2, 2.2], TITAN_WEAR.hazard, { at: [rx, y - 7, rz] });
}

/** The control tower's cab (lathe profile, bottom to top), the windows going all around. */
const CAB = [
  [3.6, 0],
  [6, 2],
  [6.4, 6],
  [4.6, 7.4],
] as const;
/** The control tower's foot, on the beam left of the hull, between the hull and the tank. */
const TOWER = { x: 44, z: -1, base: 3, cab: 21 } as const;

/** The control tower on the left of the hull: a shaft, a cab ringed with lit windows, a dish. */
function drawControlTower({ hull, neon, charge }: EnemyParts): void {
  const { x, z, base, cab } = TOWER;
  hull.bevelSlab(rect(8, 6, [x, z]), [base, base, cab], [0, 1], H.panel, {}, H.base);
  const at = (y: number): Vec3 => [x, y, z];
  hull.lathe(CAB, 8, H.base, { at: at(cab), yaw: Math.PI / 8 });
  neon.ring(6.3, 1.6, 8, TITAN_NEON, { at: at(cab + 3.2), yaw: Math.PI / 8 });
  // A dish tilted towards the nose, and a mast with a light that charges with the boss.
  hull.cylinder(0.6, 3.6, 6, H.dark, { at: [x + 3, cab + 7.4, z - 2] }, 4);
  hull.cylinder(0.6, 2.2, 6, H.dark, { at: [x - 1.4, cab + 7.4, z + 1.4], pitch: -0.6 }, 3.4);
  hull.cylinder(0.5, 10, 4, H.dark, { at: [x + 2.8, cab + 7.4, z - 2] }, 0.2);
  charge.box([1, 1, 1], WHITE, { at: [x + 2.8, cab + 17, z - 2] });
}

/** The pipe rack along the hull's right flank: three pipes (x, y), from tail to bridge. */
const RACK = [
  [-25, 13],
  [-28.5, 11],
  [-32, 9],
] as const;
const RACK_Z = { from: -48, length: 44 } as const;

/** The pipe rack on the right flank, its brackets, junction boxes where it meets the cross pipes, valves. */
function drawPipeRack({ hull, neon }: EnemyParts): void {
  for (const [x, y] of RACK) {
    hull.cylinder(1.4, RACK_Z.length, 6, H.panel, { at: [x, y, RACK_Z.from], pitch: QUARTER });
  }
  for (const z of [-44, -38, -6]) hull.box([11, 7, 1.8], H.dark, { at: [-28.5, 6, z] });
  for (const z of [-10, -26]) {
    hull.box([11, 6.6, 5], H.base, { at: [-28.5, 6.4, z] }, H.panel);
    decal(neon, rect(7, 0.8, [-28.5, z + 1.4]), 13.05, TITAN_NEON);
  }
  // Hand wheels on the valves, lit.
  for (const z of [-18, -34]) {
    hull.cylinder(0.5, 2.6, 4, H.dark, { at: [-25, 14, z] });
    neon.ring(2, 0.5, 6, TITAN_NEON, { at: [-25, 16.2, z] });
  }
}

/** Clutter on the bridge's roof: a hatch, vents, a radar on the right, an aerial on the left. */
function drawBridgeRoof({ hull, neon, charge }: EnemyParts): void {
  const roof = 24;
  decal(hull, rect(7, 6, [-2, 2]), roof + 0.03, H.dark);
  decal(neon, rect(7, 0.6, [-2, 5.4]), roof + 0.05, TITAN_NEON);
  for (const z of [-6, -8.2]) decal(hull, rect(6, 1, [6, z]), roof + 0.03, H.dark);
  hull.box([4, 2, 3], H.base, { at: [7, roof, 6] }, H.panel);
  // A rotating-radar plinth and its slab on the right.
  hull.cylinder(1.6, 2.4, 6, H.dark, { at: [-8, roof, -6] });
  hull.box([8, 0.8, 1.4], H.panel, { at: [-8, roof + 2.4, -6], yaw: 0.5 });
  // A whip aerial on the left, its tip charging.
  hull.cylinder(0.4, 14, 4, H.dark, { at: [10, roof, -10] }, 0.15);
  charge.box([0.8, 0.8, 0.8], WHITE, { at: [10, roof + 13.6, -10] });
}

/** P07-R05 (phase 7 review): the Refinery Titan's asymmetric kit, all on its core. */
export function drawTitanLandmarks(parts: EnemyParts): void {
  drawFlareStack(parts);
  drawCrane(parts);
  drawControlTower(parts);
  drawPipeRack(parts);
  drawBridgeRoof(parts);
}
