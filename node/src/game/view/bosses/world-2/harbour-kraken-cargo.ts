import type { EnemyParts } from '../../enemies/enemy-mesh';
import { openHatch } from '../final-boss-shapes';
import { organ } from '../../../../render/geometry/organic';
import { rect } from '../mini-boss-greebles';
import { H, offset } from '../mini-boss-shapes';
import { crystals, gland, ICE_FLESH } from './w2-organic';
import { RIME, snowCap } from './fjord-lynx-frost';
import { beam, DECK_Y, ORANGE_NEON } from './harbour-kraken-cranes';

// P08-R10, 2-2: the Harbour Kraken's cargo: the container bay at its stern (a part, launching
// Gnats) and the hatch covers along its deck. Logical pixels, nose +Z, Y up (towards the camera).
type Rgb = readonly [number, number, number];
type Vec3 = [number, number, number];

/** The eggs' flesh shades (P16-R06), where the container paints were. */
const PAINT: readonly Rgb[] = [
  ICE_FLESH.membrane,
  ICE_FLESH.purple,
  ICE_FLESH.teal,
  ICE_FLESH.sinew,
];
/** A container's size: across, high, along. */
const BOX: Vec3 = [7, 5, 13];
/** The stacks either side of the launch hatch: x, z, and how many high. */
const STACKS = [
  [-14.5, -6, 2],
  [-7.5, -6, 1],
  [-14.5, 8, 1],
  [7.5, 7, 2],
  [14.5, 7, 1],
  [14.5, -7, 2],
] as const;

/** A container at `at` (its base), painted `paint`, its doors' end hatched, snow on its roof. */
function container({ flesh, vein }: EnemyParts, at: Vec3, paint: Rgb): void {
  // P16-R06: an egg lying in the brood sac where a container was, a gland lit in it.
  organ(flesh, BOX[0] / 2, 6, paint, { at, pitch: Math.PI / 2 }, BOX[2] / BOX[0]);
  organ(vein, 0.9, 4, ORANGE_NEON, { at: offset(at, 0, BOX[1] * 0.8, 0) }, 0.6);
}

/**
 * The container bay (P08-R10): stacks of frosted containers either side of an open launch
 * hatch, an orange-lit gantry over it; its Gnats leave through the hatch.
 */
export function containerBay(p: EnemyParts, at: Vec3): void {
  const { hull, neon } = p;
  // P16-R06: the brood sac, a cradle of membrane full of eggs, its mouth held open by metal.
  p.flesh.bevelSlab(
    rect(38, 32),
    [DECK_Y - 1, DECK_Y, DECK_Y + 1.5],
    [0, 0.8],
    ICE_FLESH.membrane,
    { at },
    ICE_FLESH.purple,
  );
  const floor = offset(at, 0, DECK_Y + 1.5, 0);
  STACKS.forEach(([x, z, high], i) => {
    for (let k = 0; k < high; k++) {
      container(p, offset(floor, x, k * BOX[1], z), PAINT[(i + k) % PAINT.length] ?? H.base);
    }
  });
  openHatch(p, offset(floor, 0, 0.1, 0), [8, 24]);
  for (const z of [-11, 11]) {
    hull.box([1.2, 12, 1.2], H.panel, { at: offset(floor, -5.5, 0, z) });
    hull.box([1.2, 12, 1.2], H.panel, { at: offset(floor, 5.5, 0, z) });
    beam(hull, offset(floor, -6, 12, z), offset(floor, 6, 12, z), [1.6, 1.4], [H.base, RIME]);
    neon.box([9, 0.4, 0.6], ORANGE_NEON, { at: offset(floor, 0, 13.45, z) });
  }
  crystals(p.flesh, offset(floor, -17, 0, -14), 3);
}

/** The hatch covers on the deck between the cranes: frosted lids with seams and a vent. */
export function hatchCovers(p: EnemyParts): void {
  const { hull, flesh } = p;
  for (const z of [-20, 40]) {
    // Armour plates grafted on the shell.
    hull.bevelSlab(
      rect(26, 12),
      [DECK_Y - 0.5, DECK_Y, DECK_Y + 2],
      [0, 1],
      H.panel,
      {
        at: [0, 0, z],
      },
      RIME,
    );
    snowCap(flesh, rect(18, 7), DECK_Y + 2, { at: [z > 20 ? 2 : -3, 0, z] });
  }
  gland(p, [-10, DECK_Y + 2.4, 40], 1.4, ORANGE_NEON);
}
