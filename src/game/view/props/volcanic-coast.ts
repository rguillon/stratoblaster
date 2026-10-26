import { SolidBuilder } from '../../../render/geometry/solids';
import type { PropGeometry } from '../../../render/scenery/scenery-look';
import { PROP_COLORS as C, PROP_LIGHTS as L } from '../../config/prop-look';
import { corners, pane, posts } from './polar-parts';
import { gableRoof, strut } from './jungle-parts';
import { PLUME, plume, stain } from './volcanic-parts';

// P10-R08: the black-sand coasts of 4-1: fishing huts of soot-darkened planks, geothermal wells
// steaming on the islands, and the small harbour on the final coast (a basalt and iron pier, a
// rust-red crane). Sizes in world units, standing on Y = 0; the front faces -Z.

/** Outline (x, z) of the upturned boat on the beach. */
const BOAT = [
  [-2.6, 0],
  [-1.6, -0.9],
  [1.8, -0.9],
  [2.8, 0],
  [1.8, 0.9],
  [-1.6, 0.9],
] as const;

/**
 * A fishing hut on the black sand: a low hut of dark planks on short stilts under a rusty
 * corrugated roof, a rack with a net hung out to dry, an upturned boat, a lit window and a lamp.
 */
export function buildFishingHut(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  posts(s, corners(2.6, 2), 0.9, C.charred, 0.4);
  s.box([6, 2.6, 4.6], C.woodDark, { at: [0, 0.9, 0] });
  gableRoof(s, { size: [7, 5.8], y: 3.5, rise: 1.6 }, C.rustDark, C.woodDark);
  s.box([0.6, 1.6, 0.6], C.basaltLight, { at: [2, 4.2, 1.2] });
  // The net rack at the side: two poles, a bar, the dark net hung from it.
  posts(
    s,
    [
      [-4.6, -2.4],
      [-4.6, 2.4],
    ],
    3,
    C.charred,
    0.3,
  );
  s.box([0.25, 0.25, 5], C.charred, { at: [-4.6, 3, 0] });
  s.face(
    [
      [-4.65, 0.8, 2.3],
      [-4.65, 3, 2.3],
      [-4.65, 3, -2.3],
      [-4.65, 0.8, -2.3],
    ],
    C.metalDark,
  );
  s.slab(BOAT, [0, 0.9], C.rustRed, { at: [1, 0, -4.4], yaw: 0.2 }, C.basaltLight);
  s.box([0.2, 3.4, 0.2], C.metalDark, { at: [3.6, 0, -2.8] });
  pane(l, [1.4, 1], [-1, 2, -2.36], L.window);
  l.box([0.5, 0.5, 0.5], L.yellow, { at: [3.6, 3.4, -2.8] });
  return { structure: s.geometry, lights: l.geometry };
}

/**
 * A geothermal well: a wellhead of stacked valves on a concrete pad, a squat silencer drum
 * sending up a column of steam, a pipe to a small control hut with a lit window, rust stains.
 */
export function buildGeothermalWell(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  stain(s, [2, -2], 3.4, C.rustRed, 6);
  s.box([7, 0.5, 6], C.concreteDark, { at: [-1.5, 0, 0.5] });
  // The wellhead: a stack of valves with hand wheels.
  s.cylinder(0.7, 3.4, 6, C.metal, { at: [-3, 0.5, 0] });
  s.box([2.2, 0.5, 0.5], C.rustRed, { at: [-3, 1.6, 0] });
  s.box([0.5, 0.5, 2.2], C.rustRed, { at: [-3, 2.8, 0] });
  // The silencer: a wide drum, steam rising out of its open top.
  s.cylinder(2.4, 5.6, 8, C.ash, { at: [3.4, 0, 1.6] }, 2.1);
  s.ring(2.15, 0.6, 8, C.soot, { at: [3.4, 5, 1.6] });
  strut(s, [-2.3, 2.2, 0], [1.4, 2.2, 1.2], [0.4, 0.4], C.metal, 5);
  s.box([3, 2.6, 2.6], C.ironDark, { at: [-1.8, 0.5, 3.6] }, C.ash);
  pane(l, [1.2, 0.8], [-1.8, 1.8, 2.29], L.window);
  l.box([0.4, 0.4, 0.4], L.orange, { at: [-3, 3.9, 0] });
  return {
    structure: s.geometry,
    lights: l.geometry,
    plumes: [plume(PLUME.steam, [3.4, 5.6, 1.6])],
  };
}

