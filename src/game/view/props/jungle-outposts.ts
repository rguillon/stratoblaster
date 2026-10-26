import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { pane } from './polar-parts';
import { strut, vines } from './jungle-parts';

// P09-R06: the enemy's outposts in the temple ruins of 3-3: gun pits behind mossy stone walls,
// neon gates set in the old stone gateways, antennas on broken towers. Dark metal and neon
// against the old stone. Sizes in world units, standing on Y = 0; the front faces -Z.

type Rgb = readonly [number, number, number];

const VINES: readonly [Rgb, Rgb] = [C.moss, C.mossDark];

/** The ring wall of the gun pit: outer foot, top outside, top inside, inner foot. */
const PIT_WALL = [
  [6.6, 0],
  [6.2, 1.8],
  [5.4, 2],
  [5, 0],
] as const;

/**
 * A gun pit: a round wall of mossy stone blocks, a twin-barrelled turret on a turning base in
 * it aiming up and out, ammunition crates, a cyan neon ring along the wall and a red light.
 */
export function buildGunPit(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  s.lathe(PIT_WALL, 8, C.mossStoneDark, { yaw: 0.2 }, false);
  s.cylinder(2.4, 1.4, 6, C.jungleMetal);
  s.box([3, 2, 3.4], C.metalDark, { at: [0, 1.4, 0.4] });
  for (const x of [-0.6, 0.6]) {
    strut(s, [x, 2.6, -0.8], [x, 5.4, -5.2], [0.28, 0.22], C.metalDark, 4);
  }
  s.box([1.6, 1, 1.2], C.containerGreen, { at: [3, 0, 2.4] });
  s.box([1.6, 1, 1.2], C.containerGreen, { at: [3, 1, 2.4], yaw: 0.3 });
  s.box([0.2, 4, 0.2], C.metalDark, { at: [-2.8, 0, 2.6] });
  l.ring(6.25, 0.3, 8, L.cyan, { at: [0, 1.5, 0], yaw: 0.2 });
  pane(l, [1.6, 0.4], [0, 2.6, -1.36], L.red);
  l.box([0.4, 0.4, 0.4], L.red, { at: [-2.8, 4, 2.6] });
  return { structure: s.geometry, lights: l.geometry };
}

/** Half the width of the gate's opening, between its pillars. */
const GATE_HALF = 3.8;
/** Height of the gate's lintel. */
const GATE_HIGH = 9;

/**
 * A neon gate: an old stone gateway (two square pillars, a heavy lintel, vines) with the enemy's
 * frame of pink neon set inside it and a dim barrier of light across it, a dark metal guard post
 * at its side and fallen blocks.
 */
export function buildNeonGate(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  for (const x of [-GATE_HALF - 1.2, GATE_HALF + 1.2]) {
    s.box([2.4, GATE_HIGH, 2.6], C.mossStone, { at: [x, 0, 0] }, C.moss);
  }
  s.box([2 * GATE_HALF + 5.6, 2, 3.2], C.mossStoneDark, { at: [0, GATE_HIGH, 0] }, C.moss);
  s.box([2 * GATE_HALF + 2, 1, 2.4], C.mossStone, { at: [0, GATE_HIGH + 2, 0] }, C.moss);
  vines(s, [-2.6, GATE_HIGH + 2, -1.65], [3, 3, 3.4], VINES);
  vines(s, [GATE_HALF + 1.2, GATE_HIGH, -1.35], [2, 1.4, 4], VINES);
  for (const x of [-GATE_HALF + 0.2, GATE_HALF - 0.2]) {
    l.box([0.3, GATE_HIGH - 0.3, 0.3], L.pink, { at: [x, 0, -1] });
  }
  l.box([2 * GATE_HALF - 0.1, 0.3, 0.3], L.pink, { at: [0, GATE_HIGH - 0.6, -1] });
  pane(l, [2 * GATE_HALF - 0.6, GATE_HIGH - 0.9], [0, 0, -0.9], L.pinkDim);
  s.box([2.6, 3.2, 2.6], C.metalDark, { at: [6.2, 0, -3.6] });
  pane(l, [1.6, 0.6], [6.2, 2.2, -4.96], L.cyan);
  s.box([2, 1.4, 1.6], C.mossStoneDark, { at: [-6.4, 0, -3.8], yaw: 0.6 }, C.moss);
  return { structure: s.geometry, lights: l.geometry };
}

/** Where the antenna's guy cables are anchored around it (x, z). */
const ANCHORS = [
  [5.6, 2],
  [-4.6, 3.6],
  [-1, -5.8],
] as const;

/**
 * An enemy antenna on a broken temple tower: a stump of mossy stone, a tall dark lattice mast on
 * it with a dish and cross arms, guy cables down to the ground, red lights, a violet neon ring.
 */
export function buildRuinAntenna(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  s.cylinder(3.2, 6.5, 6, C.mossStone, {}, 2.7);
  s.box([2.4, 1.6, 2.4], C.mossStoneDark, { at: [3.8, 0, -2.6], yaw: 0.4 }, C.moss);
  vines(s, [0, 6.5, -2.9], [3, 2.6, 4], VINES);
  s.cylinder(0.8, 17, 4, C.metalDark, { at: [0, 6.5, 0], yaw: Math.PI / 4 }, 0.25);
  for (const y of [13, 18]) s.box([4.4, 0.25, 0.25], C.metalDark, { at: [0, y, 0] });
  s.lathe(
    [
      [0, 0],
      [1.8, 0.7],
    ],
    6,
    C.metal,
    { at: [0, 15, -0.6], pitch: -Math.PI / 2.4 },
    false,
  );
  for (const [x, z] of ANCHORS) strut(s, [x, 0, z], [0, 16, 0], [0.05, 0.05], C.metalDark);
  l.ring(2.75, 0.4, 6, L.violet, { at: [0, 5.6, 0] });
  for (const x of [-2.2, 2.2]) l.box([0.4, 0.4, 0.4], L.red, { at: [x, 18.2, 0] });
  l.box([0.5, 0.5, 0.5], L.red, { at: [0, 23.5, 0] });
  return { structure: s.geometry, lights: l.geometry };
}
