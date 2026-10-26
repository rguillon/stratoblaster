import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { pane } from './polar-parts';
import { strut } from './jungle-parts';
import { PLUME, plume, stain } from './volcanic-parts';

// P10-R08: geothermal power on the ash plains of 4-2: the power plants, their cooling towers
// sending up steam, and the insulated pipelines between the wells and the plants. Ash-grey
// concrete, soot and rust, dark iron. Sizes in world units, standing on Y = 0; the front faces -Z.

/** The power plant's separator tanks: (x, z), radius and height. */
const SEPARATORS = [
  [-12, -5, 2, 7],
  [-12, 0.5, 2, 7],
] as const;
/** The power plant's condenser stacks, steaming: (x, z), radius and height. */
const CONDENSERS = [
  [8.5, 5.5, 3, 9],
  [14, 0.5, 2.6, 8],
] as const;

/**
 * A geothermal power plant: a long turbine hall of ash-grey concrete with a sooty roof and a
 * strip of lit windows, two separator tanks, two condenser stacks sending up steam, pipes
 * between them and a rust-stained yard.
 */
export function buildGeothermalPlant(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  stain(s, [0, 0], 13, C.ashDark, 8);
  stain(s, [-11, 6], 4, C.rustRed, 6, 0.08);
  s.box([16, 7, 9], C.ash, { at: [-1, 0, -1] }, C.ironDark);
  s.box([16.4, 1.2, 9.4], C.basalt, { at: [-1, 7, -1] }, C.soot);
  s.box([6, 4, 6], C.concreteDark, { at: [0, 0, 6.5] }, C.ashDark);
  for (const [x, z, r, h] of SEPARATORS) {
    s.cylinder(r, h, 7, C.metal, { at: [x, 0, z] });
    s.lathe(
      [
        [r, h],
        [0, h + 1.4],
      ],
      7,
      C.metal,
      { at: [x, 0, z] },
      false,
    );
  }
  for (const [x, z, r, h] of CONDENSERS) {
    s.cylinder(r, h, 8, C.concrete, { at: [x, 0, z] }, r * 0.85);
    s.ring(r * 0.85, 0.8, 8, C.soot, { at: [x, h - 0.8, z] });
  }
  strut(s, [-10, 5, -2], [-9, 5, -2], [0.6, 0.6], C.metal, 5);
  strut(s, [7, 3, 0], [12, 3, 1], [0.6, 0.6], C.rust, 5);
  strut(s, [5, 4, 4], [7, 4, 5], [0.7, 0.7], C.rust, 5);
  pane(l, [12, 1], [-1, 4.5, -5.56], L.windowDim);
  for (const [x, z] of [
    [-12, -2.25],
    [8.5, 5.5],
  ] as const)
    l.box([0.5, 0.5, 0.5], L.red, { at: [x, 9.4, z] });
  return {
    structure: s.geometry,
    lights: l.geometry,
    plumes: CONDENSERS.map(([x, z, , h]) => plume(PLUME.steam, [x, h, z])),
  };
}

/** The cooling tower's hyperbolic shell: radius at each height. */
const TOWER_SHELL = [
  [8, 0],
  [6.4, 8],
  [5.2, 16],
  [5.6, 22],
] as const;

/**
 * A cooling tower: a hyperbolic shell of ash-grey concrete, blackened by soot near its rim, on
 * a ring of legs (a dark band at its foot), its inside dark, a column of white steam rising, a
 * red light on the rim.
 */
export function buildVolcanicCoolingTower(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  s.ring(8.05, 1.4, 10, C.soot);
  s.lathe(TOWER_SHELL.slice(0, 3), 10, C.ash, {}, false);
  s.lathe(TOWER_SHELL.slice(2), 10, C.ashDark, {}, false);
  // The inside of the rim, seen from above.
  s.lathe(
    [
      [5.6, 22],
      [5, 20],
    ],
    10,
    C.soot,
    {},
    false,
  );
  s.box([3, 2.4, 2], C.concreteDark, { at: [8.4, 0, 0] });
  l.box([0.5, 0.5, 0.5], L.red, { at: [0, 22, -5.6] });
  pane(l, [1, 0.8], [8.4, 1, -1.01], L.window);
  return {
    structure: s.geometry,
    lights: l.geometry,
    plumes: [plume(PLUME.steam, [0, 22, 0], 1.4)],
  };
}

/** Length of a pipeline piece along X: pieces are laid end to end every 15. */
const PIPE_LENGTH = 15;
const PIPE_RADIUS = 1;
const PIPE_HEIGHT = 2.6;

/**
 * A piece of the geothermal pipeline, exactly 15 long along X (x = -7.5 to 7.5): a fat pipe in
 * grey insulation on two low iron saddles, a dark joint collar at its end, a valve wheel with an
 * orange marker light, an ash drift against one saddle.
 */
export function buildVolcanicPipeline(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  const half = PIPE_LENGTH / 2;
  s.cylinder(PIPE_RADIUS, PIPE_LENGTH, 6, C.ashLight, {
    at: [-half, PIPE_HEIGHT, 0],
    roll: -Math.PI / 2,
  });
  s.cylinder(PIPE_RADIUS + 0.2, 0.8, 6, C.ironDark, {
    at: [half - 0.8, PIPE_HEIGHT, 0],
    roll: -Math.PI / 2,
  });
  for (const x of [-half / 2, half / 2]) {
    s.box([0.8, PIPE_HEIGHT - 0.6, 2.4], C.iron, { at: [x, 0, 0] });
  }
  s.box([0.9, 1.2, 0.9], C.rustRed, { at: [0, PIPE_HEIGHT + 0.6, 0] });
  stain(s, [-half / 2 - 1, 0.6], 1.6, C.ashDark, 5);
  l.box([0.4, 0.4, 0.4], L.orange, { at: [0, PIPE_HEIGHT + 1.8, 0] });
  return { structure: s.geometry, lights: l.geometry };
}
