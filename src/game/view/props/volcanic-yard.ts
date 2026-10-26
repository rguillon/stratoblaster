import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { gableRoof, strut } from './jungle-parts';
import { PLUME, plume } from './volcanic-parts';

// P10-R08: the rail yards between the foundries of 4-4: gantry cranes carrying ladles of molten
// metal, rail track laid piece by piece along a line, ore wagons running to and fro on it, and
// slag heaps still glowing. Sizes in world units, standing on Y = 0; the front faces -Z.

/** Half the span of the gantry crane between its legs (along X), and its beam's height. */
const SPAN = 10;
const BEAM = 12;

/**
 * A gantry crane: two A-shaped legs of dark iron on rails, a long rust-red beam between them
 * with a cabin and a trolley, a ladle of molten metal hanging from its hook, orange neon along
 * the beam and red lights at its ends.
 */
export function buildGantryCrane(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  for (const x of [-SPAN, SPAN]) {
    s.box([1.2, 0.5, 7], C.ironDark, { at: [x, 0, 0] });
    for (const z of [-3, 3]) strut(s, [x, 0.5, z], [x, BEAM, 0], [0.45, 0.35], C.ironDark, 4);
  }
  s.box([2 * SPAN + 1.6, 1.6, 1.8], C.rustRed, { at: [0, BEAM, 0] }, C.rustDark);
  s.box([2.6, 1.4, 3], C.ironDark, { at: [-3, BEAM + 1.6, 0] });
  s.box([2.2, 2, 2.2], C.iron, { at: [SPAN - 2.6, BEAM - 2, 0] });
  strut(s, [-3, BEAM, 0], [-3, 6.2, 0], [0.08, 0.08], C.metalDark);
  // The ladle: a tapered rusty pot, its molten top glowing.
  s.cylinder(1.3, 2.4, 6, C.rustDark, { at: [-3, 3.6, 0] }, 1.7);
  l.lathe(
    [
      [1.65, 5.9],
      [0, 6],
    ],
    6,
    L.molten,
    { at: [-3, 0, 0] },
    false,
  );
  l.box([2 * SPAN, 0.3, 0.2], L.orange, { at: [0, BEAM + 0.6, -0.92] });
  for (const x of [-SPAN - 0.6, SPAN + 0.6])
    l.box([0.4, 0.4, 0.4], L.red, { at: [x, BEAM + 1.6, 0] });
  return { structure: s.geometry, lights: l.geometry };
}

/** Length of a rail track piece along X: pieces are laid end to end every 15. */
const TRACK_LENGTH = 15;
/** Half the gauge: the rails run at z = ±0.85. */
const GAUGE = 0.85;
/** Heights of the ballast bed's top, the sleepers' top and the rails' top. */
const BALLAST = 0.1;
const SLEEPER = 0.25;
const RAIL = 0.4;

/**
 * A piece of rail track, exactly 15 long along X (x = -7.5 to 7.5): two iron rails on five
 * sleepers on a low bed of ash-grey ballast, and a mast beside it carrying the overhead line's
 * arm and a signal light.
 */
export function buildRailLine(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  s.box([TRACK_LENGTH, BALLAST, 3.6], C.ashDark);
  for (const x of [-6, -3, 0, 3, 6]) {
    s.box([0.7, SLEEPER - BALLAST, 2.8], C.charred, { at: [x, BALLAST, 0] });
  }
  for (const z of [-GAUGE, GAUGE]) {
    s.box([TRACK_LENGTH, RAIL - SLEEPER, 0.2], C.iron, { at: [0, SLEEPER, z] });
  }
  s.box([0.35, 4.6, 0.35], C.ironDark, { at: [0, 0, 2.6] });
  s.box([0.25, 0.25, 3], C.ironDark, { at: [0, 4.3, 1.2] });
  l.box([0.35, 0.35, 0.35], L.red, { at: [0, 4.6, 2.6] });
  return { structure: s.geometry, lights: l.geometry };
}

/** The wagon's wheels: x along the track, on the rails at z = ±GAUGE. */
const WHEELS = [-2.6, 2.6] as const;
const WHEEL_RADIUS = 0.55;

/**
 * An ore wagon, running along X on the rail track (8 long): a rusty hopper heaped with black ore
 * on a dark chassis, four wheels on the rails, and orange marker lights at both ends.
 */
export function buildOreWagon(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  for (const x of WHEELS) {
    for (const z of [-GAUGE, GAUGE]) {
      s.cylinder(WHEEL_RADIUS, 0.3, 6, C.ironDark, {
        // The six-sided wheel rests on one of its flat sides, on the rail (y = 0).
        at: [x, WHEEL_RADIUS * Math.sin(Math.PI / 3), z - 0.15],
        pitch: Math.PI / 2,
      });
    }
    s.box([1.8, 0.4, 2], C.ironDark, { at: [x, 0.7, 0] });
  }
  s.box([8, 0.4, 2.4], C.iron, { at: [0, 1.1, 0] });
  s.box([7.2, 1.8, 2.6], C.rustRed, { at: [0, 1.5, 0] }, C.rustDark);
  gableRoof(s, { size: [7.4, 2.8], y: 3.3, rise: 0.8 }, C.ore, C.ore);
  for (const x of [-4.05, 4.05]) l.box([0.1, 0.3, 0.3], L.orange, { at: [x, 1.15, 0] });
  return { structure: s.geometry, lights: l.geometry };
}

/** The slag heap's mound: radius at each height. */
const MOUND = [
  [9, 0],
  [7, 3],
  [3.5, 6],
  [1.5, 6.6],
] as const;
/** The ridges where fresh slag was poured, still glowing: turn of the mound's corner. */
const POURS = [0, (4 * Math.PI) / 7] as const;

/**
 * A slag heap: a broad mound of dark slag, two streaks of fresh slag still glowing down its
 * ridges into a glowing puddle at its foot, smoke rising from its top.
 */
export function buildSlagHeap(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  s.lathe(MOUND, 7, C.slag);
  for (const a of POURS) {
    l.face(
      [
        [3.6, 6.05, -0.4],
        [3.6, 6.05, 0.4],
        [7.2, 3.05, 0.8],
        [7.2, 3.05, -0.8],
      ],
      L.lava,
      { yaw: -a },
    );
    l.face(
      [
        [7.2, 3.05, -0.8],
        [7.2, 3.05, 0.8],
        [8.85, 0.05, 1.1],
        [8.85, 0.05, -1.1],
      ],
      L.slagGlow,
      { yaw: -a },
    );
  }
  return {
    structure: s.geometry,
    lights: l.geometry,
    plumes: [plume(PLUME.smoke, [0, 6.6, 0], 0.6)],
  };
}