/** Bollards along the pier's front edge (x). */
const BOLLARDS = [-9, -4, 1, 6] as const;
/** Containers on the quay: (x, z), yaw, two stacked or one, colour. */
const CONTAINERS = [
  [-6.5, 3.6, 0, true, C.rustRed],
  [-1.5, 3.8, 0.05, false, C.ironDark],
  [3, 4, 0, false, C.containerRed],
] as const;

/**
 * The harbour dock: a long pier of black basalt blocks and an iron deck, bollards on its edge,
 * containers on the quay, an ash-roofed shed with a lit door, and lamp posts.
 */
export function buildHarbourDock(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  s.box([22, 1.6, 6], C.basalt, { at: [0, 0, -3] }, C.iron);
  s.box([22, 1.6, 6], C.basaltLight, { at: [0, 0, 3] }, C.ashDark);
  for (const x of BOLLARDS) s.cylinder(0.4, 0.8, 5, C.soot, { at: [x, 1.6, -5.4] });
  for (const [x, z, yaw, two, color] of CONTAINERS) {
    s.box([4.4, 2.2, 2.2], color, { at: [x, 1.6, z], yaw });
    if (two) s.box([4.4, 2.2, 2.2], C.ironDark, { at: [x, 3.8, z], yaw: yaw + 0.04 });
  }
  s.box([6, 4, 5], C.iron, { at: [8, 1.6, 2.6] });
  gableRoof(s, { size: [6.8, 5.8], y: 5.6, rise: 1.4 }, C.ashLight, C.iron, { at: [8, 0, 2.6] });
  for (const x of [-10, 2]) {
    s.box([0.25, 4.6, 0.25], C.metalDark, { at: [x, 1.6, -1] });
    l.box([0.6, 0.4, 0.6], L.window, { at: [x, 6.2, -1] });
  }
  pane(l, [2.4, 2.4], [8, 1.6, 0.09], L.windowDim);
  return { structure: s.geometry, lights: l.geometry };
}

/**
 * A harbour crane: a rust-red portal on four legs, a turning cabin and a long jib reaching out
 * over the water (-Z), a counterweight behind, a hook hanging, red lights on the jib.
 */
export function buildVolcanicCrane(): PropGeometry {
  const s = new SolidBuilder({ openBottoms: true });
  const l = new SolidBuilder();
  for (const [x, z] of corners(2.6, 2.6)) {
    strut(s, [x, 0, z], [x * 0.6, 7, z * 0.6], [0.4, 0.3], C.rustRed, 4);
  }
  s.box([4.4, 0.8, 4.4], C.ironDark, { at: [0, 7, 0] });
  s.box([3.2, 3, 3.6], C.rustRed, { at: [0, 7.8, 0.8] }, C.ash);
  s.box([2.6, 1.8, 2.4], C.ironDark, { at: [0, 7.8, 3.6] });
  strut(s, [0, 9.6, -0.8], [0, 13.5, -9.6], [0.5, 0.25], C.rustRed, 4);
  strut(s, [0, 12, 0.4], [0, 13.5, -9.6], [0.08, 0.08], C.metalDark);
  strut(s, [0, 13.4, -9.4], [0, 5, -9.4], [0.06, 0.06], C.metalDark);
  s.box([0.8, 0.8, 0.8], C.ironDark, { at: [0, 4.2, -9.4] });
  pane(l, [1.6, 0.9], [0, 9.2, -1.01], L.window);
  // Red lights on the jib, at its tip and half way along.
  for (const t of [1, 0.5])
    l.box([0.4, 0.4, 0.4], L.red, { at: [0, 9.9 + 3.9 * t, -0.8 - 8.8 * t] });
  return { structure: s.geometry, lights: l.geometry };
}
