import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { pane, posts, snowCap } from './polar-parts';

// P08-R07: research outposts of the tundra (radar domes, antennas, wind turbines) and the
// pipeline on stilts of 2-3. Sizes in world units, standing on Y = 0.

/** A white radome, a faceted ball, on an insulated equipment building, with a red light on top. */
export function buildRadarDome(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  s.box([11, 5, 10], C.panel, {}, C.snow);
  s.cylinder(3.2, 2, 8, C.panelDark, { at: [0, 5, 0] });
  s.lathe(
    [
      [3.4, 6.2],
      [5.4, 8.4],
      [6, 11.2],
      [5.2, 14],
      [3, 16],
      [0, 16.8],
    ],
    8,
    C.white,
    {},
    false,
  );
  s.box([3, 2.6, 2.6], C.metalDark, { at: [-3.4, 0, -6.2] }, C.snow);
  pane(l, [7, 0.8], [1.5, 3.2, -5.06], L.cyan);
  pane(l, [1.4, 1.2], [-3.4, 0.6, -7.56], L.window);
  l.box([0.7, 0.7, 0.7], L.red, { at: [0, 16.7, 0] });
  return { structure: s.geometry, lights: l.geometry };
}

/** Heights of the masts of the antenna array, left to right. */
const MASTS = [14, 22, 18, 26, 16] as const;

/** A row of thin lattice masts with crossbars and red lights, next to a snowy equipment shed. */
export function buildAntennaArray(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  MASTS.forEach((h, i) => {
    const x = -8 + i * 4;
    s.cylinder(0.7, h, 4, C.metal, { at: [x, 0, -1], yaw: Math.PI / 4 }, 0.15);
    s.box([0.3, 0.3, 2.8], C.metalDark, { at: [x, h * 0.6, -1] });
    l.box([0.6, 0.6, 0.6], L.red, { at: [x, h - 0.1, -1] });
  });
  s.box([8, 3, 4], C.panelDark, { at: [0, 0, 5] });
  snowCap(s, [8.4, 4.4], [0, 3, 5]);
  s.box([16, 0.4, 0.4], C.metalDark, { at: [0, 3, -1] });
  pane(l, [4, 0.6], [0, 1.8, 2.94], L.cyan);
  return { structure: s.geometry, lights: l.geometry };
}

/** Yaw of the three blades around the hub, radians. */
const BLADES = [0, (2 * Math.PI) / 3, (4 * Math.PI) / 3] as const;

/**
 * A wind turbine: a tall tapering mast on a pad, a nacelle at the top, and three long blades
 * facing the road, one pointing up; a red light on the nacelle.
 */
export function buildWindTurbine(): PropGeometry {
  const s = new SolidBuilder();
  const l = new SolidBuilder();
  s.box([5, 1, 5], C.concrete, {}, C.snow);
  s.cylinder(1, 30, 6, C.white, { at: [0, 1, 0] }, 0.55);
  s.box([1.8, 2, 5], C.white, { at: [0, 30.4, 0.6] }, C.snow);
  const hub: readonly [number, number, number] = [0, 31.4, -2.2];
  s.lathe(
    [
      [0.9, 0],
      [0, 1.4],
    ],
    5,
    C.white,
    { at: hub, pitch: -Math.PI / 2 },
  );
  for (const roll of BLADES) {
    s.box([0.9, 8.2, 0.3], C.white, { at: [0, 31.4, -2.4], roll });
  }
  l.box([0.5, 0.5, 0.5], L.red, { at: [0, 32.4, 2.4] });
  return { structure: s.geometry, lights: l.geometry };
}

/** Length of a pipeline piece along X: pieces are laid end to end every 15 (TUNDRA_PIPELINE). */
const PIPE_LENGTH = 15;
const PIPE_RADIUS = 0.8;
const PIPE_HEIGHT = 2.6;

/**
 * A piece of the pipeline on stilts: an insulated grey-silver pipe exactly 15 long along X, from
 * x = -7.5 to 7.5, about 3 high on two H-shaped stilts, with a joint collar and snow on top.
 */
export function buildPipeline(): PropGeometry {
  const s = new SolidBuilder();
  const half = PIPE_LENGTH / 2;
  s.cylinder(PIPE_RADIUS, PIPE_LENGTH, 6, C.silver, {
    at: [-half, PIPE_HEIGHT, 0],
    roll: -Math.PI / 2,
  });
  s.cylinder(PIPE_RADIUS + 0.15, 0.6, 6, C.frostDark, {
    at: [half - 0.6, PIPE_HEIGHT, 0],
    roll: -Math.PI / 2,
  });
  s.box([PIPE_LENGTH, 0.35, 0.9], C.snowShade, { at: [0, PIPE_HEIGHT + 0.5, 0] }, C.snow);
  for (const x of [-half / 2, half / 2]) {
    const stilts = [
      [x, -0.75],
      [x, 0.75],
    ] as const;
    posts(s, stilts, PIPE_HEIGHT - 0.6, C.metalDark, 0.35);
    s.box([0.4, 0.5, 2.1], C.metalDark, { at: [x, PIPE_HEIGHT - 0.95, 0] });
  }
  return { structure: s.geometry };
}
