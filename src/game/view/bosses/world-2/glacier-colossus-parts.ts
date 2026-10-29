import type { Muzzle } from '../../../../core/entities/muzzle';
import type { OutlinePoint } from '../../../../render/geometry/outline';
import { mirror } from '../../../config/bosses/boss-kit';
import {
  COLOSSUS_CELLS,
  COLOSSUS_CUTTER_LASER,
  COLOSSUS_ORE_GUNS,
} from '../../../config/bosses/world-2/glacier-colossus';
import { BOSS_LOOK } from '../../../config/boss-look';
import type { EnemyParts } from '../../enemies/enemy-mesh';
import { POD_SECTION, sideStripe } from '../../enemies/enemy-shapes';
import { bossPoint } from '../boss-model';
import { organ, ribs } from '../../../../render/geometry/organic';
import { vent } from '../mini-boss-greebles';
import { gland, ICE_FLESH } from './w2-organic';
import { cog, GEAR } from '../mini-boss-mechanism';
import { H, neonBand, offset, scaled, WHITE } from '../mini-boss-shapes';
import { barrelTo, icicles, PACKED, snowCap } from './avalanche-frost';

// P08-R10, 2-4: the Glacier Colossus's parts. Logical pixels, nose +Z, Y up (towards the
// camera); each part is drawn around its centre `at` (model space), the left ones at +X.
type Vec3 = [number, number, number];

/** The Glacier Colossus's red-orange neon (P08-R10). */
export const COLOSSUS_NEON = BOSS_LOOK.neon['glacier-colossus'] ?? [1, 0.35, 0.08];

/** An octagon of radius 1, flat side to the front. */
const OCTAGON = Array.from({ length: 8 }, (_, k): OutlinePoint => {
  const a = (2 * Math.PI * (k + 0.5)) / 8;
  return [Math.sin(a), Math.cos(a)];
});
/** A cutter's pod along Z around its centre (loft stations: z, half width, bottom, top). */
const CUTTER_POD = [
  [-20, 5, -3, 6],
  [-12, 9, -5, 10],
  [12, 9, -5, 10],
  [24, 6, -2, 8],
] as const;
/** The heat sink's base around its centre, and the height of its fins. */
const SINK_BASE = [
  [-17, -12],
  [17, -12],
  [15, 13],
  [8, 17],
  [-8, 17],
  [-15, 13],
] as const;
const FIN_HEIGHT = 9;

/** Which of two mirrored muzzle lists belongs to the part drawn at `at` (left at +X). */
const sided = (at: Vec3, left: readonly Muzzle[]): readonly Muzzle[] =>
  at[0] > 0 ? left : mirror(left);

/**
 * The mount a cutter turns on (phase 8 review: the cutter, {@link cutter}, is its turret and
 * aims its laser): a drum under its pod, ringed with neon.
 */
export function cutterMount({ flesh, neon }: EnemyParts, at: Vec3): void {
  // P16-R06: a shoulder of muscle the cutter limb turns on.
  flesh.cylinder(8, 3, 7, ICE_FLESH.purple, { at: offset(at, 0, -7.5, 0) }, 7);
  neon.ring(8.3, 0.6, 8, COLOSSUS_NEON, { at: offset(at, 0, -5, 0) });
}

/**
 * A cutter laser (P08-R10), turning on its mount (its turret): a long pod out on the beam, a red-orange stripe along its sides,
 * its emitter at the front, a saw disc at its flank, frost on its back.
 */
export function cutter(p: EnemyParts, at: Vec3): void {
  const { hull, flesh, neon } = p;
  const s = Math.sign(at[0]);
  // P16-R06: a limb of flesh, an armour plate on its back, the laser and saw grafted on.
  flesh.loft(
    POD_SECTION,
    CUTTER_POD,
    ICE_FLESH.sinew,
    { at },
    { paint: (side) => (side === 2 ? ICE_FLESH.teal : undefined) },
  );
  for (const side of [1, 3]) {
    const stripe = sideStripe(POD_SECTION, side, [0.3, 0.7]);
    neon.loft(stripe, CUTTER_POD.slice(1, 3), COLOSSUS_NEON, { at }, { open: true });
  }
  const [tip] = sided(at, COLOSSUS_CUTTER_LASER);
  if (tip) barrelTo(p, tip, [2.8, 9], 'laser');
  neon.ring(3.6, 0.8, 6, COLOSSUS_NEON, {
    at: offset(bossPoint(...(tip ?? [0, 0, 0])), 0, 0, -6),
    pitch: Math.PI / 2,
  });
  cog(hull, offset(at, s * 9.5, 2, 6), 6, 10);
  snowCap(
    flesh,
    [
      [-3.5, -16],
      [3.5, -14],
      [4, 6],
      [-3, 9],
    ].map(([x, z]): OutlinePoint => [at[0] + (x ?? 0), at[2] + (z ?? 0)]),
    at[1] + 9.6,
    0.8,
  );
  icicles(flesh, [offset(at, 5, -2.5, -8), offset(at, -5, -2.5, 0), offset(at, 5, -2.5, 10)], 4);
}

