import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { corners, pane, posts } from './polar-parts';
import { gableRoof, strut } from './jungle-parts';

// P09-R06: the enemy's swamp works of 3-4: bio-labs on stilts with glowing toxic tanks, the
// pipeline on stilts across the swamp, pumping stations, and the dam's power plant. Rusty and
// dark metal, white lab panels, toxic green lights. Sizes in world units, standing on Y = 0;
// the front faces -Z.

/** Height of the bio-lab's deck on its stilts. */
const LAB_DECK = 3;
/** The bio-lab's glowing tanks: (x, z), radius and height. */
const LAB_TANKS = [
  [-5, -3.4, 1.5, 5],
  [-1.4, -3.6, 1.3, 4.2],
  [5.2, 3.2, 1.6, 5.6],
] as const;

/**
 * A bio-lab on stilts over the swamp: a white lab module on a metal deck, three tanks of glowing
 * toxic green with dark caps, a vent stack, a pipe down into the water, lit cyan windows and a
 * red light.
 */
export function buildBioLab(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  posts(s, [...corners(7, 5), [0, -5], [0, 5]], LAB_DECK, C.jungleMetal, 0.6);
  s.box([16, 0.5, 12], C.metalDark, { at: [0, LAB_DECK, 0] });
  s.box([10, 4.4, 5.6], C.white, { at: [1, LAB_DECK + 0.5, 1.6] }, C.panel);
  s.box([4, 1.4, 3], C.panelDark, { at: [3, LAB_DECK + 4.9, 1.6] });
  for (const [x, z, r, h] of LAB_TANKS) {
    l.cylinder(r, h, 6, L.toxic, { at: [x, LAB_DECK + 0.5, z] });
    s.cylinder(r + 0.15, 0.6, 6, C.metalDark, { at: [x, LAB_DECK + 0.5 + h, z] });
  }
  s.cylinder(0.5, 6.5, 5, C.rust, { at: [-4.4, LAB_DECK + 0.5, 3.6] });
  strut(s, [6.4, LAB_DECK + 2, -1.6], [7.2, 0, -4.2], [0.45, 0.45], C.rust, 4);
  for (const x of [-1.5, 2.5]) pane(l, [2.4, 1], [x, LAB_DECK + 2.4, -1.26], L.cyan);
  l.box([0.5, 0.5, 0.5], L.red, { at: [-4.4, LAB_DECK + 7, 3.6] });
  return { structure: s.geometry, lights: l.geometry };
}

/** Length of a pipeline piece along X: pieces are laid end to end every 15. */
const PIPE_LENGTH = 15;
const PIPE_RADIUS = 0.9;
const PIPE_HEIGHT = 2.8;

/**
 * A piece of the swamp pipeline on stilts, exactly 15 long along X (x = -7.5 to 7.5): a rusty
 * pipe about 3 high on two braced stilts standing in the water or on the ground, a joint collar
 * and a toxic green leak light at the valve.
 */
export function buildSwampPipeline(): PropGeometry {
  const s = new SolidBuilder();
  const l = new SolidBuilder();
  const half = PIPE_LENGTH / 2;
  s.cylinder(PIPE_RADIUS, PIPE_LENGTH, 6, C.rustDark, {
    at: [-half, PIPE_HEIGHT, 0],
    roll: -Math.PI / 2,
  });
  s.cylinder(PIPE_RADIUS + 0.2, 0.8, 6, C.jungleMetal, {
    at: [half - 0.8, PIPE_HEIGHT, 0],
    roll: -Math.PI / 2,
  });
  for (const x of [-half / 2, half / 2]) {
    for (const z of [-1, 1]) {
      strut(s, [x, 0, z * 1.5], [x, PIPE_HEIGHT - 0.4, z * 0.4], [0.25, 0.2], C.metalDark, 4);
    }
    s.box([0.45, 0.5, 2], C.metalDark, { at: [x, PIPE_HEIGHT - 1.05, 0] });
  }
  s.box([0.8, 0.9, 0.8], C.metalDark, { at: [0, PIPE_HEIGHT + 0.7, 0] });
  l.box([0.5, 0.3, 0.5], L.toxic, { at: [0, PIPE_HEIGHT + 1.6, 0] });
  return { structure: s.geometry, lights: l.geometry };
}

