import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';

// P06-R06 (reviewer, 2026-10-26): farms of the green land. Sizes in world units, on Y = 0.

/** A pitched roof over a block `w × d` whose walls are `h` high, the ridge along X. */
function gableRoof(s: SolidBuilder, [w, h, d]: readonly [number, number, number], rise: number) {
  const slope = Math.atan2(rise, d / 2);
  const run = Math.hypot(rise, d / 2) + 0.6;
  s.box([w + 0.8, 0.5, run], C.farmRoof, { at: [0, h + rise / 2, -d / 4], pitch: -slope });
  s.box([w + 0.8, 0.5, run], C.farmRoof, { at: [0, h + rise / 2, d / 4], pitch: slope });
  // The gable ends, wound like the box's side faces at -X and +X.
  const [x0, x1] = [-w / 2, w / 2];
  s.face(
    [
      [x0, h, d / 2],
      [x0, h + rise, 0],
      [x0, h, -d / 2],
    ],
    C.farmWall,
  );
  s.face(
    [
      [x1, h, -d / 2],
      [x1, h + rise, 0],
      [x1, h, d / 2],
    ],
    C.farmWall,
  );
}

/** A long barn under a dark pitched roof, a lower wing, and a cyan neon line along the ridge. */
export function buildFarmhouse(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  s.box([14, 5, 9], C.farmWall);
  gableRoof(s, [14, 5, 9], 3.5);
  s.box([6, 3.5, 6], C.farmWall, { at: [-3, 0, 6.5] }, C.roof);
  l.box([14.6, 0.35, 0.35], L.cyan, { at: [0, 8.6, 0] });
  l.box([3, 2.6, 0.3], L.window, { at: [3, 0.2, -4.6] });
  l.box([1.8, 1.2, 0.3], L.window, { at: [-4, 2, -4.6] });
  return { structure: s.geometry, lights: l.geometry };
}

/** A long glass greenhouse on a low wall, its grow lights glowing pink through the roof. */
export function buildGreenhouse(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  s.box([16, 1, 7], C.concrete);
  s.box([16, 2.5, 7], C.glassGreen, { at: [0, 1, 0] }, C.glassGreen);
  gableRoof(s, [15.2, 3.5, 7], 2);
  for (const x of [-8, 0, 8]) s.box([0.5, 5.5, 7.2], C.metalDark, { at: [x, 0, 0] });
  l.box([15, 0.3, 0.6], L.pink, { at: [0, 3.2, -1.6] });
  l.box([15, 0.3, 0.6], L.pink, { at: [0, 3.2, 1.6] });
  return { structure: s.geometry, lights: l.geometry };
}

/** Three grain silos with domed tops on a concrete pad, an auger tower and a red light. */
export function buildGrainSilos(): PropGeometry {
  const s = new SolidBuilder();
  const l = new SolidBuilder();
  s.box([15, 0.6, 7], C.concrete);
  for (const x of [-5, 0, 5]) {
    s.cylinder(2.3, 11, 8, C.silver, { at: [x, 0.6, 0] });
    s.lathe(
      [
        [2.4, 11.6],
        [1.4, 13],
        [0, 13.6],
      ],
      8,
      C.metal,
      { at: [x, 0, 0] },
    );
  }
  s.box([1.6, 16, 1.6], C.metalDark, { at: [6.5, 0, -3] });
  s.box([12, 0.6, 0.6], C.metalDark, { at: [0.5, 14.5, -3] });
  l.ring(2.35, 0.4, 8, L.yellow, { at: [0, 9, 0] });
  l.box([0.8, 0.8, 0.8], L.red, { at: [6.5, 16, -3] });
  return { structure: s.geometry, lights: l.geometry };
}