/**
 * An ore cannon (P08-R10): an armoured octagonal barbette, its housing with two fat barrels
 * that fire fans of big shells, a red-orange ring round its foot, snow on its roof.
 */
export function oreCannon(p: EnemyParts, at: Vec3): void {
  const { hull, flesh, neon } = p;
  // P16-R06: an armoured growth, a swollen organ under a metal casemate.
  organ(flesh, 13, 8, ICE_FLESH.purple, { at: offset(at, 0, 2, 0) }, 0.45);
  hull.bevelSlab(scaled(OCTAGON, 9), [12, 13.5, 15], [0, 1.2], H.base, { at }, H.panel);
  neonBand(neon, scaled(OCTAGON, 13), [6.5, 8.5], [1.02, 1.02], COLOSSUS_NEON, { at });
  hull.box([16, 6, 14], H.panel, { at: offset(at, 0, 9, 4) }, H.base);
  for (const tip of sided(at, COLOSSUS_ORE_GUNS)) {
    barrelTo(p, tip, [2.6, 12]);
    const [x, y, z] = bossPoint(...tip);
    hull.cylinder(3.4, 3, 6, GEAR, { at: [x, y, z - 13], pitch: Math.PI / 2 });
  }
  snowCap(
    flesh,
    [
      [-6, -2],
      [5, -4],
      [7, 6],
      [-5, 8],
    ].map(([x, z]): OutlinePoint => [at[0] + (x ?? 0), at[2] + (z ?? 0)]),
    15,
    1,
  );
  gland(p, offset(at, 0, 9, -11), 1.6, COLOSSUS_NEON);
}

/**
 * The heat sink (P08-R10, no weapon): a radiator block at the bow, its fins glowing red-orange
 * between them; the ice around it has melted, the frost only on its outer rims.
 */
export function heatSink(p: EnemyParts, at: Vec3): void {
  const { hull, flesh, neon, charge } = p;
  // P16-R06: a gill organ, its fleshy lamellae glowing between them.
  flesh.bevelSlab(SINK_BASE, [8, 10, 12], [0, 1.2], ICE_FLESH.crimson, { at }, ICE_FLESH.purple);
  for (let i = 0; i < 6; i++) {
    const z = -9 + i * 4.4;
    flesh.box(
      [26 - Math.abs(i - 2.5) * 2, FIN_HEIGHT, 1.4],
      ICE_FLESH.membrane,
      { at: offset(at, 0, 12, z) },
      ICE_FLESH.sinew,
    );
    if (i < 5)
      neon.box([22 - Math.abs(i - 2) * 2, FIN_HEIGHT - 2, 1.6], COLOSSUS_NEON, {
        at: offset(at, 0, 12, z + 2.2),
      });
  }
  charge.box([6, 0.6, 20], WHITE, { at: offset(at, 0, 12 + FIN_HEIGHT, 2) });
  for (const s of [-1, 1]) {
    hull.box([3, FIN_HEIGHT + 2, 26], H.dark, { at: offset(at, s * 14.5, 12, 2) }, H.panel);
  }
  icicles(
    flesh,
    [offset(at, -15, 8, 14), offset(at, 15, 8, 14), offset(at, -12, 8, 17), offset(at, 12, 8, 17)],
    4,
  );
}

/**
 * The missile pod (P08-R10): an armoured box on the stern, four missile tips standing in their
 * tubes (they light up as a salvo charges), vents and frost on its back.
 */
export function missilePod(p: EnemyParts, at: Vec3): void {
  const { hull, flesh, charge, muzzle } = p;
  const box: OutlinePoint[] = [
    [-12, -11],
    [12, -11],
    [13, 8],
    [9, 12],
    [-9, 12],
    [-13, 8],
  ];
  // P16-R06: a brood sac on the stern, four metal tubes grafted in it, missiles growing inside.
  flesh.bevelSlab(box, [15, 17, 22], [0, 3], ICE_FLESH.membrane, { at }, ICE_FLESH.purple);
  ribs(
    flesh,
    [at[2] - 6, at[2] + 6],
    { halfWidth: 13, y: 16, height: 6, thickness: 0.8 },
    ICE_FLESH.bone,
    { at: [at[0], 0, 0] },
  );
  for (const cell of COLOSSUS_CELLS) {
    const tip = bossPoint(...cell);
    hull.ring(2.6, 1, 6, H.dark, { at: offset(tip, 0, -2.8, 0) });
    charge.cylinder(1.9, 2.6, 6, WHITE, { at: offset(tip, 0, -2.6, 0) }, 0);
    muzzle(tip, 'missile');
  }
  vent(hull, offset(at, 0, 21.8, -8.5), [10, 3], 3);
  snowCap(
    flesh,
    [
      [-12, 4],
      [-6, 2],
      [-5, 11],
      [-9, 12],
    ].map(([x, z]): OutlinePoint => [at[0] + (x ?? 0), at[2] + (z ?? 0)]),
    22,
    0.8,
    PACKED,
  );
}