/**
 * A pumping station: a concrete pump house under a corrugated roof, two big rusty intake pipes
 * plunging into the swamp, a settling tank, a roof fan, lit toxic green windows and a red light.
 */
export function buildPumpingStation(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  s.box([10, 6, 8], C.concreteDark, { at: [-1, 0, 1] });
  gableRoof(s, { size: [10.8, 8.8], y: 6, rise: 1.8 }, C.corrugated, C.concreteDark, {
    at: [-1, 0, 1],
  });
  for (const x of [-4, 1]) {
    strut(s, [x, 4, -3], [x, 4, -6], [0.8, 0.8], C.rust, 6);
    strut(s, [x, 4, -6], [x, 0.3, -8.2], [0.8, 0.8], C.rust, 6);
  }
  s.cylinder(2.6, 4.4, 8, C.jungleMetal, { at: [6.6, 0, 2.4] });
  s.cylinder(1.4, 0.6, 6, C.metalDark, { at: [-2.6, 6.9, 2] });
  for (const x of [-4.6, -1, 2.6]) pane(l, [1.8, 1.2], [x, 3.2, -3.06], L.toxicDim);
  l.ring(2.65, 0.4, 8, L.toxic, { at: [6.6, 3.2, 2.4] });
  s.box([0.2, 3.4, 0.2], C.metalDark, { at: [3.4, 6, 4.4] });
  l.box([0.5, 0.5, 0.5], L.red, { at: [3.4, 9.4, 4.4] });
  return { structure: s.geometry, lights: l.geometry };
}

/** A transmission pylon at (x, z): a tapering lattice mast with two cross arms, red-lit. */
function pylon(s: SolidBuilder, l: SolidBuilder, [x, z]: readonly [number, number]): void {
  s.cylinder(1.4, 18, 4, C.jungleMetal, { at: [x, 0, z], yaw: Math.PI / 4 }, 0.4);
  for (const y of [12, 16]) s.box([7, 0.4, 0.5], C.jungleMetal, { at: [x, y, z] });
  l.box([0.6, 0.6, 0.6], L.red, { at: [x, 18, z] });
}

/**
 * The dam's power plant: a long turbine hall under a shallow roof, three penstocks coming down
 * the slope behind it from the lake, a transformer yard and two pylons, rows of lit windows, a
 * cyan neon band and red lights.
 */
export function buildDamPowerPlant(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  s.box([24, 9, 11], C.damConcrete, { at: [-2, 0, -2] }, C.concreteDark);
  gableRoof(s, { size: [24.6, 11.6], y: 9, rise: 1.6 }, C.metalDark, C.damConcrete, {
    at: [-2, 0, -2],
  });
  for (const x of [-9, -2, 5]) {
    strut(s, [x, 6, 3.4], [x, 14, 13], [1.3, 1.3], C.rust, 6);
  }
  s.box([10, 0.4, 6], C.concrete, { at: [-6, 0, -10.5] });
  for (const x of [-9, -5.5, -2]) s.box([2.2, 3, 2.4], C.metal, { at: [x, 0.4, -10.5] });
  pylon(s, l, [7, -12]);
  pylon(s, l, [12, 2]);
  for (let x = -11; x <= 6; x += 4.25) pane(l, [2.4, 2.4], [x, 3.4, -7.56], L.window);
  l.box([24.4, 0.4, 0.4], L.cyan, { at: [-2, 8, -7.75] });
  return { structure: s.geometry, lights: l.geometry };
}
