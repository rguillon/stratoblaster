import { SolidBuilder } from '../../../render/geometry/solids';
import type { OutlinePoint } from '../../../render/geometry/outline';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { pane } from './polar-parts';
import { hipRoof } from './jungle-parts';

// P09-R06: the giant dam across the end of 3-4's lake, a set piece: X from -235 to 235, Z from
// -18 to 18, its crest 32 above the water (Y = 0), its downstream face towards -Z (the camera
// looks towards +Z) with a spillway of five gates in the middle and white water pouring down from
// them, buttresses, and lights along the crest. Within 600 triangles.

type Rgb = readonly [number, number, number];

/** Half the dam's width along X, without the rocks at its ends. */
const DAM_HALF = 226;
/** Height of the crest above the water, and the crest's span along Z. */
const CREST = 30;
const CREST_Z = [4, 16] as const;
/** Where the downstream face meets the water. */
const FOOT_Z = -14;
/** The spillway's gates: their centres along X, their width. */
const GATES = [-48, -24, 0, 24, 48] as const;
const GATE_W = 18;
/** Buttresses on the downstream face, outside the spillway: their X. */
const BUTTRESSES = [-190, -150, -110, -70, 70, 110, 150, 190] as const;
/** Lights along the crest, every this along X. */
const LAMP_STEP = 32;

/**
 * A prism along X from x = -half to half (centred on `x`): its section `section` in the (Z, Y)
 * plane, as (-y, z) points, extruded as a slab turned on its side.
 */
function prismX(
  s: SolidBuilder,
  section: readonly (readonly [y: number, z: number])[],
  [x, half]: readonly [number, number],
  color: Rgb,
): void {
  // Turned by -90° around Z, a slab's (x, y, z) becomes (y, -x, z): its outline (-y, z).
  const outline: OutlinePoint[] = section.map(([y, z]) => [-y, z]);
  s.slab(outline, [x - half, x + half], color, { roll: -Math.PI / 2 });
}

/** The point of the downstream face at height `y`, `out` off the face. */
function onFace(y: number, out: number): readonly [number, number] {
  const run = CREST_Z[0] - FOOT_Z;
  const length = Math.hypot(run, CREST);
  const z = FOOT_Z + (run * y) / CREST;
  return [y + (out * run) / length, z - (out * CREST) / length];
}

/** Foam or spray, alternating along the spillway. */
const splash = (x: number): Rgb => (Math.round(x / 24) % 2 === 0 ? C.foam : C.spray);

/** White water pouring from a gate down the face at `x`: foam above, spray lower (4 triangles). */
function spillway(s: SolidBuilder, x: number): void {
  const bands: readonly (readonly [number, number, Rgb])[] = [
    [CREST - 2, CREST * 0.45, C.foam],
    [CREST * 0.45, 0, C.spray],
  ];
  const [x0, x1] = [x - GATE_W / 2 + 1, x + GATE_W / 2 - 1];
  for (const [top, bottom, color] of bands) {
    const [yt, zt] = onFace(top, 0.4);
    const [yb, zb] = onFace(bottom, 0.4);
    s.face(
      [
        [x0, yb, zb],
        [x0, yt, zt],
        [x1, yt, zt],
        [x1, yb, zb],
      ],
      color,
    );
  }
  s.lathe(
    [
      [3.2, 0],
      [3.5, 2.2],
      [0, 5],
    ],
    5,
    splash(x),
    { at: [x, 0, FOOT_Z - 0.8] },
    false,
  );
}

/** The spillway's piers and gates at the crest, with the gantry crane over them. */
function gates(s: SolidBuilder): void {
  const piers = [...GATES.map((x) => x - GATE_W / 2), (GATES.at(-1) ?? 0) + GATE_W / 2];
  for (const x of piers) s.box([3, 7, 13], C.damConcrete, { at: [x, CREST - 4, 9.5] });
  for (const x of GATES) {
    s.box([GATE_W - 3, 4, 1], C.rustDark, { at: [x, CREST - 3, CREST_Z[0] + 1] });
  }
  s.box([2 * GATES.length * GATE_W * 0.55, 1.4, 2], C.signalOrange, { at: [0, CREST + 4, 12] });
}

/**
 * The giant dam: a concrete wall with a sloping downstream face (towards -Z), a road on its
 * crest, buttresses, a spillway of five gates in the middle with white water pouring down the
 * face into a churn of foam, a control tower, rocks at both ends, and lamps along the crest.
 */
export function buildGiantDam(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  const body = [
    [0, FOOT_Z],
    [CREST, CREST_Z[0]],
    [CREST, CREST_Z[1]],
    [0, CREST_Z[1] + 2],
  ] as const;
  prismX(s, body, [0, DAM_HALF], C.damConcrete);
  s.box([2 * DAM_HALF, 0.4, 9], C.concreteDark, { at: [0, CREST, 10] });
  for (const x of BUTTRESSES) {
    prismX(s, [[0, FOOT_Z - 3], onFace(CREST - 3, 0), [0, FOOT_Z + 4]], [x, 2], C.concrete);
  }
  gates(s);
  GATES.forEach((x) => {
    spillway(s, x);
  });
  s.box([GATES.length * GATE_W, 0.3, 4.4], C.spray, { at: [0, 0, FOOT_Z - 1.8] }, C.foam);
  s.box([10, 7, 8], C.concrete, { at: [-90, CREST, 10] });
  hipRoof(s, 9, [CREST + 7, 2.4], C.metalDark, { at: [-90, 0, 10] });
  for (const x of [-DAM_HALF - 1, DAM_HALF + 1]) {
    s.lathe(
      [
        [8, 0],
        [6.5, 24],
        [2.5, 36],
      ],
      5,
      C.mossStone,
      { at: [x, 0, 4], yaw: x },
    );
  }
  pane(l, [8, 1.6], [-90, CREST + 3.6, 5.94], L.window);
  l.box([0.8, 0.8, 0.8], L.red, { at: [-90, CREST + 9.4, 10] });
  for (let x = -DAM_HALF + 10; x < DAM_HALF; x += LAMP_STEP) {
    l.box([0.8, 1.6, 0.8], L.yellow, { at: [x, CREST + 0.4, CREST_Z[0] + 0.8] });
  }
  return { structure: s.geometry, lights: l.geometry };
}
